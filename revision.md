# LabLens AI: Prototype Revision

**Milestone:** Project Prototype Revision (due Nov 19, 2026)
**Intended user:** a graduate student researcher who needs to rebuild what happened in an experiment from scattered notes, photos, and instrument files.
**Central task:** paste or attach raw experiment notes → get a draft structured record → check and correct it → confirm it into a log.

---

## 1. What I changed and why

I reviewed the three tests from the First Working Slice, the known limitations I listed then, and the feedback I received (section 2). The biggest gap was that the central task only worked for my two prepared samples. Any real note a researcher typed produced the same generic placeholder record (`EXP-2026-9999`, "Custom Sample / Ingested", "General Workbench Log"), even when the sample ID and settings were written plainly in the text. I also had not built the review-and-confirm step that my Problem Framing promised.

I chose three priority improvements, all on the central task:

| # | Priority improvement | Before | After |
|---|---|---|---|
| 1 | **Custom notes produce a record built from the user's own text** | Any custom input returned a fixed placeholder record | `extractor.py` pulls out date, sample ID, equipment, settings (temperature, time, power, wavelength, pressure, etc.), observations, follow-ups, and file names from the user's text |
| 2 | **Human-in-the-loop review: edit, confirm, or reject** | Read-only card; nothing could be corrected or saved | Every field is editable, settings are an editable table, the summary rebuilds from the corrected values, and **Confirm record** / **Reject draft** save the record to a session log or discard it. The log can be downloaded as JSON |
| 3 | **Clearer handling of empty, unsupported, and file inputs** | Empty input was flagged, but attached files were listed by name only | TXT/CSV contents are now read and used. An image-only upload explains that photo reading is planned and asks for the key values. Text with no lab details gets a specific example of what to enter |

### How the AI part works now (implemented vs. simulated vs. planned)

| Part | Status | How it works |
|---|---|---|
| Input handling, TXT/CSV reading, editing, confirm/reject, session log, JSON export | **Implemented** | Streamlit (`app.py`) |
| "AI extraction" of fields from notes | **Simulated (Wizard-of-Oz stand-in)** | `extractor.py` uses transparent rule-based pattern matching, not a language model. It stands in for the planned multimodal model so the review experience can be tested on real-looking notes |
| Reading handwriting and photos, linking records across sessions, persistent storage | **Planned** | Not built |

**Intended AI role (unchanged):** a multimodal model receives a photo of handwritten bench notes plus instrument text, and returns structured fields (date, sample ID, equipment, parameters, observations) with a pointer to the source text for each one. The value for the user is skipping manual transcription and tagging, which is the step researchers skip under time pressure.

**Implementation note:** I kept extraction rule-based in this milestone so I could test the review flow and the risk safeguard without paying for or debugging an API. That means the tests below say nothing about how accurate a real model would be (see section 3).

---

## 2. Response to feedback

All three peer reviews I received said the same thing: my submission contained only a PDF with no link to the GitHub repository or the Replit app, so nothing could be tested. The instructor feedback raised three specific issues. None of the reviews commented on the product itself, because no reviewer could open it.

| Feedback or observed issue | Decision | What changed, or why it was deferred |
|---|---|---|
| Peer reviewers (3 of 3): no repository or Replit link, so nothing could be tested | **Acted on** | Links to the live prototype and repository are at the top of the README with access instructions. The Canvas submission now includes the repository link |
| Instructor: the live app was not part of my own evidence | **Acted on** | The before/after comparison uses a screenshot of the live Replit app (`docs/screenshots/`). Test cases record what the app actually did |
| Instructor: no next steps listed with limitations | **Acted on** | Added "Remaining limitations" and "Next priorities" (sections 5 and 6) |
| Instructor: the PDF named no repository | **Acted on** | All documentation now lives in the repository and is linked from the README |
| My own known limitation: attached files listed by name only | **Acted on (partly)** | TXT/CSV contents are now read. Images are still not read; the app says so at upload time and asks the user to type the key values |
| My own known limitation: no persistent storage | **Adapted** | Added a confirmed-record log and JSON export for the session. A real database is deferred because it is not needed to test the central task |
| My own known limitation: AI is simulated | **Deferred** | Still simulated, but now honest and testable: every value shows the exact words it came from. A live model is the top next priority |

### Substitute user session (because peer feedback did not cover the product)

> **TODO (Ategeka):** The assignment asks for one short session with a classmate or another person when peer feedback was not usable. Have one person try the central task on the revised app (for example, paste one of their own lab notes, or Sample 1), then fill in this table with what actually happened. Do not include their name.

| What they tried | What happened | What I changed or decided |
|---|---|---|
| _to fill in_ | _to fill in_ | _to fill in_ |

---

## 3. Evaluation

**How these were run:** Each input was run through `extractor.py` with `tests/run_test_cases.py`. The raw output is saved in `tests/test_output.txt`. Typical 2 and the Risk case were also clicked through in the deployed Replit app (Nov 19), and the on-screen fields, warnings, summary, and Confirm-button state matched the table. Typical 2 was confirmed into the session log. Screenshots are in `docs/screenshots/`.

**What these tests can and cannot show:** The extraction step is a rule-based stand-in, so these tests check whether the review flow is useful and whether the safeguard works. They do **not** measure the accuracy or reliability of an AI model.

| Case | Input or action | Expected result / success criterion | Actual result | Pass, partial, or fail | Implication or next step |
|---|---|---|---|---|---|
| **Typical 1** | Sample 1: "Date: Oct 12, 2026. Sample ID: Si-Wafer-402. Used Karl Suss Aligner. Exposure time: 8.5s. Note: Edge bead removal seemed uneven…" | Date, sample ID, equipment, exposure time, observation, and attached file name are all filled in correctly with evidence. Nothing is invented | Date `Oct 12, 2026`, sample `Si-Wafer-402`, equipment `Karl Suss Aligner`, setting `Exposure time 8.5 s`, observation about the uneven edge bead, file `optical_microscope_042.png`. Follow-up correctly shown as "not found" | **Pass** | Works for clearly labeled notes |
| **Typical 2** | Custom informal note: "Nov 3 2026. Sample GaN-117. Ran PECVD SiN deposition, 300C, 40 min. Thickness looked thin on ellipsometer, recheck tomorrow." | Record uses GaN-117, Nov 3 2026, PECVD, 300 C, 40 min, and flags the follow-up, instead of a generic template | All of those fields were extracted. Equipment `PECVD, ellipsometer`. The same sentence appears as both observation and follow-up | **Pass** (minor issue) | Duplicate sentence is easy to edit, but observation and follow-up should be split within a sentence |
| **Challenge** | Shorthand note with an uncertain ID and no date: "laser test again, 2.5 W, 1064 nm, spot looked off-center on sample LT-3? maybe LT-8. redo w/ new lens" | Power and wavelength extracted, date flagged as missing, and the uncertain sample ID (LT-3 vs LT-8) flagged for the user to choose | Power `2.5 W`, wavelength `1064 nm`, follow-up `redo w/ new lens`, date flagged "not found". **But the sample ID was shown as a confident `LT-3`.** The writer's doubt ("?", "maybe LT-8") was missed, and "laser" was not recognized as equipment | **Partial** | A real miss: confident output when the source expresses doubt. The evidence snippet still shows "LT-3? maybe LT-8", and the user must check before confirming, but the field should be marked uncertain. Next fix: treat "?", "maybe", "or" next to an ID as ambiguous |
| **Invalid / empty** | (a) Clicked Extract with nothing entered. (b) Entered "hello there". (c) Attached only a JPG photo | No crash, no fake record. A specific message tells the user what to do | (a) "No input yet. Paste your notes or attach a TXT/CSV file…" (b) "We couldn't find any experiment details… Add at least a sample ID and what you ran…" (c) Explains photo reading is planned and asks the user to type the key values. No record created in any case | **Pass** | The old version showed a template record for any non-empty text; this is now blocked |
| **Risk** | "Wafer W-12 and wafer W-14 went in the furnace at 950C for 2 h on 11/02/2026, not sure which one cracked." Then tried to confirm without choosing | The app must not pick a wafer for the user. Confirm stays blocked until the user chooses a sample ID and ticks "I checked these values" | Sample ID marked **ambiguous (W-12, W-14)** with a warning. Summary reads "run on [sample ID needs your choice]". Confirm stayed disabled until a choice was made and the box was ticked. After choosing W-14, the saved record listed `sample_id` under `user_edited_fields` | **Pass** | The safeguard works when the conflict is explicit. It does not yet cover hedged wording (see Challenge) |

**Repeat check:** Typical 2 was run 3 times and gave 1 distinct output. The stand-in is rule-based, so its output does not vary. A live generative model will vary, and this check must be repeated once one is connected.

### Before and after: same input

**Input (Typical 2):** `Nov 3 2026. Sample GaN-117. Ran PECVD SiN deposition, 300C, 40 min. Thickness looked thin on ellipsometer, recheck tomorrow.`

| | Before (live Replit app, Nov 19) | After (revised) |
|---|---|---|
| Record ID | `EXP-2026-9999` (same for every custom input) | Assigned only when the user confirms (`LL-<date>-<time>`) |
| Sample ID | "Custom Sample / Ingested" | `GaN-117`, with the source text shown |
| Date | not shown | `Nov 3 2026` |
| Equipment | "General Workbench Log" | `PECVD, ellipsometer` |
| Settings | none | `Temperature 300 C`, `Time 40 min` (editable table) |
| Summary | First 120 characters of the raw text, cut off mid-word | "Nov 3 2026: run on GaN-117 using PECVD, ellipsometer. Settings recorded: Temperature 300 C; Time 40 min. Observation: Thickness looked thin…" |
| Steps | Generic: "Raw log ingestion into LabLens engine…" | `Deposition` (only steps mentioned in the note) |
| User control | None (read-only) | Edit every field, then confirm or reject |

Screenshots: before `docs/screenshots/before_custom_input_GaN-117.jpg`, after `docs/screenshots/after_custom_input_GaN-117.jpg`. The risk safeguard is shown in `docs/screenshots/risk_case_ambiguous_sample_id.jpg`.

**Did the revision help?** Yes for this issue. Before, the record ignored everything the researcher wrote. After, every field comes from their words and can be traced back to them. This was the most important gap, because it is the only path a real user would take.

### What the evidence tells me

The review flow now works for the two realistic note styles I tested, and the app refuses to produce a record from empty or non-lab input, which the old version did not. The safeguard also works when two values clearly conflict. What remains unreliable is hedged or shorthand language: in the Challenge case the tool presented "LT-3" confidently when the researcher was unsure, so a busy user who skims could still save the wrong ID. That is the exact failure the product is meant to prevent. These results support the claim that a review-first record card is understandable and saves retyping. They do **not** support any claim about AI accuracy, because no model is connected yet. Next I would (1) flag hedged values as uncertain, (2) connect a real model and repeat these five cases plus the three-run variation check, and (3) test with real researchers' notes, de-identified, to see what vocabulary the rules miss.

---

## 4. Risk response: wrong or invented details in a permanent record

**Who could be affected:** the researcher, their advisor, and anyone who later tries to reproduce the experiment from the record.

**What might go wrong:** an AI extractor could fill in a missing value, attach an observation to the wrong sample, or sound confident about something the researcher was unsure of. Because the output looks official, users may accept it without checking (over-reliance on AI, or automation bias). In a lab, a crack attributed to the wrong wafer or a wrong temperature can waste weeks of work or make a result impossible to reproduce.

**What I changed:**
- **No invented values.** If a field is not in the text, it is shown as "not found" and the summary says "[not given]". The old placeholders ("Custom Sample", "General Workbench Log") are removed.
- **Conflicts force a choice.** If two values are found (for example W-12 and W-14), the field is left empty until the user picks one or types their own.
- **Evidence beside every value.** Each field has "Where this came from", showing the exact words it was taken from, and the original notes can be shown side by side.
- **Confirmation requires review.** Confirm stays disabled until there is a Sample ID, every conflict is resolved, and the user ticks "I checked these values against my original notes." Fields the user changed are recorded in `user_edited_fields`.
- **Privacy.** The app tells users to use non-sensitive notes. Nothing is stored after the tab closes, and uploaded files are read in memory only. This matters because lab notes can contain unpublished, proprietary protocols.

**Risk test result:** passed for an explicit conflict (Risk case). Partly failed for a hedged value (Challenge case).

**What risk remains:** a tick box does not guarantee that someone actually reads the evidence. The extractor can still be confidently wrong when doubt is expressed in words. A real model would add a new risk: hallucinated values that look plausible. A future version should mark low-confidence values as uncertain, keep the "not found / never guess" rule in the model's instructions, and check that each extracted value appears in the source text.

---

## 5. Remaining limitations (ranked by effect on the central task)

1. **Extraction is rule-based, not AI.** It only knows the equipment and units in its word lists (for example, it missed "laser") and cannot read handwriting or photos.
2. **Hedged values are not flagged** (Challenge case).
3. **Observation and follow-up can duplicate** when one sentence contains both.
4. **Records last only for the session.** JSON export is the only way to keep them.
5. **Not yet tested with a real user** beyond the substitute session.

## 6. Next priorities

1. Flag hedged or uncertain values ("?", "maybe", "or") as ambiguous. This is a small change that closes the Challenge failure.
2. Connect a live multimodal model behind the same review screen, keep the "never guess" rule, and re-run all five cases plus three-run variation checks.
3. Run a short session with 2–3 graduate researchers using de-identified notes, and expand the equipment and unit vocabulary from what they actually write.
