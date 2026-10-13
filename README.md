# genai-prototype
# LabLensAI — Laboratory Record-Continuity Platform

> An AI-assisted laboratory record-continuity platform that automatically organizes heterogeneous experiment data—from cleanroom photos and handwritten notes to instrument logs—into one searchable, connected digital record for graduate researchers.

## First Working Slice
This prototype allows a user (e.g., a graduate researcher) to ingest raw, unorganized experiment notes or instrument logs and instantly view a structured, indexed digital record card containing identified equipment, extracted tags, procedural steps, and linked file assets.

## Prototype Access
- **Working Replit Prototype:** https://lab-lens-ai.replit.app/lablens-streamlit/
- **Instructions:** Open the link, select a pre-populated sample scenario or enter custom experiment notes, and click **"Ingest & Link Record"** to view the resulting organized record.

## AI Functionality & Prototype Status
- **Intended AI Role:** A multimodal vision-language model engine that automatically parses unstructured handwritten notes, cleanroom photos, and raw instrument data files to cross-link experimental context automatically.
- **Current Functional Behavior:** UI flow, form input handling, empty state validation, and dynamic card generation.
- **Simulated / Wizard-of-Oz Behavior:** Text extraction, equipment identification, tagging, and procedural breakdown are simulated using keyword matching and prewritten outputs to demonstrate the intended user experience before API integration.

## Test Results

| Test Case | Input or Action | What Happened | Status |
| :--- | :--- | :--- | :--- |
| **Typical Case** | Selected Sample 1 (Cleanroom Lithography Notes) and submitted. | Rendered structured record EXP-2026-0891 with tags, equipment metadata, and step breakdown. | **Pass** |
| **Challenge Case** | Submitted informal, unformatted laser test notes with missing details. | Generated generic record ID EXP-2026-9999 with basic summary; could not extract discrete steps. | **Partial** |
| **Invalid Case** | Clicked process button with empty input field and no files. | Correctly flagged error requiring data input before proceeding. | **Pass** |

## Known Limitations
1. **Simulated AI Processing:** Dynamic optical character recognition (OCR) and vision-language extraction are hardcoded/simulated for prototype evaluation.
2. **No Persistent Data Storage:** Results exist only during the active browser session and are not saved to a database or ELN backend.
3. **Limited Input File Ingestion:** Attached files are listed by file name without content-level parsing.
