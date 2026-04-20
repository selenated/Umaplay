---
date: 2025-11-27T08:05:00-05:00
topic: Race retry TRY AGAIN bug
status: research_complete
---

# RESEARCH — Race retry TRY AGAIN bug

## Research Question
Why does the race retry flow sometimes fail after pressing `TRY AGAIN` (either by clicking the wrong green `Race` button or by never resolving `View Results`), and how should the transition be hardened so the bot reliably returns to a stable lobby state?

## Summary (≤ 10 bullets)
- `TRY AGAIN` handling is implemented in `RaceFlow` via `_attempt_try_again_retry()`, `_handle_retry_transition()`, and a recursive call back into `lobby()`.
- `_attempt_try_again_retry()` uses `Waiter.click_when` with OCR-based gating and `forbid_texts=("RACE","NEXT")` to click the green `TRY AGAIN` button reliably.
- `_handle_retry_transition()` then uses `Waiter.try_click_once` over green buttons with `texts=("USE","USE ITEM","TRY AGAIN","RACE","YES","OK","CONFIRM")`, trying to clear any interstitial dialogs before the lobby buttons reappear.
- Because `confirm_texts` includes `"RACE"` and is evaluated *before* any `seen("VIEW RESULTS")` / `seen("RACE")` checks, the main lobby `Race` button can be treated as just another confirmation and clicked from inside `_handle_retry_transition()`.
- `Waiter.try_click_once` with `allow_greedy_click=False` relies solely on OCR disambiguation, but it still targets `"RACE"`, so it can confidently click the lobby `Race` when that is the only green button in view.
- `lobby()` resolves `View Results` via `_pick_view_results_button()` (YOLO `button_white` + OCR text scoring) and then uses `ActiveButtonClassifier` to decide if `View Results` is active; if inactive, it follows the green `Race` path instead.
- In the provided log, the *first* retry behaves as intended: `_handle_retry_transition()` clears a confirmation, then detects `View Results`, and `lobby()` sees `View Results active probability: 0.934` and proceeds.
- The *second* retry loops inside `_handle_retry_transition()` performing 3 `try_click` confirmation clicks, times out without ever seeing `View Results` or `Race`, and then `lobby()` is unable to detect a `button_white` `View Results` at all, aborting after ~15s of retries.
- This indicates two primary risks: (1) `_handle_retry_transition()` can over-click green confirmations, including the main `Race` button; and (2) `View Results` detection in `lobby()` is fragile when YOLO `button_white` detections or OCR are missing during the retry flow.
- Robustness likely requires both tightening `_handle_retry_transition()` (e.g., treating lobby `Race` differently than confirmation dialogs) and adding stronger state/visual guards around `View Results` vs `Race` in `lobby()` when coming from a retry.

## Detailed Findings (by area)

### Area: Race retry flow and TRY AGAIN handling
- **Why relevant:** This is the core control flow that runs after a loss, decides to retry, and navigates back to a stable lobby.
- **Files & anchors (path:line_start–line_end):**
  - `core/actions/race.py:173–207` — `_attempt_try_again_retry()`
  - `core/actions/race.py:209–247` — `_handle_retry_transition()`
  - `core/actions/race.py:872–913` — loss detection, retry decision, and recursion into `lobby()`
- **Behavior:**
  - After a race finishes and the trophy/skip loop is done, the flow sleeps 1s and probes for a green `TRY AGAIN`:
    ```python
    loss_indicator_seen = self.waiter.seen(
        classes=("button_green",),
        texts=("TRY AGAIN",),
        tag="race_try_again_probe",
        threshold=0.3,
    )
    ```
  - If the `TRY AGAIN` loss indicator is seen, counters are updated and `should_retry` is computed from `Settings.TRY_AGAIN_ON_FAILED_GOAL`.
  - When `should_retry` is true, `_attempt_try_again_retry()` is called. Otherwise, the flow proceeds to click a green `NEXT` and finish the race day.
  - On a successful `TRY AGAIN` click, `_handle_retry_transition()` is invoked, and **if it returns**, `self.lobby()` is called again to re-handle the lobby as if it were a fresh race.

### Area: `_attempt_try_again_retry()` — TRY AGAIN click
- **Why relevant:** Ensures the bot actually clicks the intended `TRY AGAIN` button and not `RACE`/`NEXT`.
- **Files & anchors:**
  - `core/actions/race.py:173–207`
- **Key details:**
  - Uses `Waiter.click_when` with OCR disambiguation and negative filters:
    ```python
    clicked, det = self.waiter.click_when(
        classes=("button_green",),
        texts=("TRY AGAIN",),
        prefer_bottom=False,
        allow_greedy_click=False,
        timeout_s=0.3,
        forbid_texts=("RACE", "NEXT"),
        tag="race_try_again_try",
        return_object=True,
    )
    ```
  - `allow_greedy_click=False` disables the single-candidate and bottom-most fast paths in `Waiter.click_when`, forcing the use of OCR-based text matching.
  - `forbid_texts=("RACE", "NEXT")` prevents misclicks on a lone `RACE` or `NEXT` green button, even if OCR is slightly noisy.
  - The log in your trace shows this working as intended:
    - `DEBUG waiter.py:202: [waiter] text match (tag=race_try_again_try) score=1.00 target_texts=['try again']`
    - `INFO  race.py:195: [race] TRY AGAIN clicked (y_center=568.1) | counters=...`

### Area: `_handle_retry_transition()` — clearing interstitials and waiting for lobby
- **Why relevant:** This is where the automation bridges from `TRY AGAIN` to the lobby; misbehavior here can start races without visiting `View Results`, or leave the flow in an ambiguous state before reentering `lobby()`.
- **Files & anchors:**
  - `core/actions/race.py:209–247`
- **Implementation:**
  ```python
  logger_uma.debug("[race] Handling retry transition interstitials.")
  confirm_texts = ("USE", "USE ITEM", "TRY AGAIN", "RACE", "YES")
  cleanup_texts = ("OK", "CONFIRM")
  deadline = time.time() + 10.0

  while time.time() < deadline:
      if self.waiter.try_click_once(
          classes=("button_green",),
          texts=confirm_texts + cleanup_texts,
          prefer_bottom=False,
          allow_greedy_click=False,
          forbid_texts=("NEXT",),
          tag="race_try_again_confirm",
      ):
          logger_uma.debug("[race] Clicked retry interstitial confirmation.")
          time.sleep(0.45)
          continue

      if self.waiter.seen(
          classes=("button_white",),
          texts=("VIEW RESULTS",),
          tag="race_retry_view_results_ready",
      ):
          logger_uma.debug("[race] View Results ready after retry.")
          return

      if self.waiter.seen(
          classes=("button_green",),
          texts=("RACE",),
          tag="race_retry_race_ready",
      ):
          logger_uma.debug("[race] Race button ready after retry.")
          return

      time.sleep(0.35)

  logger_uma.warning("[race] Retry transition timed out; continuing anyway.")
  ```
- **Key observations / risks:**
  - `try_click_once` runs at the *top* of the loop; if it clicks anything, the function logs and `continue`s without checking for `View Results` or lobby `RACE` readiness.
  - `confirm_texts` explicitly include `"RACE"` and are used *together* with `cleanup_texts` as positive OCR targets:
    - Any green `button_green` whose OCR text matches `USE`, `USE ITEM`, `TRY AGAIN`, `RACE`, `YES`, `OK`, or `CONFIRM` can be clicked by this block.
  - This is intended for dialogs like "USE ITEM", "RACE?", alarms, or confirmation boxes, but it **does not distinguish** those from the main lobby `Race` button.
  - When the main lobby screen with white `View Results` and green `Race` appears, the green `Race` button matches both:
    - Class: `button_green`
    - Text: `"RACE"` ∈ `confirm_texts`
  - Because `try_click_once` executes before any `seen("VIEW RESULTS")` / `seen("RACE")` checks, it can treat the **lobby `Race`** as just another confirmation and click it as part of "clearing interstitials". This matches your description of it "pressing the first button_green found (Race) instead of View results".
  - The forbids `forbid_texts=("NEXT",)` only block green `NEXT` buttons, not `RACE`, so they do not mitigate this specific issue.

### Area: Waiter APIs and OCR behavior
- **Why relevant:** `_attempt_try_again_retry()` and `_handle_retry_transition()` rely on `Waiter.click_when` and `Waiter.try_click_once` for green-button handling; understanding their cascades is key to explaining the observed logs.
- **Files & anchors:**
  - `core/utils/waiter.py:70–229` — `Waiter.click_when`
  - `core/utils/waiter.py:283–347` — `Waiter.try_click_once`
  - `core/utils/waiter.py:363–392` — `_is_forbidden`
  - `core/utils/waiter.py:393–437` — `_pick_by_text`
- **Key semantics:**
  - `click_when` cascade:
    1. If there is exactly one candidate and `allow_greedy_click=True`, click it immediately (subject to `forbid_texts`).
    2. If multiple and `prefer_bottom=True` and `allow_greedy_click=True`, click the bottom-most non-forbidden candidate.
    3. Else, if `texts` and `ocr` exist, OCR each candidate and pick by fuzzy match against `texts`, excluding any that match `forbid_texts`.
    4. Repeat until timeout.
  - `try_click_once` is a **single-shot** version of this cascade:
    - It also supports `allow_greedy_click`, `prefer_bottom`, `texts`, and `forbid_texts`.
    - With `allow_greedy_click=False` (as used in both `_attempt_try_again_retry()` and `_handle_retry_transition()`), steps (1) and (2) are disabled; only the **OCR disambiguation** path runs when `texts` are provided.
  - `_pick_by_text` normalizes `texts` and OCR strings, uses a mix of exact-word and fuzzy ratio comparison, and only returns a candidate when a score passes `threshold`.
  - In your log, every `try_click_once` during retry transition logged:
    ```
    [waiter] try_click text match score=1.00 target_texts=['use', 'use item', 'try again', 'race', 'yes', 'ok', 'confirm']
    [race] Clicked retry interstitial confirmation.
    ```
    This indicates that OCR is confidently matching at least one of the listed tokens; on some frames, that may well be the main `RACE` button on the lobby screen.

### Area: View Results detection & ActiveButtonClassifier
- **Why relevant:** Determines whether the lobby chooses `View Results` or goes straight to the `Race` button.
- **Files & anchors:**
  - `core/actions/race.py:285–300` — `_pick_view_results_button()`
  - `core/actions/race.py:713–871` — `lobby()`
  - `core/perception/is_button_active.py` — `ActiveButtonClassifier` implementation (referenced, not deeply inspected here)
- **Implementation:**
  - `_pick_view_results_button()`:
    - Collects detections with `self._collect("race_view_btn")`.
    - Filters to YOLO `button_white` detections.
    - For each, OCRs the region and scores against `"VIEW RESULTS"` / `"VIEW RESULT"` using `fuzzy_ratio`.
    - Picks the best-scoring white button above a small minimum score.
  - `lobby()` first tries `_pick_view_results_button()` once; if it returns `None`, it retries with progressive delays `2s, 3s, 5s, 5s` (total ~15s). If still `None`, it aborts with:
    ```
    "View Results button not found after ~15s of retries. Cannot determine lobby state. Aborting race operation."
    ```
  - If a `view_btn` is found, `ActiveButtonClassifier` is used:
    ```python
    clf = ActiveButtonClassifier.load(Settings.IS_BUTTON_ACTIVE_CLF_PATH)
    img, _ = self._collect("race_lobby_active")
    crop = crop_pil(img, view_btn["xyxy"])
    p = float(clf.predict_proba(crop))
    is_view_active = p >= 0.51
    logger_uma.debug("[race] View Results active probability: %.3f", p)
    ```
  - When `is_view_active` is true, `View Results` is clicked twice with delays to clear residual screens.
  - When `is_view_active` is false, the code follows the green `Race` path:
    ```python
    if not self.waiter.click_when(
        classes=("button_green",),
        texts=("RACE",),
        prefer_bottom=True,
        timeout_s=6,
        tag="race_lobby_race_click",
    ):
        # abort if Race not found
    ```
- **Failure modes observed in log:**
  - At 06:58:44, the log shows `View Results active probability: 0.967` — `lobby()` correctly chooses `View Results` after the initial race.
  - At 06:58:57, after the first retry, we see `View Results ready after retry.` and `View Results active probability: 0.934` — again, we follow the `View Results` path.
  - After the second retry, `_handle_retry_transition()` times out without ever logging `View Results ready after retry` or `Race button ready after retry`, then `lobby()` logs multiple `"No view result button found, waiting ..."` and finally aborts with the "View Results button not found" error.
  - This shows that, in this specific trace, the failure mode is **missing `button_white` / `VIEW RESULTS` detection** rather than misclassification by `ActiveButtonClassifier` or an explicit wrong click on `Race` inside `lobby()`.

### Area: Log reconstruction — what happens across the two retries
- **Why relevant:** Ties the implementation to the runtime behavior you observed.
- **Files & anchors:**
  - `core/actions/race.py` — `RaceFlow` internals as above
  - `core/utils/waiter.py` — shared waiter behavior
- **First retry (works as designed):**
  - Loss detected:
    - `INFO  [race] Loss indicator detected (toggle=True) | counters={'loss_indicators': 1, ...}`
  - `TRY AGAIN` clicked via `_attempt_try_again_retry()`:
    - `DEBUG [waiter] text match (tag=race_try_again_try) score=1.00 target_texts=['try again']`
    - `INFO  [race] TRY AGAIN clicked ...`
  - `_handle_retry_transition()`:
    - `DEBUG [race] Handling retry transition interstitials.`
    - `DEBUG [waiter] try_click text match score=1.00 ...`
    - `DEBUG [race] Clicked retry interstitial confirmation.`
    - `DEBUG [race] View Results ready after retry.` (loop exits early)
  - Back in `lobby()`:
    - `_pick_view_results_button()` succeeds.
    - `DEBUG [race] View Results active probability: 0.934`
    - Flow proceeds via `View Results` path.
- **Second retry (fails):**
  - Loss detected again:
    - `INFO  [race] Loss indicator detected (toggle=True) | counters={'loss_indicators': 2, ...}`
  - `TRY AGAIN` clicked again:
    - `DEBUG [waiter] text match (tag=race_try_again_try) score=1.00 ...`
    - `INFO  [race] TRY AGAIN clicked ...`
  - `_handle_retry_transition()` enters a loop:
    - `DEBUG [race] Handling retry transition interstitials.`
    - Then three iterations of:
      - `DEBUG [waiter] try_click text match score=1.00 target_texts=[...]`
      - `DEBUG [race] Clicked retry interstitial confirmation.`
    - Finally:
      - `WARNING [race] Retry transition timed out; continuing anyway.`
  - Back in `lobby()`:
    - `_pick_view_results_button()` repeatedly returns `None`; we see:
      - `WARNING No view result button found, waiting 2s more (attempt 1/4)...`
      - `WARNING No view result button found, waiting 3s more (attempt 2/4)...`
      - `WARNING No view result button found, waiting 5s more (attempt 3/4)...`
      - `WARNING No view result button found, waiting 5s more (attempt 4/4)...`
    - Then:
      - `ERROR View Results button not found after ~15s of retries. Cannot determine lobby state. Aborting race operation.`
- **Interpretation:**
  - The second retry shows `_handle_retry_transition()` continuously finding something it thinks is a "retry interstitial" (`try_click text match score=1.00`), but it never reaches a state where `View Results` or lobby `RACE` is observed via `seen()`.
  - Given that `confirm_texts` contain `RACE`, a plausible hypothesis is that some of those `try_click` matches are **hitting the main `Race` button**, repeatedly restarting or leaving the bot in an unexpected state instead of cleanly returning to a lobby with a detectable white `View Results` button.
  - Even if that is not happening in every failure, the current structure makes it possible and aligns with your description of the bot pressing "the first button_green found (Race)".

## 360° Around Target(s)
- **Target file(s):**
  - `core/actions/race.py` — `RaceFlow` implementation, retry logic, lobby handling.
  - `core/utils/waiter.py` — unified waiter API for detection and clicks.
- **Dependency graph (depth 2):**
  - `core/actions/race.py`
    - Imports and uses:
      - `core.utils.waiter.Waiter` — perception+click orchestration (`click_when`, `try_click_once`, `seen`).
      - `core.perception.is_button_active.ActiveButtonClassifier` — classifies if `View Results` is active.
      - `core.utils.text._normalize_ocr`, `fuzzy_ratio` — text normalization and scoring.
      - `core.utils.yolo_objects.collect`, `find` — YOLO detection helpers.
      - `core.utils.geometry.crop_pil` — image cropping for OCR and classifier.
      - `core.settings.Settings` — feature flags such as `TRY_AGAIN_ON_FAILED_GOAL` and classifier path.
  - `core/utils/waiter.py`
    - Depends on:
      - `core.controllers.base.IController` — click primitives.
      - `core.perception.ocr.interface.OCRInterface` — OCR calls.
      - `core.perception.yolo.interface.IDetector` — YOLO detection.
      - `core.utils.geometry.crop_pil` — ROI cropping.
      - `core.utils.text.fuzzy_contains`, `fuzzy_ratio` — fuzzy text matching.

## Open Questions / Ambiguities
- **How should we treat `RACE` during retry transition?**
  - Today, `_handle_retry_transition()` treats any green `RACE` as a generic confirmation. This likely conflates confirmation dialogs with the main lobby `Race` button.
  - Options:
    - Remove `"RACE"` from `confirm_texts` in `_handle_retry_transition()` so only `USE` / `TRY AGAIN` / `YES` / `OK` / `CONFIRM` are clicked during the transition.
    - Or gate `RACE` clicks in `_handle_retry_transition()` behind an additional condition (e.g., presence of an alarm-clock YOLO class, or absence of `button_white` `View Results`).
- **Ordering of checks inside `_handle_retry_transition()`:**
  - Currently, we always attempt `try_click_once` before probing for `View Results` / lobby `RACE` readiness.
  - Alternative:
    - First check for a stable lobby (`VIEW RESULTS` or main `RACE` via `seen()`), and only if neither is present, fall back to clicking confirmation dialogs.
    - This would avoid accidentally clicking the lobby `Race` button as an interstitial once the lobby is already ready.
- **Expected UI variants after `TRY AGAIN`:**
  - Are there scenarios where, after pressing `TRY AGAIN`, the game *never* shows a white `View Results` button (e.g., immediate re-queue into the next race or different UI skins)?
  - If so, what is the correct behavior for the bot?
    - Always re-click `Race` without viewing results?
    - Or treat such screens as ambiguous and abort?
  - The answer affects whether we should treat absence of `View Results` after retry as a hard failure (current behavior) versus adding a controlled fallback to green `Race` when the state is clearly pre-race.

## Suggested Next Step
- Draft `docs/ai/features/try-again-bug/PLAN.md` with:
  - **Per-file change notes:**
    - `core/actions/race.py`:
      - Refine `_handle_retry_transition()` to avoid treating the main lobby `Race` button as a generic confirmation (e.g., remove `"RACE"` from `confirm_texts`, or reorder checks to prioritize detecting a stable lobby before clicking any more greens).
      - Optionally, add additional logging and/or debug captures (tagged by agent) around retry transitions to capture the actual UI when `try_click` loops occur.
      - Consider strengthening `lobby()`'s fallback when `_pick_view_results_button()` fails repeatedly, possibly by adding a guarded `Race` fallback when certain visual cues (like race badges or lobby tiles) are present.
    - `core/utils/waiter.py`:
      - Evaluate whether `try_click_once` should support a more conservative mode for high-risk flows (e.g., extra OCR checks, or a different threshold for certain keywords like `RACE`).
  - **Testing plan:**
    - Record controlled runs with forced losses and multiple retries, capturing debug screenshots for `race_try_again_confirm`, `race_retry_view_results_ready`, and `race_lobby_*` tags.
    - Validate that, after the changes, the bot:
      - Always clears confirmation dialogs correctly.
      - Never clicks the lobby `Race` button from `_handle_retry_transition()` when `View Results` is intended.
      - Either reliably finds `View Results` or takes a clearly defined fallback path with explicit logging when `View Results` is absent.
