"""Triage + reminders + red flags. Deterministic rules only (no Gemma). Imports base, content_q, content_learn."""
import re
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote

import streamlit as st

from base import (ADHERENCE_LOW, DEFAULT_TARGET, L, P, TEST_INTERVALS, TIER_CAPS, add_log, adherence,
                  classify_glucose, confounders_active, glucose_summary, latest_glucose, logs,
                  night_lows, now, to_date, today)
from content_learn import CONFOUNDERS
from content_q import CUTS, DURATION_DAYS, QMODULES, REDFLAG_OPTIONS, SCALE_WEIGHTS

_BN = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def T(en, bn):
    return {"en": en, "bn": bn}


def _n(x):
    return str(x).translate(_BN)


def _isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ================================================================ triage
TIERS = ["self_care", "next_visit", "this_week"]  # low -> high
WINDOW_DAYS = 14  # VERIFY days of symptom logs considered
TREND_DELTA = 1.0  # VERIFY severity change that counts as worse or better
NUMB_IDS = {"numb", "loss_hot", "loss_pebble"}  # option ids meaning loss of feeling
OPT_CONF = {"oc_b12": "b12_metformin", "oc_alcohol": "alcohol", "oc_illness": "illness",
            "ill_sick": "illness", "ill_med": "new_medicine"}
NO_DEMOTE = {"b12_metformin"}  # VERIFY listed as a reason, but never lowers a tier
POSSIBLE = {"foot": ["alcohol", "illness"], "night": ["alcohol", "exercise", "fasting", "poor_sleep"],
            "thirst": ["illness", "steroids", "feast_day", "stress", "meter"]}
B12_Q = T("Should my vitamin B12 level be tested?", "আমার ভিটামিন বি-১২ পরীক্ষা করা দরকার কি?")
MODULE_QS = {
    "foot": [T("Should my feet be checked for nerve damage or poor blood flow?",
               "আমার পায়ে স্নায়ুর ক্ষতি বা রক্তসঞ্চালনের সমস্যা আছে কিনা দেখা দরকার কি?"),
             T("Which shoes and foot care do you advise for me?", "আমার জন্য কোন জুতা ও পায়ের যত্ন ভালো?")],
    "night": [T("Could my evening medicine or meal timing be linked to night-time lows?",
                "রাতের ওষুধ বা খাবারের সময় কি রাতে সুগার কমার সাথে যুক্ত হতে পারে?")],
    "thirst": [T("Do these readings and symptoms mean my plan needs a review?",
                 "এই মাপ ও উপসর্গ দেখে কি আমার পরিকল্পনা আবার দেখা দরকার?")],
}
QUESTION_PACK = {  # keys match profile.doctor_plan (low_sugar is added by the doctor-visit form)
    "missed_meal": T("What should I do with my medicine if I miss a meal?", "খাবার বাদ পড়লে আমার ওষুধ নিয়ে কী করব?"),
    "small_meal": T("What should I do if I eat much less than usual?", "স্বাভাবিকের চেয়ে অনেক কম খেলে কী করব?"),
    "sick_day": T("What is my plan for days when I am sick and cannot eat?",
                  "অসুস্থ হয়ে খেতে না পারলে আমার পরিকল্পনা কী?"),
    "exercise": T("What should I do before and after exercise?", "ব্যায়ামের আগে ও পরে কী করব?"),
    "bedtime": T("What should I do if my sugar is low at bedtime?", "ঘুমের আগে সুগার কম থাকলে কী করব?"),
    "checks": T("Do I need a foot, eye or kidney check this year?", "এ বছর কি আমার পা, চোখ বা কিডনি পরীক্ষা করা দরকার?"),
}
_WEIGHT = re.compile(r"weight loss|lost weight|losing weight|ওজন কম")


def _sev(e):
    v = e.get("severity")
    return float(v) if _isnum(v) else 0.0


def _sym_rows(key):
    return [e for e in logs("symptom", WINDOW_DAYS) if e.get("module") == key and _sev(e) > 0]


def _shift(tier, d):
    return TIERS[max(0, min(2, TIERS.index(tier) + d))]


def _chosen(m, answers):
    """[(question, option)] for answers that match a defined option id."""
    return [(q, o) for q in m["questions"] for o in q["options"] if o["id"] == answers.get(q["id"])]


def _scale_vals(m, answers):
    out = {}
    for q in m["questions"]:
        if q["type"] == "scale":
            try:
                out[q["id"]] = max(0, min(10, int(answers.get(q["id"]))))
            except (TypeError, ValueError):
                pass
    return out


def _scale_weight(v):
    return next((w for lo, w in SCALE_WEIGHTS if v >= lo), 0)


def _trend(key):
    sev = [_sev(e) for e in _sym_rows(key)]
    if len(sev) >= 4:
        h = len(sev) // 2
        d = sum(sev[h:]) / (len(sev) - h) - sum(sev[:h]) / h
        return "worse" if d >= TREND_DELTA else "better" if d <= -TREND_DELTA else "same"
    c = [e.get("status") for e in logs("concern") if e.get("key") == key]
    return c[-1] if c and c[-1] in ("better", "same", "worse") else "unknown"


def _worse_streak(key):
    c = [e.get("status") for e in logs("concern") if e.get("key") == key][-3:]
    return len(c) == 3 and all(s == "worse" for s in c)


def _metformin():
    for m in P().get("medicines", []):
        n = str(m.get("name", "")).lower()
        if m.get("cls") == "metformin" or "metformin" in n or "মেটফরমিন" in n:
            return m
    return None


def _b12(key, answers):
    """Numbness or tingling plus metformin for 12 months or more."""
    if key != "foot":
        return False
    numb = (answers.get("f_type") in ("tingle", "numb") or answers.get("f_loss") in ("loss_hot", "loss_pebble")
            or any(e.get("numbness") for e in logs("symptom", WINDOW_DAYS) if e.get("module") == "foot"))
    m = _metformin()
    try:
        return bool(numb and m and m.get("start_date")
                    and to_date(m["start_date"]) <= today() - timedelta(days=365))  # VERIFY
    except ValueError:
        return False


def _eval(key, answers):
    """Returns (ReportItem, score) for one module."""
    m = QMODULES[key]
    chosen, scales = _chosen(m, answers), _scale_vals(m, answers)
    score = sum(o["weight"] for _, o in chosen) + sum(_scale_weight(v) for v in scales.values())
    signals = sum(1 for _, o in chosen if o["signal"])
    ld = len({e["ts"][:10] for e in _sym_rows(key)})
    # night has no scale question, so night/bedtime lows in the glucose log count as present days
    days = max(ld, DURATION_DAYS.get(answers.get("duration"), 0), night_lows(WINDOW_DAYS) if key == "night" else 0)
    cut = CUTS[key]
    fast = any(o["id"] in m["fast_track"] for _, o in chosen)
    conf = list(confounders_active()) + [OPT_CONF[o["id"]] for _, o in chosen if o["id"] in OPT_CONF]
    b12 = _b12(key, answers)
    if b12:
        conf.append("b12_metformin")
    conf = list(dict.fromkeys(c for c in conf if c in CONFOUNDERS))
    active = [c for c in conf if c not in NO_DEMOTE]
    if fast or (signals >= 2 and days >= m["min_days"]):
        tier = "this_week"
    elif signals >= 1 or score >= cut["low"]:
        tier = "next_visit"
    else:
        tier = "self_care"
    # one demotion for active confounders; fast-track (wound, skin change) is exempt  # VERIFY
    if active and not fast and not (tier == "this_week" and score >= cut["high"]):
        tier = _shift(tier, -1)
    if _worse_streak(key):
        tier = _shift(tier, 1)
    why = sorted((x for x in chosen if x[1]["signal"] or x[1]["weight"] > 0),
                 key=lambda x: (not x[1]["signal"], -x[1]["weight"]))
    reasons = [T(f"{q['text']['en']} {o['label']['en']}", f"{q['text']['bn']} {o['label']['bn']}")
               for q, o in why][:6]
    sv = [v for v in scales.values() if v > 0]
    for v in sv:
        reasons.append(T(f"Strength you reported: {v} out of 10", f"আপনার জানানো তীব্রতা: ১০ এর মধ্যে {_n(v)}"))
    if ld:
        reasons.append(T(f"You logged this on {ld} of the last {WINDOW_DAYS} days.",
                         f"গত {_n(WINDOW_DAYS)} দিনের মধ্যে আপনি {_n(ld)} দিন এটি লিখেছেন।"))
    sev = [_sev(e) for e in _sym_rows(key)] or [float(v) for v in sv]
    item = {"module": key, "tier": tier, "title": m["title"], "reasons": reasons, "present_days": days,
            "avg_severity": round(sum(sev) / len(sev), 1) if sev else None, "trend": _trend(key),
            "confounders": conf + [c for c in POSSIBLE.get(key, []) if c not in conf],
            "specialist": m["specialist"] if tier == "this_week" else None,
            "questions": ([B12_Q] if b12 else []) + MODULE_QS.get(key, [])}
    return item, score


def _triage(answers):
    """Returns (items, other_noted) with caps applied. Triage never produces an emergency."""
    ev = sorted((_eval(k, a if isinstance(a, dict) else {}) for k, a in answers.items() if k in QMODULES),
                key=lambda t: (-TIERS.index(t[0]["tier"]), -t[1], -t[0]["present_days"]))
    items, other, nw, nn = [], [], 0, 0
    for it, _ in ev:
        if it["tier"] == "this_week":
            if nw < TIER_CAPS["this_week"]:
                nw += 1
            else:  # extra this_week item steps down one tier and competes for a next_visit slot
                it = {**it, "tier": "next_visit", "specialist": None}
        if it["tier"] == "next_visit":
            if nn >= TIER_CAPS["next_visit"]:
                other.append(T(f"You noted: {it['title']['en']}", f"আপনি জানিয়েছেন: {it['title']['bn']}"))
                continue
            nn += 1
        items.append(it)
    return items, other


def triage_answers(answers):
    return _triage(answers)[0]


def save_answers(module, answers):
    m = QMODULES.get(module)
    if not m or not isinstance(answers, dict):
        return
    ss = st.session_state.setdefault("symptom_session", {})
    ss.setdefault("answers", {})[module] = dict(answers)
    ss["updated"] = now().isoformat(timespec="seconds")
    k, v = next(iter(_scale_vals(m, answers).items()), (module, 0))
    numb = any(o["id"] in NUMB_IDS for _, o in _chosen(m, answers))
    add_log("symptom", module=module, key=k, severity=v, numbness=numb, note="")
    st.session_state["report_cache"] = None


def note_other(text):
    """Save an unmapped 'Other' answer verbatim for the neutral 'Other things you noted' list."""
    t = " ".join(str(text or "").split())[:200]
    if t:
        ss = st.session_state.setdefault("symptom_session", {})
        ss.setdefault("other_noted", []).append(t)
        ss["other_noted"] = ss["other_noted"][-30:]
        st.session_state["report_cache"] = None


def route_group(module, answers):
    """Red-flag group to open first when a chosen option needs it (e.g. vomiting), else None."""
    vals = {str(v) for v in (answers or {}).values()}
    return "high_emergency" if any(o in vals for o in REDFLAG_OPTIONS.get(module, [])) else None


def _kw(text, words):
    t = " ".join(str(text or "").lower().split())
    return sum(1 for w in words if (re.search(r"\b" + re.escape(w) + r"\b", t) if w.isascii() else w in t))


def module_for_text(text):
    """Keyword fallback. None when nothing matches or two modules tie."""
    sc = sorted(((_kw(text, m["keywords"]["en"] + m["keywords"]["bn"]), k) for k, m in QMODULES.items()),
                reverse=True)
    return sc[0][1] if sc[0][0] and (len(sc) == 1 or sc[0][0] > sc[1][0]) else None


def _med_notes(ans):
    notes, qs = [], []
    met = _metformin()
    if met:
        fast = [e for e in logs("glucose") if e.get("context") == "fasting" and _isnum(e.get("value_mgdl"))]
        if len(fast) >= 14 and (to_date(fast[-1]["ts"]) - to_date(fast[0]["ts"])).days >= 28:  # VERIFY
            ad, t = adherence(met.get("name", ""), 28), today()
            rec = [e["value_mgdl"] for e in fast if to_date(e["ts"]) > t - timedelta(days=14)]
            old = [e["value_mgdl"] for e in fast if t - timedelta(days=28) < to_date(e["ts"]) <= t - timedelta(days=14)]
            if rec and ad is not None and ad >= ADHERENCE_LOW:  # VERIFY
                avg = sum(rec) / len(rec)
                down = bool(old) and avg < sum(old) / len(old) - 5  # VERIFY mg/dL fall that counts as improving
                if avg > (P().get("target_range") or DEFAULT_TARGET)["high"] and not down:
                    notes.append(T(
                        "Your readings have not changed much while you logged most doses. This can have many "
                        "causes. Worth asking your doctor whether your plan needs a review.",
                        "আপনি বেশিরভাগ ডোজ নেওয়ার কথা লিখেছেন, অথচ সুগারের মাপ প্রায় একই আছে। এর অনেক কারণ থাকতে পারে। "
                        "আপনার পরিকল্পনা আবার দেখা দরকার কি না, ডাক্তারকে জিজ্ঞাসা করা ভালো।"))
                    qs.append(T("Does my medicine plan need a review?", "আমার ওষুধের পরিকল্পনা কি আরেকবার দেখা দরকার?"))
    if (ans.get("thirst") or {}).get("t_nv") in ("nv_nausea", "nv_vomit") and "new_medicine" in confounders_active():
        qs.append(T("I have had stomach upset since my medicine changed. Could they be linked?",
                    "ওষুধ বদলানোর পর থেকে আমার পেটের অস্বস্তি হচ্ছে। এ দুটি কি সম্পর্কিত হতে পারে?"))
    blob = " ".join(str(x) for x in (st.session_state.get("symptom_session") or {}).get("other_noted", []))
    blob += " " + " ".join(str(e.get("text", "")) for e in logs("checkin"))
    if _WEIGHT.search(blob.lower()):
        qs.append(T("I have lost weight without trying. Could my diabetes or medicine be a reason?",
                    "আমি চেষ্টা না করেই ওজন কমে যাচ্ছে। এর কারণ কি আমার ডায়াবেটিস বা ওষুধ হতে পারে?"))
    return notes, qs


def build_report():
    if st.session_state.get("report_cache"):
        return st.session_state["report_cache"]
    ss = st.session_state.get("symptom_session") or {}
    ans = dict(ss.get("answers") or {})
    for e in logs("symptom", WINDOW_DAYS):  # modules only logged (e.g. demo data) still appear
        if e.get("module") in QMODULES and _sev(e) > 0:
            ans.setdefault(e["module"], {})
    items, other = _triage(ans)
    other += [T(str(s)[:200], str(s)[:200]) for s in (ss.get("other_noted") or []) if str(s).strip()]
    notes, mq = _med_notes(ans)
    seen, dq = set(), []
    for q in [q for it in items for q in it["questions"]] + mq + list(QUESTION_PACK.values()):
        if q["en"] not in seen:
            seen.add(q["en"])
            dq.append(q)
    b = buckets()
    r = {"generated": now().isoformat(timespec="seconds"), "items": items, "other_noted": other,
         "doctor_questions": dq, "med_notes": notes,
         "tests_due": [{**i, "bucket": k} for k in ("overdue", "today", "week") for i in b[k]],
         "glucose_summary": glucose_summary(14)}
    st.session_state["report_cache"] = r
    return r


# ================================================================ reminders
TESTS = {
    "hba1c": {"title": T("HbA1c blood test", "এইচবিএ১সি রক্তপরীক্ষা"), "unit": "%", "result": T("Result (%)", "ফলাফল (%)")},
    "eye": {"title": T("Eye exam", "চোখ পরীক্ষা"), "unit": "", "result": None},
    "kidney": {"title": T("Kidney tests (urine and blood)", "কিডনি পরীক্ষা (প্রস্রাব ও রক্ত)"), "unit": "mg/dL",
               "result": T("Creatinine result (mg/dL)", "ক্রিয়েটিনিনের ফলাফল (mg/dL)")},  # VERIFY unit
    "foot": {"title": T("Foot check by a doctor", "ডাক্তারের কাছে পা পরীক্ষা"), "unit": "", "result": None},
    "lipid": {"title": T("Cholesterol test", "কোলেস্টেরল পরীক্ষা"), "unit": "mg/dL",
              "result": T("Total cholesterol (mg/dL)", "মোট কোলেস্টেরল (mg/dL)")},  # VERIFY unit
    "bp": {"title": T("Blood pressure check", "রক্তচাপ মাপা"), "unit": "mmHg",
           "result": T("Top number (mmHg)", "উপরের সংখ্যা (mmHg)")},
    "doctor_visit": {"title": T("Doctor visit", "ডাক্তার দেখানো"), "unit": "", "result": None},
}
REMINDER_NOTE = T("Your doctor may set a different schedule.", "আপনার ডাক্তার অন্য সময়সূচি দিতে পারেন।")
DEFAULT_OFFSETS = {"hba1c": 7, "foot": 14, "bp": 7, "eye": 30, "kidney": 30, "lipid": 60}  # VERIFY days to first reminder


def add_due(key, due_date, interval=None):
    if key not in TEST_INTERVALS:
        return None
    d = str(due_date.isoformat() if hasattr(due_date, "isoformat") else due_date)[:10]
    try:
        to_date(d)
        iv = int(interval or TEST_INTERVALS[key])
    except (TypeError, ValueError):
        return None
    item = {"id": f"{key}-{uuid.uuid4().hex[:8]}", "key": key, "due": d, "done": None, "interval_days": iv}
    st.session_state.setdefault("due", []).append(item)
    st.session_state["report_cache"] = None
    return item


def ensure_defaults():
    have = {i.get("key") for i in st.session_state.get("due", []) if not i.get("done")}
    for k, off in DEFAULT_OFFSETS.items():
        if k not in have:
            add_due(k, today() + timedelta(days=off))


def buckets():
    t, out = today(), {"overdue": [], "today": [], "week": [], "later": []}
    for i in sorted((i for i in st.session_state.get("due", []) if not i.get("done")), key=lambda i: i["due"]):
        d = (to_date(i["due"]) - t).days
        out["overdue" if d < 0 else "today" if d == 0 else "week" if d <= 7 else "later"].append(i)
    return out


def mark_done(id, result=None):
    for i in st.session_state.get("due", []):
        if i.get("id") == id and not i.get("done"):
            i["done"], k = now().isoformat(timespec="seconds"), i["key"]
            if result not in (None, "") and TESTS.get(k, {}).get("result"):
                try:
                    add_log("test", key=k, value=float(result), unit=TESTS[k]["unit"])
                except (TypeError, ValueError):
                    pass
            if k != "doctor_visit":  # the next visit date is set by the doctor-visit form
                iv = int(i.get("interval_days") or TEST_INTERVALS[k])
                add_due(k, today() + timedelta(days=iv), iv)
            st.session_state["report_cache"] = None
            return True
    return False


# ================================================================ red flags
def _I(i, en, bn):
    return {"id": i, "text": T(en, bn)}


GROUPS = {  # rule "any": one item is enough; "two": 2+ items, or 1 plus a very high/low glucose today
    "cardiac": {"title": T("Heart signs", "হৃদয়ের লক্ষণ"), "rule": "any", "items": [
        _I("c_chest", "Pressure, squeezing or tightness in the chest", "বুকে চাপ, চেপে ধরা বা ভার লাগা"),
        _I("c_pain", "Pain in the jaw, arm or back", "চোয়াল, হাত বা পিঠে ব্যথা"),
        _I("c_breath", "Short of breath", "শ্বাসকষ্ট বা হাঁপিয়ে ওঠা"),
        _I("c_sweat", "Cold sweat", "ঠান্ডা ঘাম"),
        _I("c_nausea", "Feeling sick or vomiting", "বমি বমি ভাব বা বমি"),
        _I("c_tired", "Unusual tiredness or weakness", "অস্বাভাবিক ক্লান্তি বা দুর্বলতা")]},
    "stroke": {"title": T("Stroke signs", "স্ট্রোকের লক্ষণ"), "rule": "any", "items": [
        _I("s_balance", "Sudden loss of balance or dizziness", "হঠাৎ ভারসাম্য হারানো বা মাথা ঘোরা"),
        _I("s_eyes", "Sudden trouble seeing", "হঠাৎ দেখতে অসুবিধা"),
        _I("s_face", "One side of the face drooping", "মুখের এক পাশ ঝুলে পড়া"),
        _I("s_arm", "Weakness in one arm or leg", "এক হাত বা পায়ে দুর্বলতা"),
        _I("s_speech", "Slurred speech or trouble speaking", "কথা জড়িয়ে যাওয়া বা বলতে অসুবিধা"),
        _I("s_time", "These signs started suddenly, in the last few hours",
           "এই লক্ষণ হঠাৎ, গত কয়েক ঘণ্টার মধ্যে শুরু হয়েছে")]},
    "severe_low": {"title": T("Very low sugar signs", "খুব কম সুগারের লক্ষণ"), "rule": "any", "items": [
        _I("sl_confused", "Confused or cannot think clearly", "বিভ্রান্ত বা পরিষ্কার ভাবতে পারছেন না"),
        _I("sl_swallow", "Cannot swallow or drink safely", "নিরাপদে গিলতে বা পান করতে পারছেন না"),
        _I("sl_seizure", "A fit or seizure", "খিঁচুনি"),
        _I("sl_faint", "Fainted or cannot be woken", "অজ্ঞান বা জাগানো যাচ্ছে না")]},
    "high_emergency": {"title": T("Very high sugar signs", "খুব বেশি সুগারের লক্ষণ"), "rule": "two", "items": [
        _I("h_vomit", "Vomiting, with high sugar", "বেশি সুগারের সাথে বমি"),
        _I("h_fruity", "Breath smells fruity", "নিঃশ্বাসে ফলের মতো গন্ধ"),
        _I("h_deep", "Fast, deep breathing", "দ্রুত ও গভীর শ্বাস"),
        _I("h_drowsy", "Very sleepy or hard to wake", "খুব ঘুম ঘুম ভাব বা জাগতে কষ্ট")]},
    "foot_emergency": {"title": T("Serious foot signs", "পায়ের গুরুতর লক্ষণ"), "rule": "two", "items": [
        _I("fe_red", "Redness spreading up the foot or leg", "পা বা পায়ের ওপরের দিকে ছড়িয়ে পড়া লালচে ভাব"),
        _I("fe_fever", "Fever with a foot wound", "পায়ে ঘা থাকার সাথে জ্বর"),
        _I("fe_black", "Black or very dark skin on the foot or a toe", "পা বা আঙুলের চামড়া কালো বা খুব কালচে"),
        _I("fe_pus", "Pus or a bad smell from a wound", "ক্ষত থেকে পুঁজ বা দুর্গন্ধ")]},
}
_EMERG = ["chest pain", "pain in my chest", "chest pressure", "chest tight", "tight chest", "heart attack",
          "stroke", "face droop", "slurred", "can't speak", "cannot speak", "unconscious", "passed out",
          "seizure", "can't breathe", "cannot breathe",
          "বুকে ব্যথা", "বুকে ব্যাথা", "বুক ব্যথা", "বুকে চাপ", "বুক চেপে", "হার্ট অ্যাটাক", "হার্টঅ্যাটাক",
          "স্ট্রোক", "মুখ বেঁকে", "কথা জড়িয়ে", "কথা বলতে পারছি না", "অজ্ঞান", "খিঁচুনি", "শ্বাস নিতে পারছি না"]
_SELF = ["suicide", "kill myself", "end my life", "want to die", "hurt myself", "harm myself", "self-harm",
         "self harm", "আত্মহত্যা", "মরে যেতে চাই", "মরতে চাই", "নিজেকে শেষ", "নিজেকে আঘাত"]


def screen_items(group=None):
    gs = [group] if group in GROUPS else list(GROUPS)
    return [{"id": i["id"], "group": g, "text": i["text"]} for g in gs for i in GROUPS[g]["items"]]


def _extreme_glucose():
    g = latest_glucose()
    if not g or not _isnum(g.get("value_mgdl")):
        return False
    try:
        age = now() - datetime.fromisoformat(g["ts"]).replace(tzinfo=None)
    except ValueError:
        return False
    return age.total_seconds() < 86400 and classify_glucose(g["value_mgdl"]) in ("very_high", "severe_low")  # VERIFY 24 h


def check_flags(selected_ids):
    sel, extreme, hit = set(selected_ids or []), _extreme_glucose(), []
    for g, d in GROUPS.items():
        n = sum(1 for i in d["items"] if i["id"] in sel)
        if n and (d["rule"] == "any" or n >= 2 or extreme):
            hit.append(g)
    return {"level": "emergency" if hit else "none", "groups": hit}


def _norm(text):
    return " ".join(str(text or "").lower().replace("\u2019", "'").split())


def selfharm_text(text):
    t = _norm(text)
    return any(w in t for w in _SELF)


def text_triggers(text):
    t = _norm(text)
    return any(w in t for w in _EMERG) or selfharm_text(t)


def care_links():
    cp = P().get("care_person")
    if not cp:
        return None
    d = re.sub(r"\D", "", str(cp.get("phone", "")))
    if len(d) == 11 and d.startswith("01"):
        d = "880" + d[1:]
    if len(d) < 8:
        return None
    name, hh = (P().get("name") or "").strip(), now().strftime("%H:%M")
    msg = L({"en": f"{name or 'Someone'} needs help. Time: {hh}",
             "bn": f"{name or 'একজন'} সাহায্য চাইছেন। সময়: {hh.translate(_BN)}"})
    return {"tel": f"tel:+{d}", "wa": f"https://wa.me/{d}?text={quote(msg)}", "sms": f"sms:+{d}?body={quote(msg)}"}
