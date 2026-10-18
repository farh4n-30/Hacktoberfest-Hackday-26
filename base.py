"""Config + i18n + state + rules. Imports nothing local (one lazy import in load_demo)."""
import json
import re
from datetime import date, datetime, timedelta, timezone

import streamlit as st


APP_NAME = "Diabetes-" 
EMERGENCY_NUMBER = "999" 
LANGS = {"en": "English", "bn": "বাংলা"}
MGDL_PER_MMOL = 18.0 
HYPO_L1 = 70  # VERIFY mg/dL, low
HYPO_L2 = 54  # VERIFY mg/dL, severe low
VERY_HIGH = 250  # VERIFY mg/dL, very high
DEFAULT_TARGET = {"low": 70, "high": 180}  # VERIFY mg/dL
NEW_CHAPTER_WINDOW_DAYS = 14
ADHERENCE_LOW = 70  # VERIFY percent below which missed doses count as a confounder
MAX_IMPORT_BYTES = 1_000_000
MAX_LOGS = 5000
TIER_CAPS = {"this_week": 1, "next_visit": 2}  # VERIFY
TIER_LABELS = {
    "emergency": {"en": "Emergency", "bn": "জরুরি"},
    "this_week": {"en": "See your doctor this week", "bn": "এই সপ্তাহে ডাক্তার দেখান"},
    "next_visit": {"en": "Raise at your next visit", "bn": "পরের ভিজিটে বলুন"},
    "self_care": {"en": "Self-care", "bn": "নিজের যত্ন"},
}
TEST_INTERVALS = {"hba1c": 90, "eye": 365, "kidney": 365, "foot": 365,
                  "lipid": 365, "bp": 30, "doctor_visit": 90}  # VERIFY days
SPECIALISTS = {
    "foot": {"en": "a foot care specialist", "bn": "পায়ের যত্নের বিশেষজ্ঞ"},
    "eye": {"en": "an eye doctor", "bn": "চোখের ডাক্তার"},
    "kidney": {"en": "a kidney specialist", "bn": "কিডনি বিশেষজ্ঞ"},
    "nerve": {"en": "a nerve specialist", "bn": "স্নায়ু বিশেষজ্ঞ"},
    "heart": {"en": "a heart specialist", "bn": "হৃদরোগ বিশেষজ্ঞ"},
    "endocrine": {"en": "a diabetes specialist", "bn": "ডায়াবেটিস বিশেষজ্ঞ"},
}
MED_NAMES = {  # lowercase drug name or medicine class -> {en, bn}
    "metformin": {"en": "Metformin", "bn": "মেটফরমিন"},
    "glimepiride": {"en": "Glimepiride", "bn": "গ্লিমিপিরাইড"},
    "gliclazide": {"en": "Gliclazide", "bn": "গ্লিক্লাজাইড"},
    "glibenclamide": {"en": "Glibenclamide", "bn": "গ্লিবেনক্লামাইড"},
    "empagliflozin": {"en": "Empagliflozin", "bn": "এম্পাগ্লিফ্লোজিন"},
    "dapagliflozin": {"en": "Dapagliflozin", "bn": "ড্যাপাগ্লিফ্লোজিন"},
    "sitagliptin": {"en": "Sitagliptin", "bn": "সিটাগ্লিপটিন"},
    "linagliptin": {"en": "Linagliptin", "bn": "লিনাগ্লিপটিন"},
    "insulin": {"en": "Insulin", "bn": "ইনসুলিন"},
    "insulin glargine": {"en": "Insulin glargine", "bn": "ইনসুলিন গ্লারজিন"},
    "insulin aspart": {"en": "Insulin aspart", "bn": "ইনসুলিন অ্যাসপার্ট"},
    "sulfonylurea": {"en": "Sulfonylurea tablet", "bn": "সালফোনাইলইউরিয়া ট্যাবলেট"},
    "sglt2": {"en": "SGLT2 tablet", "bn": "এসজিএলটি-টু ট্যাবলেট"},
    "dpp4": {"en": "DPP-4 tablet", "bn": "ডিপিপি-ফোর ট্যাবলেট"},
    "insulin_basal": {"en": "Long-acting insulin", "bn": "দীর্ঘস্থায়ী ইনসুলিন"},
    "insulin_rapid": {"en": "Fast-acting insulin", "bn": "দ্রুত কার্যকর ইনসুলিন"},
    "insulin_mix": {"en": "Mixed insulin", "bn": "মিক্সড ইনসুলিন"},
    "other": {"en": "Other medicine", "bn": "অন্য ওষুধ"},
}

_BD = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
DISCLAIMER = {
    "en": f"Prototype. Not clinically validated and not a substitute for a doctor. "
          f"Your data stays in this session only. Emergency: call {EMERGENCY_NUMBER}.",
    "bn": f"এটি একটি প্রোটোটাইপ। ক্লিনিক্যালি যাচাই করা হয়নি এবং ডাক্তারের বিকল্প নয়। "
          f"আপনার তথ্য শুধু এই সেশনে থাকে। জরুরি অবস্থায় {EMERGENCY_NUMBER.translate(_BD)} নম্বরে ফোন করুন।",
}
_MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "bn": ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
           "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"],
}
LOG_TYPES = {"glucose", "food", "med", "water", "exercise", "energy",
             "mood", "symptom", "concern", "test", "checkin"}
_SEX = {"male", "female", "other"}
_DTYPE = {"type1", "type2", "gestational", "prediabetes", "unsure"}
_MEDCLS = {"metformin", "sulfonylurea", "sglt2", "dpp4",
           "insulin_basal", "insulin_rapid", "insulin_mix", "other"}


# ---------------------------------------------------------------- i18n
def lang():
    return st.session_state.get("lang") or "en"


def set_lang(code):
    if code in LANGS:
        st.session_state["lang"] = code


def L(x):
    if isinstance(x, dict):
        return x.get(lang()) or x.get("en") or ""
    return "" if x is None else x


def LL(items):
    return [L(i) for i in items or []]


def num(x):
    if isinstance(x, float):
        x = round(x, 1)
        x = int(x) if x == int(x) else x
    s = str(x)
    return s.translate(_BD) if lang() == "bn" else s


def to_date(iso):
    return date.fromisoformat(str(iso)[:10])


def fmt_date(iso):
    try:
        d = to_date(iso)
    except ValueError:
        return str(iso or "")
    return f"{num(d.day)} {_MONTHS[lang()][d.month - 1]} {num(d.year)}"


def med_label(name):
    """Drug name or class -> display text (Bangla script in bn when known)."""
    m = MED_NAMES.get(str(name or "").strip().lower())
    return L(m) if m else str(name or "")


# ---------------------------------------------------------------- time
def now():
    return datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None)  # Bangladesh, naive


def today():
    return now().date()


def _ts(e):
    return datetime.fromisoformat(e["ts"]).replace(tzinfo=None)


# ---------------------------------------------------------------- state
def blank_profile():
    return {"schema_version": 1, "name": "", "age": 40, "sex": "other", "diabetes_type": "type2",
            "diagnosed_year": None, "medicines": [], "allergies": [], "conditions": [],
            "other_history": "", "units": "mgdl", "target_range": dict(DEFAULT_TARGET),
            "fluid_limit": False, "water_target": None, "fasting_now": False,
            "care_person": None, "doctor_plan": None}


def init_state():
    defaults = {"lang": None, "profile": None, "logs": [], "due": [], "seen_content": {},
                "symptom_session": {}, "report_cache": None, "view": "dashboard", "gemma_cache": {}}
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def P():
    return st.session_state.get("profile") or {}


def set_profile(d):
    st.session_state["profile"] = {**blank_profile(), **d, "schema_version": 1}
    st.session_state["report_cache"] = None


def logs(type=None, days=None):
    out = st.session_state.get("logs", [])
    if type:
        out = [e for e in out if e.get("type") == type]
    if days is not None:
        cut = now() - timedelta(days=days)
        out = [e for e in out if _ts(e) >= cut]
    return sorted(out, key=_ts)


def add_log(type, **fields):
    e = {"ts": now().isoformat(timespec="seconds"), "type": type, **fields}
    st.session_state["logs"].append(e)
    st.session_state["report_cache"] = None
    return e


def mark_seen(ids):
    s = st.session_state["seen_content"]
    for i in ids:
        s[i] = today().isoformat()


def seen():
    return st.session_state.get("seen_content", {})


def go(view):
    st.session_state["view"] = view


def export_json():
    s = st.session_state
    return json.dumps({"schema_version": 1, "exported": now().isoformat(timespec="seconds"),
                       "profile": s.get("profile"), "logs": s.get("logs", []), "due": s.get("due", []),
                       "seen_content": s.get("seen_content", {}),
                       "symptom_session": s.get("symptom_session", {})},
                      ensure_ascii=False, indent=1)


def _iso_ok(s):
    try:
        datetime.fromisoformat(s)
        return isinstance(s, str)
    except (TypeError, ValueError):
        return False


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _profile_ok(p):
    if not isinstance(p, dict) or not isinstance(p.get("name"), str):
        return False
    age = p.get("age")
    if not (isinstance(age, int) and not isinstance(age, bool) and 0 < age < 130):
        return False
    if p.get("sex") not in _SEX or p.get("diabetes_type") not in _DTYPE:
        return False
    if p.get("units") not in ("mgdl", "mmol"):
        return False
    t = p.get("target_range")
    if not (isinstance(t, dict) and _num(t.get("low")) and _num(t.get("high")) and t["low"] < t["high"]) and 18 <= t["low"] < t["high"] <= 600):  
        return False
    meds = p.get("medicines", [])
    if not (isinstance(meds, list) and all(
            isinstance(m, dict) and isinstance(m.get("name"), str) and m.get("cls") in _MEDCLS for m in meds)):
        return False
    for k in ("allergies", "conditions"):
        v = p.get(k, [])
        if not (isinstance(v, list) and all(isinstance(i, str) for i in v)):
            return False
    cp = p.get("care_person")
    return cp is None or (isinstance(cp, dict) and isinstance(cp.get("phone"), str))


def import_json(text):
    def bad(en, bn):
        return False, L({"en": en, "bn": bn})
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_IMPORT_BYTES:
        return bad("This file is too big or not text.", "ফাইলটি অনেক বড় অথবা লেখা নয়।")
    try:
        d = json.loads(text)
    except ValueError:
        return bad("This is not a valid profile file.", "এটি সঠিক প্রোফাইল ফাইল নয়।")
    if not isinstance(d, dict) or d.get("schema_version") != 1:
        return bad("This file version is not supported.", "এই ফাইলের সংস্করণ চলবে না।")
    if not _profile_ok(d.get("profile")):
        return bad("The profile in this file looks incomplete.", "ফাইলের প্রোফাইলে তথ্য ঠিক নেই।")
    lg, due = d.get("logs", []), d.get("due", [])
    if not (isinstance(lg, list) and len(lg) <= MAX_LOGS and all(
            isinstance(e, dict) and e.get("type") in LOG_TYPES and _iso_ok(e.get("ts")) for e in lg)):
        return bad("The records in this file look wrong.", "ফাইলের রেকর্ডগুলো ঠিক নেই।")
    if not (isinstance(due, list) and len(due) <= 200 and all(
            isinstance(i, dict) and isinstance(i.get("id"), str) and i.get("key") in TEST_INTERVALS
            and _iso_ok(i.get("due")) for i in due)):
        return bad("The reminders in this file look wrong.", "ফাইলের রিমাইন্ডারগুলো ঠিক নেই।")
    s = st.session_state
    set_profile(d["profile"])
    s["logs"], s["due"] = lg, due
    sc, ss = d.get("seen_content"), d.get("symptom_session")
    s["seen_content"] = sc if isinstance(sc, dict) else {}
    s["symptom_session"] = ss if isinstance(ss, dict) else {}
    s["report_cache"], s["view"] = None, "dashboard"
    return True, L({"en": "Profile loaded.", "bn": "প্রোফাইল লোড হয়েছে।"})


def load_demo(key):
    from data_misc import DEMOS  # lazy: data_misc imports base
    d = DEMOS[key]()
    s = st.session_state
    s["profile"] = None
    if d.get("profile"):
        set_profile(d["profile"])
    s["logs"], s["due"] = list(d.get("logs", [])), list(d.get("due", []))
    s["seen_content"], s["symptom_session"] = {}, {}
    s["report_cache"], s["gemma_cache"], s["view"] = None, {}, "dashboard"


def reset():
    keep = st.session_state.get("lang")
    st.session_state.clear()
    init_state()
    st.session_state["lang"] = keep


# ---------------------------------------------------------------- rules
def to_mgdl(v, unit):
    return float(v) * MGDL_PER_MMOL if unit == "mmol" else float(v)


def from_mgdl(v, unit):
    return round(float(v) / MGDL_PER_MMOL, 1) if unit == "mmol" else round(float(v))


def fmt_glucose(mgdl):
    unit = P().get("units", "mgdl")
    return f"{num(from_mgdl(mgdl, unit))} {'mmol/L' if unit == 'mmol' else 'mg/dL'}"


def _target():
    return P().get("target_range") or DEFAULT_TARGET


def classify_glucose(mgdl):
    v = float(mgdl)
    if v < HYPO_L2:
        return "severe_low"
    if v < HYPO_L1:
        return "low"
    if v >= VERY_HIGH:
        return "very_high"
    return "high" if v > _target()["high"] else "in_range"


def latest_glucose():
    g = logs("glucose")
    return g[-1] if g else None


def glucose_summary(days):
    vals = [e["value_mgdl"] for e in logs("glucose", days) if _num(e.get("value_mgdl"))]
    n = len(vals)
    if not n:
        return {"avg": None, "tir_pct": None, "lows": 0, "highs": 0, "n": 0}
    t = _target()
    tir = sum(1 for v in vals if t["low"] <= v <= t["high"])
    return {"avg": round(sum(vals) / n, 1), "tir_pct": round(100 * tir / n),
            "lows": sum(1 for v in vals if v < HYPO_L1),
            "highs": sum(1 for v in vals if v > t["high"]), "n": n}


def night_lows(days):
    return sum(1 for e in logs("glucose", days)
               if _num(e.get("value_mgdl")) and e["value_mgdl"] < HYPO_L1
               and (e.get("context") in ("night", "bedtime") or _ts(e).hour < 6))


def adherence(med_name, days):
    """Percent (0-100) of logged doses taken for this medicine; None if nothing logged."""
    rows = [e for e in logs("med", days) if str(e.get("name", "")).lower() == str(med_name).lower()]
    if not rows:
        return None
    return 100.0 * sum(1 for e in rows if e.get("taken")) / len(rows)


def confounders_active():
    """Keys: fasting, missed_doses, new_medicine, steroids (match CONFOUNDERS in content_learn)."""
    p, out = P(), []
    if p.get("fasting_now"):
        out.append("fasting")
    meds = p.get("medicines", [])
    if any((a := adherence(m.get("name", ""), 7)) is not None and a < ADHERENCE_LOW for m in meds):
        out.append("missed_doses")
    cut = today() - timedelta(days=30)  # VERIFY
    for m in meds:
        try:
            if m.get("start_date") and to_date(m["start_date"]) >= cut:
                out.append("new_medicine")
                break
        except ValueError:
            pass
    blob = (p.get("other_history", "") + " " + " ".join(m.get("name", "") for m in meds)).lower()
    if re.search(r"steroid|prednis|dexameth|স্টেরয়েড|প্রেডনিসোলন", blob):
        out.append("steroids")
    return out


def water_today():
    t = today().isoformat()
    return sum(int(e.get("glasses", 0)) for e in logs("water") if e["ts"][:10] == t)
