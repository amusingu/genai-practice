# LabLens AI: Laboratory Record-Continuity Platform

LabLens AI turns scattered lab notes and instrument output into one structured, checkable experiment record. It is built for **graduate student researchers** in physical science, engineering, and biomedical labs, who lose hours reconstructing what they ran, on which sample, with which settings, from paper notebooks, phone photos, and instrument PCs.

## Links
- **Working prototype (Replit):** https://lab-lens-ai.replit.app/lablens-streamlit/
- **Repository:** https://github.com/amusingu/genai-practice
- **Demo video:** see [Demo Video](#demo-video) below

**How to try it:** open the prototype link (no login needed). Choose **Sample 1** or **Custom Input**, paste notes, then click **Extract draft record**. Check each field against "Where this came from", fix anything wrong, tick the check box, and click **Confirm record**. Confirmed records appear in the session log and can be downloaded as JSON.

Example custom input: `Nov 3 2026. Sample GaN-117. Ran PECVD SiN deposition, 300C, 40 min. Thickness looked thin on ellipsometer, recheck tomorrow.`

## Prototype status: what is real vs. simulated
| Feature | Status |
|---|---|
| Text input, TXT/CSV file reading | Implemented |
| Field extraction (date, sample ID, equipment, settings, observations, follow-ups, files) | **Simulated AI:** rule-based stand-in (`extractor.py`), not a language model |
| Evidence shown for each value, editable review, confirm/reject, session log, JSON export | Implemented |
| Reading photos of handwritten notes (OCR / vision model) | Planned |
| Saving records between sessions; linking related runs | Planned |

## Milestone documents
- **[Prototype Revision](revision.md):** priority improvements, response to feedback, five test cases, before/after comparison, interpretation, risk response, limitations, next priorities
- **[AI-Use Disclosure (draft)](ai-use-disclosure.md)**
- **Test evidence:** [`tests/run_test_cases.py`](tests/run_test_cases.py) and its raw output in [`tests/test_output.txt`](tests/test_output.txt)
- **Screenshots:** [`docs/screenshots/`](docs/screenshots/)

## Code
| File | Purpose |
|---|---|
| `app.py` | Streamlit interface: input, review, confirm/reject, log |
| `extractor.py` | Rule-based extraction (stand-in for the planned AI model). It never invents values and flags missing or conflicting ones |
| `tests/run_test_cases.py` | Runs the evaluation cases and prints actual results |
| `requirements.txt` | Python dependencies |

In Replit, the app lives in `artifacts/lablens-streamlit/` and is launched by `run.py`, which serves it under `/lablens-streamlit/`.

Run locally: `pip install -r requirements.txt`, then `streamlit run app.py`

## Demo Video
**TODO:** paste the Google Drive viewing link here (shared with ehughes8@nd.edu and ghuang3@nd.edu).

## Previous milestone (First Working Slice)
The first slice showed template records for two prepared samples. Any custom input returned a generic placeholder record. Its three tests and three known limitations are carried forward and addressed in [revision.md](revision.md).

All example data in this repository is synthetic.
