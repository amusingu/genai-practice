# AI-Use Disclosure: LabLens AI

## Tools used
- **Gemini:** brainstorming and the system outline during Problem Framing.
- **Replit Agent:** helped port and publish the first Streamlit version of the prototype (First Working Slice).
- **Claude (Anthropic):** used during this Prototype Revision milestone.

## How AI helped
- **Problem Framing:** Gemini helped outline the architecture of a multimodal app that takes note images and instrument text.
- **This revision:** Claude helped me turn my feedback into revision priorities. It drafted the rule-based `extractor.py` (the stand-in for the planned AI step), the review-and-confirm changes to `app.py`, the test script, `revision.md`, this disclosure, and the README. Later, at my request, it also restyled the app's appearance. I reviewed the drafts and decided what to keep and submit.

## Representative prompts
1. **Gemini (Problem Framing):** "Help me outline a system architecture for a multimodal web app that accepts handwritten note images and raw instrument text, sending them to a multimodal AI endpoint to extract structured metadata." *Produced:* a scaffold of the ingest → extract → review flow. *What I changed:* I narrowed it to a single-page Replit prototype with no hardware integration.
2. **Claude (this milestone):** I asked Claude to review my project folder (problem framing, prototype note, links, and feedback) and help with the Prototype Revision assignment. *Produced:* drafts of the extractor, app changes, test cases, and documentation. *What I did with it:* I reviewed the drafts and decided what to keep and submit.
3. **Claude (this milestone):** "Make the website a little more aesthetically pleasing." *Produced:* a header banner, a three-step progress tracker, coloured status labels, and a teal theme, with no change to the app's logic.

## Human judgment
- Claude suggested adding before/after screenshot files to the repository. I decided not to include them. The before/after comparison is recorded in the written table in `revision.md` and in the raw test output.
- I kept extraction rule-based for this milestone rather than connecting an AI API before the deadline.
- I reported the Challenge case as **Partial** instead of adjusting the rules to make it pass.
- I kept the rule that a record cannot be confirmed until conflicts are resolved and the values are checked.

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
