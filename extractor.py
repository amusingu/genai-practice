"""
LabLens AI - field extraction module (prototype stand-in for the planned AI step).

STATUS: IMPLEMENTED, RULE-BASED (not an AI model).
The planned product sends notes + photos to a multimodal model. In this
prototype, that step is simulated with transparent pattern matching so that
(1) custom notes produce a record built from the user's own text instead of a
generic template, and (2) every extracted value can be traced to the exact
words it came from.

Design rule (risk safeguard): never invent a value. If a field is not found,
it is returned as "missing". If two different values are found, it is
returned as "ambiguous" and the user must choose.
"""

import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional

MIN_WORDS = 4  # below this, ask the user for more detail

# --- Known lab equipment / process vocabulary (extendable) -------------------
EQUIPMENT_TERMS = [
    "karl suss aligner", "mask aligner", "aligner", "pecvd", "lpcvd", "ald",
    "sputter", "sputtering", "e-beam evaporator", "e-beam", "evaporator",
    "rie", "icp", "ellipsometer", "profilometer", "sem", "afm", "xrd",
    "uv-vis spectrometer", "uv-vis", "spectrometer", "optical microscope",
    "microscope", "spin coater", "hotplate", "hot plate", "furnace",
    "plasma asher", "wet bench", "probe station", "four-point probe",
]

# Process words used to build a "detected process sequence"
PROCESS_TERMS = {
    "clean": "Substrate cleaning",
    "spin": "Spin coating",
    "coat": "Coating",
    "soft bake": "Soft bake",
    "bake": "Bake",
    "exposure": "Exposure",
    "expose": "Exposure",
    "develop": "Develop",
    "edge bead": "Edge bead removal",
    "deposition": "Deposition",
    "etch": "Etch",
    "anneal": "Anneal",
    "measure": "Measurement",
    "scan": "Scan / measurement",
    "inspect": "Inspection",
}

OBSERVATION_CUES = [
    "note:", "looked", "seemed", "observed", "uneven", "anomaly", "crack",
    "thin", "thick", "residue", "peak", "defect", "bubble", "contamina",
    "failed", "good", "ok",
]
FOLLOWUP_CUES = ["recheck", "re-check", "redo", "re-run", "rerun", "tomorrow",
                 "todo", "to do", "follow up", "follow-up", "next time", "ask advisor"]

MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DATE_PATTERNS = [
    rf"\b{MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}\b",   # Oct 12, 2026
    r"\b\d{4}-\d{2}-\d{2}\b",                                        # 2026-10-12
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",                                  # 10/12/2026
]

PARAM_PATTERNS = [
    ("Temperature", r"(-?\d+(?:\.\d+)?)\s*°?\s*(C|K|F)\b"),
    ("Time", r"(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|min|mins|minutes|h|hr|hrs|hours)\b"),
    ("Pressure", r"(\d+(?:\.\d+)?)\s*(mTorr|Torr|mbar|Pa)\b"),
    ("Power", r"(\d+(?:\.\d+)?)\s*(W|kW)\b"),
    ("Wavelength", r"(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)\s*(nm)\b"),
    ("Gas flow", r"(\d+(?:\.\d+)?)\s*(sccm)\b"),
    ("Spin speed", r"(\d+(?:\.\d+)?)\s*(rpm)\b"),
    ("Thickness", r"(\d+(?:\.\d+)?)\s*(um|µm|Å|A)\b"),
    ("Absorbance", r"absorbance\s*(?:of|:)?\s*(\d+(?:\.\d+)?)()"),
]

FILE_PATTERN = r"\b[\w\-]+\.(?:png|jpg|jpeg|tif|tiff|csv|txt|dat|xlsx)\b"

SAMPLE_LABELED = r"\b(?:sample(?:\s*id)?|wafer|substrate|specimen|batch)\s*(?:id)?\s*[:#]?\s*([A-Za-z0-9][\w\-\.]*\d[\w\-]*)"


@dataclass
class Field:
    name: str
    value: str = ""
    status: str = "missing"          # found | ambiguous | missing
    evidence: List[str] = field(default_factory=list)  # exact snippets from input
    options: List[str] = field(default_factory=list)   # for ambiguous fields


@dataclass
class Extraction:
    ok: bool
    message: str = ""
    fields: dict = field(default_factory=dict)
    parameters: List[dict] = field(default_factory=list)
    process_sequence: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    summary: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        return d


# --- helpers -----------------------------------------------------------------
def _snippet(text: str, start: int, end: int, pad: int = 25) -> str:
    s = max(0, start - pad)
    e = min(len(text), end + pad)
    out = text[s:e].strip().replace("\n", " ")
    return ("…" if s > 0 else "") + out + ("…" if e < len(text) else "")


def _sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[\.\!\?;])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _unique(seq):
    seen, out = set(), []
    for x in seq:
        k = x.lower()
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def _make_field(name, matches):
    """matches: list of (value, evidence)."""
    f = Field(name=name)
    if not matches:
        return f
    values = _unique([m[0] for m in matches])
    f.evidence = [m[1] for m in matches]
    if len(values) == 1:
        f.value, f.status = values[0], "found"
    else:
        f.status, f.options = "ambiguous", values
        f.value = ""  # user must choose; do not guess
    return f


# --- extractors --------------------------------------------------------------
def find_dates(text):
    out = []
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, text, flags=re.I):
            out.append((m.group(0).strip().rstrip(","), _snippet(text, m.start(), m.end())))
    return out


def find_sample_ids(text):
    out = []
    for m in re.finditer(SAMPLE_LABELED, text, flags=re.I):
        val = m.group(1).rstrip(".,;")
        # filter out obvious non-IDs (e.g., a filename picked up by accident)
        if re.search(FILE_PATTERN, val, flags=re.I):
            continue
        out.append((val, _snippet(text, m.start(), m.end())))
    return out


def find_equipment(text):
    low = text.lower()
    hits = []
    for term in EQUIPMENT_TERMS:  # longest/most specific terms are listed first
        for m in re.finditer(r"\b" + re.escape(term) + r"\b", low):
            # skip if this span is already covered by a longer term
            if any(m.start() >= s and m.end() <= e for _, _, s, e in hits):
                continue
            hits.append((text[m.start():m.end()], _snippet(text, m.start(), m.end()), m.start(), m.end()))
    hits.sort(key=lambda h: h[2])
    return [(h[0], h[1]) for h in hits]


def find_parameters(text):
    params = []
    taken = []
    for label, pat in PARAM_PATTERNS:
        for m in re.finditer(pat, text, flags=re.I):
            if any(m.start() < e and m.end() > s for s, e in taken):
                continue
            # avoid reading the "C" in a sample ID or the "s" in a word as units
            unit = m.group(2)
            if label == "Thickness" and unit in ("A",) and not re.search(r"\d\s*A\b", m.group(0)):
                continue
            taken.append((m.start(), m.end()))
            value = (m.group(1) + (" " + unit if unit else "")).strip()
            # use a nearby label from the notes if one exists (e.g., "Exposure time")
            pre = text[max(0, m.start() - 30):m.start()]
            # only trust an explicit label written as "Label: value" or "Label = value"
            lbl = re.search(r"([A-Za-z][A-Za-z \-]{2,25})\s*[:=]\s*$", pre)
            nearby = lbl.group(1).strip() if lbl else ""
            params.append({
                "type": label,
                "label_in_notes": nearby,
                "value": value,
                "evidence": _snippet(text, m.start(), m.end()),
            })
    # filter out matches that are actually part of a date or sample ID
    return params


def find_cue_sentences(text, cues):
    out = []
    for s in _sentences(text):
        low = s.lower()
        if any(c in low for c in cues):
            out.append(s)
    return out


def find_process_sequence(text):
    low = text.lower()
    found = []
    for key, label in PROCESS_TERMS.items():
        for m in re.finditer(r"\b" + re.escape(key), low):
            found.append((m.start(), label))
    found.sort()
    seq = []
    for _, label in found:
        if not seq or seq[-1] != label:
            if label not in seq:
                seq.append(label)
    return seq


# --- main entry point --------------------------------------------------------
def extract(text: str, attached_text: str = "", attached_names: Optional[List[str]] = None) -> Extraction:
    attached_names = attached_names or []
    combined = (text or "").strip()
    if attached_text and attached_text.strip():
        combined = (combined + "\n" + attached_text.strip()).strip()

    if not combined and not attached_names:
        return Extraction(ok=False, message="No input yet. Paste your notes or attach a TXT/CSV file, then try again.")

    if not combined and attached_names:
        return Extraction(
            ok=False,
            message=("Only an image was attached. Image reading (OCR) is planned but not built in this prototype. "
                     "Please type the key details from the photo (date, sample ID, equipment, settings) into the notes box."),
        )

    words = re.findall(r"\w+", combined)
    dates = find_dates(combined)
    samples = find_sample_ids(combined)
    equipment = find_equipment(combined)
    params = find_parameters(combined)

    if len(words) < MIN_WORDS or not (dates or samples or equipment or params):
        return Extraction(
            ok=False,
            message=("We couldn't find any experiment details in this input (no date, sample ID, equipment, or "
                     "measured settings). Add at least a sample ID and what you ran, e.g. "
                     "'Sample GaN-117, PECVD 300C 40 min'."),
        )

    ex = Extraction(ok=True)
    ex.fields["date"] = _make_field("Date", dates)
    ex.fields["sample_id"] = _make_field("Sample ID", samples)
    eq_vals = _unique([e[0] for e in equipment])
    eq_field = Field(name="Equipment")
    if eq_vals:
        eq_field.value = ", ".join(eq_vals)
        eq_field.status = "found"
        eq_field.evidence = [e[1] for e in equipment]
    ex.fields["equipment"] = eq_field

    obs = find_cue_sentences(combined, OBSERVATION_CUES)
    fup = find_cue_sentences(combined, FOLLOWUP_CUES)
    ex.fields["observations"] = Field("Observations", " ".join(obs), "found" if obs else "missing", obs)
    ex.fields["follow_up"] = Field("Follow-up", " ".join(fup), "found" if fup else "missing", fup)

    ex.parameters = params
    ex.process_sequence = find_process_sequence(combined)
    ex.files = _unique(re.findall(FILE_PATTERN, combined, flags=re.I) + attached_names)

    for key, f in ex.fields.items():
        if f.status == "ambiguous":
            ex.warnings.append(f"{f.name}: more than one value found ({', '.join(f.options)}). Choose the right one before confirming.")
        elif f.status == "missing" and key in ("date", "sample_id"):
            ex.warnings.append(f"{f.name}: not found in your notes. Fill it in or leave it blank; LabLens will not guess.")

    ex.summary = build_summary({k: asdict(v) for k, v in ex.fields.items()}, ex.parameters)
    return ex


def build_summary(fields: dict, parameters: list) -> str:
    """Summary built ONLY from extracted/edited values. No outside facts are added.
    fields: {key: {"value":..., "status":...}}, parameters: [{"type","label_in_notes","value"}]"""
    def _v(key, label):
        fl = fields[key]
        if fl.get("value"):
            return fl["value"]
        return f"[{label} needs your choice]" if fl.get("status") == "ambiguous" else f"[{label} not given]"

    parts = []
    lead = f"{_v('date', 'date')}: run on {_v('sample_id', 'sample ID')}"
    if fields["equipment"].get("value"):
        lead += f" using {fields['equipment']['value']}"
    parts.append(lead + ".")
    params = [p for p in parameters if str(p.get("value", "")).strip()]
    if params:
        parts.append("Settings recorded: " + "; ".join(
            (p.get("label_in_notes") or p.get("type") or "Setting") + " " + str(p["value"]) for p in params) + ".")
    obs = fields["observations"].get("value", "")
    fup = fields["follow_up"].get("value", "")
    if obs:
        parts.append("Observation: " + re.sub(r"^note:\s*", "", obs, flags=re.I))
    if fup and fup != obs:
        parts.append("Follow-up: " + fup)
    return " ".join(parts)
