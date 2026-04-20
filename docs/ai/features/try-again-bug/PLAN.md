---
status: plan_ready
---

# PLAN

## Objectives
- Ensure that, after pressing `TRY AGAIN`, the bot reliably transitions through any interstitial dialogs and returns to a stable race lobby state.
- Prevent `_handle_retry_transition()` from accidentally clicking the lobby `Race` button when the intended flow is to go through `View Results`.
- Improve robustness of the `View Results` vs `Race` decision in `lobby()` after a retry, while keeping behavior unchanged for normal (non-retry) flows.

## Steps (general; not per-file)

### Step 1 — Harden retry transition interstitial handling
**Goal:** Make `_handle_retry_transition()` safely clear only genuine retry-related dialogs and avoid treating the main lobby `Race` button as a generic confirmation.

**Actions (high level):**
- Narrow the set of green button texts that `_handle_retry_transition()` is allowed to click as “confirmations” (e.g., focus on `USE`, `USE ITEM`, `TRY AGAIN`, `YES`, `OK`, `CONFIRM`).
- Reorder the logic so that, once the lobby is clearly visible (white `View Results` and/or green `Race` in a stable state), the function stops clicking confirmations and returns.
- Add targeted debug logging (and optionally debug captures via existing `Waiter` tags) when:
  - A `try_click_once` confirmation is performed during retry transition.
  - `View Results` or lobby `Race` readiness is detected, to confirm the state sequence.

**Affected files (expected):**
- `core/actions/race.py` (implementation of `_handle_retry_transition()`)
- `core/utils/waiter.py` (only if minor helper changes are needed; try to keep this optional)

**Quick validation:**
- Run a scenario where a race is intentionally lost and retried at least twice.
- Confirm in logs that:
  - `_handle_retry_transition()` stops as soon as `View Results` or lobby `Race` is available and does not keep clicking `Race` as a confirmation.
  - `View Results ready after retry.` appears for successful transitions, or at least a deterministic fallback path is used.

### Step 2 — Strengthen View Results detection and fallback in lobby
**Goal:** Reduce false negatives when detecting `View Results` in `lobby()` after retries and provide a clear, safe fallback when the button is not found.

**Actions (high level):**
- Review `_pick_view_results_button()` behavior in conditions following a retry, focusing on:
  - YOLO `button_white` detections around `View Results`.
  - OCR thresholds and acceptable scores for `VIEW RESULTS` text.
- Consider small robustness tweaks, such as:
  - Allowing slightly lower OCR thresholds when `TRY AGAIN` was just used and the classifier still indicates a likely `button_white` in the expected region.
  - Adding extra logging to capture the number of white buttons and their OCR texts when `_pick_view_results_button()` returns `None` after a retry.
- In `lobby()`, refine the control flow when `_pick_view_results_button()` repeatedly returns `None` after a retry:
  - Option A: Keep the current conservative behavior (abort with clear error) but ensure logs provide enough context to debug missing `button_white` detections.
  - Option B (if the UI pattern is well understood): add a guarded fallback path that clicks green `Race` when certain cues indicate the lobby is ready but `View Results` is absent.

**Affected files (expected):**
- `core/actions/race.py` (implementations of `_pick_view_results_button()` and `lobby()`)

**Quick validation:**
- Simulate or replay sessions where `View Results` is known to appear late or has been flaky.
- Verify that:
  - The bot either reliably identifies and clicks `View Results` within the retry window, or
  - Emits detailed logs (and, if configured, captures) explaining why `View Results` was not found and what fallback it took.

### Step 3 — Telemetry and safety refinements for retries
**Goal:** Improve observability and guardrails around retry behavior so future regressions can be diagnosed quickly.

**Actions (high level):**
- Extend existing race result counters and logs to clearly distinguish between:
  - Normal race completions with and without `TRY AGAIN`.
  - Retries where `_handle_retry_transition()` had to time out vs. those that reached `View Results` or lobby `Race` quickly.
- Consider adding a simple “max consecutive retries” or “max retry transition failures” safeguard to avoid infinite or confusing loops.
- Ensure that when the flow does abort (e.g., no `View Results` found after all retries), the error message clearly states whether we came from a retry and what the last seen state was (e.g., counts of green/white buttons in the last frame).

**Affected files (expected):**
- `core/actions/race.py` (counters, logging around retry decisions and lobby failures)

**Quick validation:**
- Run multiple training runs with forced losses and retries.
- Inspect logs to confirm that retry metrics and failure reasons are easy to interpret and that the bot exits gracefully when something goes wrong.

### Step 4 — Finalization
**Goal:** Stabilize, verify, and close out the change.

**Actions (high level):**
- Run existing automated tests (if any touch race flows) and a small set of manual runs:
  - Normal race win without retries.
  - Single retry path.
  - Double retry path similar to the provided log.
- Verify that non-retry flows (e.g., normal lobby `Race` clicks, daily races, nav flows) are unaffected.
- Clean up any temporary debug logs or experimental tweaks, keeping only the most useful diagnostics.

**Affected files (expected):**
- `core/actions/race.py`
- `core/utils/waiter.py` (if touched)

**Quick validation:**
- No new noisy logs in normal runs.
- TRY AGAIN flows behave deterministically and no longer get stuck in the “View Results button not found” abort pattern for the original repro scenario.

## Test Plan
- **Unit:**
  - If feasible, add focused tests around helper methods (e.g., `_pick_view_results_button()` given synthetic detections, or a small harness around `Waiter._pick_by_text` and `try_click_once` for key text combinations).
- **Integration/E2E:**
  - Record or replay sessions with:
    - A single loss triggering one `TRY AGAIN`.
    - Back-to-back losses triggering two or more `TRY AGAIN` attempts.
  - Confirm the sequence: `TRY AGAIN` → interstitials cleared → `View Results` (or well-defined fallback) → stable lobby.
- **UX/Visual:**
  - Manually inspect debug screenshots (if enabled) around tags like `race_try_again_confirm`, `race_retry_view_results_ready`, and `race_view_btn` to ensure we are clicking the correct UI elements.

## Verification Checklist
- [ ] Lint and tests pass locally.
- [ ] TRY AGAIN flows (single and multiple retries) complete successfully without misclicking the lobby `Race` instead of `View Results`.
- [ ] Normal race flows without retries remain unchanged.
- [ ] Logs remain clear and concise; retry-related warnings/errors are actionable.

## Rollback / Mitigation
- Revert the changes to `core/actions/race.py` (and `core/utils/waiter.py` if modified) to restore the previous behavior if a regression is detected.
- As a runtime safeguard, temporarily disable `TRY_AGAIN_ON_FAILED_GOAL` in settings so losses do not trigger automatic retries until the issue is fully resolved.

## Open Questions (if any)
- Are there race/result UI variants where `View Results` is intentionally absent after `TRY AGAIN`? If so, what is the desired behavior (auto `Race`, or abort)?
- Should we add an explicit feature flag controlling whether the bot is allowed to click green `Race` during retry transitions, or keep that purely controlled by code logic?
