# AI-Use Disclosure (Draft): LabLens AI

> **Note to self (delete before submitting):** This draft was prepared with Claude's help. Before submitting, rewrite it in your own words, check that every statement matches what you actually did, and fill in the TODO items. The assignment asks for your own account.

## Tools used
- **Gemini:** ideation and the system outline during Problem Framing (recorded in that milestone).
- **Replit (and its AI agent, if used):** hosting the Streamlit prototype. **TODO:** say whether Replit's AI agent generated the First Working Slice code.
- **Claude (Anthropic), Nov 19, 2026:** helped with this revision milestone (details below).

## Development assistance
- **Problem framing (earlier milestone):** Gemini helped outline the architecture of a multimodal app that takes note images and instrument text.
- **This revision:** Claude read my assignment brief, feedback, Problem Framing PDF, and README, and ran my live Replit app to record the current behavior. It then:
  - drafted the rule-based `extractor.py` that stands in for the planned AI extraction
  - drafted the revised `app.py` (editable review, evidence view, confirm/reject, session log, input handling)
  - wrote and ran the test script (`tests/run_test_cases.py`)
  - drafted `revision.md`, this disclosure, and the README.

## Representative prompts
1. **Gemini (Problem Framing):** "Help me outline a system architecture for a multimodal web app that accepts handwritten note images and raw instrument text, sending them to a multimodal AI endpoint to extract structured metadata." *Produced:* a scaffold of the ingest → extract → review flow. *What I changed:* narrowed it to a single-page Replit prototype with no hardware integration.
2. **Claude (this milestone):** "Go into my Google Drive… get caught up on [the Gen AI project]… you'll see in the Google Doc it says assignment due today. So start working on that." *Produced:* the revised code, test cases, and documentation drafts. *What I changed:* **TODO:** describe your edits.
3. **TODO:** add one prompt you used to build the First Working Slice in Replit, what it produced, and what you changed.

## Human judgment
- **TODO (required, must be true):** name at least one AI suggestion you rejected, corrected, or substantially revised, and why. Possible places to look: wording in `revision.md` you disagreed with, a field or rule in `extractor.py` that does not match how your lab actually writes notes, or an earlier Gemini or Replit suggestion you dropped (for example hardware integration, which you ruled out as a non-goal).
- Decisions in this milestone that should be yours to keep or change:
  - Keep extraction rule-based for now rather than wiring up an API before the deadline.
  - Report the Challenge case as **Partial** instead of tuning the rules to make it pass.
  - Block confirmation until conflicts are resolved and values are checked.

## Verification
- The extractor was tested on six synthetic inputs. The raw output is saved in `tests/test_output.txt`, and the test table in `revision.md` was checked against it.
- The app's confirm, reject, and blocked-confirm paths were checked with a scripted run of the code.
- Typical 2 and the Risk case were clicked through in the deployed Replit app, and the results matched the script output.
- **Still needs checking:** Typical 1, the Challenge case, and the invalid cases have only been run through the script, not clicked through in the deployed app.
- No credentials, API keys, or real lab data are in the repository. All test inputs are synthetic.

## AI inside the product
| | |
|---|---|
| **Task** | Turn unstructured lab notes and instrument text (and, later, photos of handwritten notes) into a structured experiment record |
| **Inputs** | Pasted notes; TXT/CSV instrument exports. Photos are planned |
| **Outputs** | Date, sample ID, equipment, settings, observations, follow-ups, linked files, a summary, and the source text for each value |
| **Current status** | **Simulated.** A rule-based stand-in (`extractor.py`) replaces the model. Review, editing, and saving are implemented. OCR and vision-model extraction are planned |
