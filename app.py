"""
LabLens AI - Prototype Revision (Nov 2026)

Run:  streamlit run app.py

What is real vs simulated in this version
- IMPLEMENTED: input handling, TXT/CSV file reading, rule-based field extraction
  (extractor.py), evidence display, editable review, confirm/reject, session log,
  JSON export.
- SIMULATED (Wizard-of-Oz): the "AI extraction" step. extractor.py stands in for
  the planned multimodal model using transparent pattern matching.
- PLANNED: reading handwriting/photos (OCR + vision model), persistent storage,
  linking records across sessions.
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from extractor import extract, build_summary

st.set_page_config(page_title="LabLensAI Prototype", layout="centered")

# --------------------------------------------------------------------------
# Sample data (synthetic)
# --------------------------------------------------------------------------
SAMPLES = {
    "Custom Input": "",
    "Sample 1: Cleanroom Optical Lithography Notes": (
        "Date: Oct 12, 2026. Sample ID: Si-Wafer-402. Used Karl Suss Aligner. "
        "Exposure time: 8.5s. Note: Edge bead removal seemed uneven on the south quadrant. "
        "File attached: optical_microscope_042.png"
    ),
    "Sample 2: UV-Vis Spectrometer Raw Output": (
        "Absorbance Spectrum Run #3. Peak wavelength: 520nm. "
        "Buffer solution: PBS pH 7.4. Temperature: 22C. Drift observed after 15 mins."
    ),
}
MAX_FILE_CHARS = 20000

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("draft", None)        # current Extraction dict
ss.setdefault("draft_n", 0)         # bumps to give widgets fresh keys
ss.setdefault("log", [])            # confirmed records
ss.setdefault("flash", None)


def _rerun():
    (getattr(st, "rerun", None) or st.experimental_rerun)()


# --------------------------------------------------------------------------
# Header + honest status
# --------------------------------------------------------------------------
st.title("LabLensAI")
st.subheader("Laboratory Record-Continuity Platform")
st.write(
    "Paste messy lab notes or an instrument export. LabLens drafts a structured experiment "
    "record, **shows you exactly which words each value came from**, and lets you correct it "
    "before anything is saved."
)
with st.expander("Prototype status: what is real vs. simulated", expanded=False):
    st.markdown(
        "- **Working:** text + TXT/CSV input, field extraction, evidence view, editing, "
        "confirm/reject, session log, JSON export.\n"
        "- **Simulated AI:** extraction uses rule-based pattern matching as a stand-in for the "
        "planned multimodal model. It only reads text; it does not understand chemistry.\n"
        "- **Planned:** reading photos of handwritten notes (OCR / vision model), saving records "
        "between sessions, linking related runs."
    )
st.caption(
    "Privacy: use sample or non-sensitive notes. Nothing is stored after you close this tab, "
    "and uploaded files are read in memory only."
)
st.divider()

# --------------------------------------------------------------------------
# Step 1: Ingest
# --------------------------------------------------------------------------
st.header("1. Add experiment notes")
choice = st.selectbox("Start from a sample or choose Custom Input:", list(SAMPLES.keys()))
notes = st.text_area(
    "Paste raw notes, metadata, or instrument log text:",
    value=SAMPLES[choice],
    height=150,
    key=f"notes_{choice}",
    placeholder="e.g. Nov 3 2026. Sample GaN-117. PECVD SiN deposition, 300C, 40 min. "
                "Thickness looked thin on ellipsometer, recheck tomorrow.",
)
upload = st.file_uploader(
    "Attach an instrument file (TXT/CSV is read) or a photo (PNG/JPG is listed, not read yet)",
    type=["png", "jpg", "jpeg", "csv", "txt"],
)

attached_text, attached_names = "", []
if upload is not None:
    attached_names.append(upload.name)
    if upload.name.lower().endswith((".txt", ".csv")):
        try:
            attached_text = upload.getvalue().decode("utf-8", errors="replace")[:MAX_FILE_CHARS]
            st.caption(f"Read {len(attached_text):,} characters from {upload.name}.")
        except Exception:
            st.warning(f"Could not read {upload.name}. Paste its key lines into the notes box instead.")
    else:
        st.info(
            f"{upload.name} attached. Photo reading is **planned, not built**: type the key values "
            "from the photo (date, sample ID, settings) into the notes box so they appear in the record."
        )

if st.button("Extract draft record", type="primary"):
    result = extract(notes, attached_text, attached_names)
    if not result.ok:
        ss.draft = None
        ss.flash = ("warn", result.message)
    else:
        ss.draft = result.to_dict()
        ss.draft["source_text"] = (notes + ("\n" + attached_text if attached_text else "")).strip()
        ss.draft_n += 1
        ss.flash = None

if ss.flash:
    kind, msg = ss.flash
    (st.warning if kind == "warn" else st.success)(msg)

# --------------------------------------------------------------------------
# Step 2: Review & correct
# --------------------------------------------------------------------------
STATUS_BADGE = {
    "found": ":green[found in notes]",
    "ambiguous": ":orange[more than one value: choose]",
    "missing": ":red[not found: fill in or leave blank]",
}

if ss.draft:
    d, n = ss.draft, ss.draft_n
    st.divider()
    st.header("2. Review the draft record")
    st.caption("Draft values come only from your text. Check each one against the evidence before confirming.")

    for w in d["warnings"]:
        st.warning(w)

    edited = {}
    for key in ["date", "sample_id", "equipment", "observations", "follow_up"]:
        f = d["fields"][key]
        st.markdown(f"**{f['name']}** · {STATUS_BADGE[f['status']]}")
        if f["status"] == "ambiguous":
            pick = st.radio(
                f"Which {f['name']} is correct?",
                ["— choose —"] + f["options"] + ["None of these / type my own"],
                key=f"pick_{key}_{n}", horizontal=True, label_visibility="collapsed",
            )
            if pick == "None of these / type my own":
                edited[key] = st.text_input(f"{f['name']} (your entry)", key=f"own_{key}_{n}")
            else:
                edited[key] = "" if pick == "— choose —" else pick
        elif key in ("observations", "follow_up"):
            edited[key] = st.text_area(f["name"], value=f["value"], key=f"f_{key}_{n}",
                                       height=70, label_visibility="collapsed")
        else:
            edited[key] = st.text_input(f["name"], value=f["value"], key=f"f_{key}_{n}",
                                        label_visibility="collapsed")
        if f["evidence"]:
            with st.expander("Where this came from"):
                for ev in f["evidence"]:
                    st.code(ev, language=None)

    st.markdown("**Recorded settings** · edit, add, or delete rows")
    params_df = pd.DataFrame(d["parameters"] or [], columns=["type", "label_in_notes", "value", "evidence"])
    params_edit = st.data_editor(
        params_df, num_rows="dynamic", width="stretch", key=f"params_{n}",
        column_config={"evidence": st.column_config.TextColumn("evidence (from notes)", disabled=True)},
    )

    if d["process_sequence"]:
        st.markdown("**Process steps mentioned (in order):** " + " → ".join(d["process_sequence"]))
    if d["files"]:
        st.markdown("**Linked files:** " + ", ".join(d["files"]))

    # Rebuild summary from the user's corrected values, so edits flow through
    preview = {**d, "fields": {k: {**v} for k, v in d["fields"].items()}}
    for k, v in edited.items():
        preview["fields"][k]["value"] = v
        preview["fields"][k]["status"] = "found" if v else preview["fields"][k]["status"]
    preview["parameters"] = params_edit.fillna("").to_dict("records")

    summary = st.text_area("Structured summary (built only from the values above; editable)",
                           value=build_summary(preview["fields"], preview["parameters"]), key=f"summary_{n}_{hash(str(edited) + str(preview['parameters']))}", height=110)

    with st.expander("Show original notes side by side"):
        st.text(d.get("source_text", ""))

    unresolved = [d["fields"][k]["name"] for k in edited
                  if d["fields"][k]["status"] == "ambiguous" and not edited[k]]
    checked = st.checkbox("I checked these values against my original notes.", key=f"check_{n}")

    blockers = []
    if not edited["sample_id"].strip() and "Sample ID" not in unresolved:
        blockers.append("add a Sample ID")
    if unresolved:
        blockers.append("choose a value for " + ", ".join(unresolved))
    if not checked:
        blockers.append("tick the check box above")
    if blockers:
        st.caption("To confirm: " + "; ".join(blockers) + ".")

    c1, c2 = st.columns(2)
    if c1.button("Confirm record", type="primary", disabled=bool(blockers)):
        now = datetime.now()
        rec = {
            "record_id": f"LL-{now:%Y%m%d-%H%M%S}",
            "confirmed_at": now.isoformat(timespec="seconds"),
            **{k: v for k, v in edited.items()},
            "parameters": [{k: r[k] for k in ("type", "label_in_notes", "value")} for r in preview["parameters"]],
            "process_sequence": d["process_sequence"],
            "files": d["files"],
            "summary": summary,
            "user_edited_fields": [k for k in edited if edited[k] != d["fields"][k]["value"]],
            "extraction_method": "rule-based stand-in (simulated AI)",
        }
        ss.log.append(rec)
        ss.draft = None
        ss.flash = ("ok", f"Record {rec['record_id']} saved to this session's log.")
        _rerun()
    if c2.button("Reject draft"):
        ss.draft = None
        ss.flash = ("warn", "Draft discarded. Nothing was saved. Edit your notes and extract again.")
        _rerun()

# --------------------------------------------------------------------------
# Step 3: Session log
# --------------------------------------------------------------------------
if ss.log:
    st.divider()
    st.header("3. Confirmed records (this session)")
    st.dataframe(
        pd.DataFrame([{k: r[k] for k in ("record_id", "date", "sample_id", "equipment", "summary")} for r in ss.log]),
        width="stretch", hide_index=True,
    )
    st.download_button("Download records as JSON", data=json.dumps(ss.log, indent=2),
                       file_name="lablens_records.json", mime="application/json")
    st.caption("Records are kept only for this browser session (persistent storage is planned).")
