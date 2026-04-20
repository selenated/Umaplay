# Event Dataset Workflow (Supports & Trainees)

This guide documents the reproducible flow for adding fresh events to the catalog. Follow the numbered steps in order—each depends on the previous one.

---

## 0. Prerequisites

- Chrome (or similar) with DevTools
- Local clone of this repo with Python + Node dependencies installed
- (Optional) Scratch editor for validating JSON output

---

## 1. Collect Data from GameTora

Skills (Optional):
1. Open <https://gametora.com/umamusume/skills>
2. Open **Developer Tool** (**Right Click** -> **Inspect** -> **Network** -> **Refresh Page Once** -> **Filter Search for `skills`** -> **Look for file with `skills.*.json` name example `skills.a297e9ee.json`** -> **Right Click** -> **Copy Value** -> **Copy URL**) (<https://gametora.com/data/umamusume/skills.a297e9ee.json>)

Characters and Supports:
1. Open <https://gametora.com/umamusume/characters> or <https://gametora.com/umamusume/supports>
2. Select characters or supports you want to scrape and copy `id` from `url` (<https://gametora.com/umamusume/supports/30034-rice-shower> `30034-rice-shower`) (<https://gametora.com/umamusume/characters/105801-meisho-doto> `105801-meisho-doto`).

> 💡 Tip: keep the page open until you confirm the scrape succeeded—recopying is faster than reselecting everything.

>  Skills are only required if Cygames updates a patch that adds new skills or makes changes to skills.

---

## 2. Run the scraper

From the repo root:
```bash
cd datasets
```

skills (Optional):
```bash
cls && python scrape_skills.py --url-json https://gametora.com/data/umamusume/skills.a297e9ee.json --out in_game/skills.json --debug
```

Supports:
```bash
cls && python scrape_events.py --supports-card "30036-riko-kashimoto,30034-rice-shower" --skills "in_game/skills.json" --status "in_game/status.json" --period "pre_first_anni" --images --img-dir "../web/public/events" --out "supports_events.json" --debug
```

Characters:
```bash
cls && python scrape_events.py --characters-card "105602-matikanefukukitaru,102801-hishi-akebono" --skills "in_game/skills.json" --status "in_game/status.json" --period "pre_first_anni" --images --img-dir "../web/public/events" --out "supports_events.json" --debug
```

- `--characters-card` and `--supports-card` can be used at the same time.
- Replace `--characters-card` and `--supports-card` with a comma-separated list that covers any new supports and characters you expect in the scrape.
- `--skills` path to `json` file to look for skills `id` that is related to events and get its name. `default: in_game/skills.json`
- `--status` path to `json` file to look for status `id` that is related to events and get its name. `default: in_game/status.json`
- `--period` select period to scrape from \*remove to scrape post first anniversary data\* 
- `--images` download card images `default: false`
- `--img-dir` target folder for images `default: images`
- `--clear-images` clear images dir before download new images. `default: false` \*\*warning do not set if `--img-dir` is set to `../web/public/events` this will remove all of the images inside `/web/public/events`\*\*
- `--out` output JSON file. `required`
- `--debug` is optional but recommended while verifying new entities. Remove it once you are confident in the pipeline.

The script emits `supports_events.json`, containing every parsed support/trainee block, their options, and computed default preferences.

---

## 3. Validate and merge results

1. Open `supports_events.json` in your editor.
2. Spot-check each new entry:
   - Seasonal trainee names should retain suffixes like `(Summer)`.
   - `(Original)` variants are automatically normalized (suffix removed).
   - Range outcomes (e.g., energy `-5/-20`) should appear as separate outcomes in an option.
   - Ensure `default_preference` matches expectations.
3. Copy the **new** support/trainee objects(only copy contents inside `[]`) into `datasets/in_game/events.json`. Keep the array sorted/grouped as desired.
4. Run `python -m json.tool datasets/in_game/events.json` (or your formatter of choice) to ensure valid JSON before committing.

---

## 4. Rebuild the catalog

From the project root:

```bash
python build_catalog.py
```

This regenerates the compressed catalog consumed by the runtime and web UI.

---

## 5. Rebuild the web assets

```bash
cd web
npm run build
```

The updated build will include the refreshed catalog for distribution.

---

## 6. Optional clean-up & QA

- Launch the bot or web UI locally to confirm the catalog surfaces the new events correctly.

---

## Reference / Troubleshooting

- Parsed output is temporary in `datasets/supports_events.json`.
- Canonical dataset is `datasets/in_game/events.json`.
- If the scraper fails to parse an entity, rerun with `--debug` and inspect the console output for the relevant block.
- For additional automation helpers (e.g., GPT tools) see the historical notes in previous README revisions.
