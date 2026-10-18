"""Dashboard + quick log. Start and profile live in pages_profile (re-exported below). No JavaScript."""
import streamlit as st

from base import (NEW_CHAPTER_WINDOW_DAYS, L, P, add_log, classify_glucose, fmt_date, fmt_glucose, from_mgdl,
                  glucose_summary, go, latest_glucose, logs, med_label, num, seen, to_date, to_mgdl, today,
                  water_today)
from content_learn import CARDS, EXPLAINERS
from content_q import QMODULES
from data_misc import DEMO_LABEL, food_warnings, match_foods
from engine import REMINDER_NOTE, T, TESTS, buckets, mark_done, selfharm_text, text_triggers
from pages_profile import render_profile, render_start  # noqa: F401  re-exported for app.py
from pages_safety import _esc, _help999, _rule15, open_emergency, render_doctor_visit, render_safety
from ui import NAV, card, lbl, scale_0_10, title

GLU_BOUNDS = (20, 600)  # VERIFY mg/dL limits accepted for a typed reading
RESULT = {"hba1c": (2.0, 20.0, 0.1, "%.1f"), "kidney": (0.1, 15.0, 0.1, "%.1f"),
          "lipid": (50.0, 600.0, 1.0, "%.0f"), "bp": (50.0, 300.0, 1.0, "%.0f")}  # VERIFY (min, max, step, format)
GCTX = {"fasting": T("Fasting, before breakfast", "খালি পেটে, সকালের খাবারের আগে"),
        "before_meal": T("Before a meal", "খাবারের আগে"), "after_meal": T("2 hours after a meal", "খাবারের ২ ঘণ্টা পরে"),
        "bedtime": T("At bedtime", "ঘুমের আগে"), "night": T("In the night", "রাতে"),
        "random": T("Any other time", "অন্য যেকোনো সময়")}
AMOUNT = {"small": T("Small", "অল্প"), "medium": T("Medium", "মাঝারি"), "large": T("Large", "বেশি")}
CARB_RANK = {"low": 0, "med": 1, "high": 2}
EXKIND = {"walk": T("Walking", "হাঁটা"), "cycle": T("Cycling", "সাইকেল চালানো"), "work": T("Housework or farm work", "ঘরের বা মাঠের কাজ"),
          "sport": T("Sport", "খেলাধুলা"), "other": T("Other", "অন্য")}
STATUS = {"better": T("Better", "ভালো"), "same": T("Same", "একই"), "worse": T("Worse", "খারাপ"),
          "unsure": T("Not sure", "নিশ্চিত নই")}
DUE_LBL = {"overdue": T("overdue", "দেরি হয়েছে"), "today": T("today", "আজ"), "week": T("this week", "এই সপ্তাহে")}


def _add(kind, **fields):
    add_log(kind, **fields)


def _k(tab, name):  # widget key; the counter changes after a save so inputs reset
    return f"ql_{tab}{st.session_state.get('ql_n_' + tab, 0)}_{name}"


def _bump(tab):
    st.session_state["ql_n_" + tab] = st.session_state.get("ql_n_" + tab, 0) + 1


def _screen(text):
    """Emergency or self-harm words in any free text go to the emergency route first."""
    if selfharm_text(text):
        open_emergency(crisis=True)
        st.rerun()
    elif text_triggers(text):
        open_emergency()
        st.rerun()


def _is_demo():
    return any(str(i.get("id", "")).startswith("demo-") for i in st.session_state.get("due", []))


def _is_new(cid, added):  # same rule as pages_guide, so opening Learn clears the banner
    try:
        age = (today() - to_date(added)).days
    except ValueError:
        return False
    last = seen().get(cid)
    return age <= NEW_CHAPTER_WINDOW_DAYS if not last else str(last)[:10] < str(added)[:10]


# ---------------------------------------------------------------- feedback after a save
def _flash():
    f = st.session_state.pop("ql_flash", None)
    if not f:
        return
    saved = L(T("Saved.", "সংরক্ষিত হয়েছে।"))
    if f["kind"] == "glucose":
        c = f["cls"]
        st.success(f"{saved} {fmt_glucose(f['mg'])}")
        if c in ("low", "severe_low"):
            st.warning(f"**{L(T('Low sugar: treat it now', 'সুগার কম: এখনই ব্যবস্থা নিন'))}**\n\n- {L(_rule15())}\n- {L(_help999())}")
            if c == "severe_low":
                st.button(L(T("Check for emergency signs", "জরুরি লক্ষণ আছে কিনা দেখুন")), key="ql_fl_sl",
                          on_click=open_emergency, args=("severe_low",))
        elif c == "very_high":
            st.warning(L(T("Your reading is very high. Check again. If you vomit, feel very sleepy, or breathe fast and deep, get help now.",
                           "আপনার মাপ খুব বেশি। আবার মাপুন। বমি হলে, খুব ঘুম ঘুম লাগলে, বা দ্রুত ও গভীর শ্বাস হলে এখনই সাহায্য নিন।")))
            st.button(L(T("Check for emergency signs", "জরুরি লক্ষণ আছে কিনা দেখুন")), key="ql_fl_vh",
                      on_click=open_emergency, args=("high_emergency",))
        elif c == "high":
            st.info(L(T("This is above your target range. Tell your doctor if it keeps happening.",
                        "এটি আপনার লক্ষ্যসীমার ওপরে। বারবার হলে ডাক্তারকে জানান।")))
    elif f["kind"] == "food":
        names = ", ".join(L(x) for x in f["names"])
        st.success(f"{saved} {L(T('We matched:', 'আমরা যা চিনেছি:'))} {names}" if names else saved)
        if not names:
            st.caption(L(T("We could not match the food. Your note is saved as you typed it.",
                           "খাবারটি চিনতে পারিনি। আপনার লেখা যেমন ছিল তেমনই সংরক্ষিত হয়েছে।")))
            if P().get("allergies"):
                st.info(L(T("Ingredients unknown: ask how the food was made if you have an allergy.",
                            "উপকরণ অজানা: অ্যালার্জি থাকলে খাবার কীভাবে রান্না হয়েছে জিজ্ঞাসা করুন।")))
        for w in f["warnings"]:
            (st.warning if w["level"] == "care" else st.info)(L(w["text"]))
    else:
        st.success(saved)


# ---------------------------------------------------------------- quick log tabs
def _glucose():
    u = P().get("units", "mgdl")
    mm = u == "mmol"
    g = latest_glucose()
    if g:
        st.caption(f"{L(T('Last reading', 'সর্বশেষ মাপ'))}: {fmt_glucose(g['value_mgdl'])}, {fmt_date(g['ts'])} {num(g['ts'][11:16])}")
    v = st.number_input(f"{L(T('Sugar reading', 'সুগারের মাপ'))} ({'mmol/L' if mm else 'mg/dL'})", value=None,
                        min_value=float(from_mgdl(GLU_BOUNDS[0], u)), max_value=float(from_mgdl(GLU_BOUNDS[1], u)),
                        step=0.1 if mm else 1.0, format="%.1f" if mm else "%.0f", key=_k("g", "v"))
    ctx = st.selectbox(L(T("When did you measure?", "কখন মেপেছেন?")), list(GCTX), format_func=lambda c: L(GCTX[c]),
                       key=_k("g", "c"))
    if st.button(lbl("save"), type="primary", key=_k("g", "s")):
        if v is None:
            st.warning(L(T("Please enter your reading.", "আপনার মাপটি লিখুন।")))
            return
        mg = round(to_mgdl(v, u), 1)
        add_log("glucose", value_mgdl=mg, context=ctx)
        st.session_state["ql_flash"] = {"kind": "glucose", "mg": mg, "cls": classify_glucose(mg)}
        _bump("g")
        st.rerun()


def _food():
    desc = st.text_input(L(T("What did you eat or drink?", "কী খেয়েছেন বা পান করেছেন?")), max_chars=150, key=_k("f", "d"))
    amt = st.selectbox(L(T("How much?", "কতটুকু?")), list(AMOUNT), format_func=lambda a: L(AMOUNT[a]), key=_k("f", "a"))
    own = st.text_input(L(T("Or write the amount, like 1 plate, 2 pieces, 1 bowl",
                            "অথবা পরিমাণ লিখুন, যেমন ১ প্লেট, ২ টুকরা, ১ বাটি")), max_chars=40, key=_k("f", "o"))
    if st.button(lbl("save"), type="primary", key=_k("f", "s")):
        t = desc.strip()
        if not t:
            st.warning(L(T("Please write what you ate.", "কী খেয়েছেন তা লিখুন।")))
            return
        _screen(t)
        _screen(own)
        with st.spinner(L(T("Checking the food...", "খাবার দেখা হচ্ছে..."))):
            ms = match_foods(t)
        ws = food_warnings(ms)
        carb = max((m["carb"] for m in ms), key=CARB_RANK.get, default="unknown")
        add_log("food", text=t, amount=own.strip() or amt, matched=[m["id"] for m in ms], carb=carb,
                warnings=[L(w["text"]) for w in ws])
        st.session_state["ql_flash"] = {"kind": "food", "names": [m["name"] for m in ms], "warnings": ws}
        _bump("f")
        st.rerun()


def _meds():
    meds = P().get("medicines", [])
    if not meds:
        st.info(L(T("No medicines in your profile yet.", "আপনার প্রোফাইলে এখনো কোনো ওষুধ নেই।")))
        st.button(L(NAV["profile"]), key="ql_m_prof", on_click=go, args=("profile",))
        return
    st.caption(L(T("Take medicines only as your doctor told you. We never calculate or change doses.",
                   "ওষুধ শুধু ডাক্তারের বলা অনুযায়ী নিন। আমরা কখনো ডোজ হিসাব বা পরিবর্তন করি না।")))
    t = today().isoformat()
    for i, m in enumerate(meds):
        name = str(m.get("name", ""))
        rows = [e for e in logs("med", 2) if e["ts"][:10] == t and str(e.get("name", "")).lower() == name.lower()]
        yes, no = sum(1 for e in rows if e.get("taken")), sum(1 for e in rows if not e.get("taken"))
        st.markdown(f"**{_esc(med_label(name))}**")
        if m.get("dose_text"):
            st.caption(_esc(m["dose_text"]))
        st.caption(f"{L(T('Today', 'আজ'))}: {L(T('taken', 'নিয়েছি'))} {num(yes)}, {L(T('missed', 'বাদ গেছে'))} {num(no)}")
        c1, c2 = st.columns(2)
        c1.button(L(T("Taken", "নিয়েছি")), key=f"ql_mt_{i}", type="primary", on_click=_add, args=("med",),
                  kwargs={"name": name, "taken": True}, use_container_width=True)
        c2.button(L(T("Missed", "বাদ গেছে")), key=f"ql_mm_{i}", on_click=_add, args=("med",),
                  kwargs={"name": name, "taken": False}, use_container_width=True)


def _water():
    p = P()
    if p.get("fluid_limit") or any(c in p.get("conditions", []) for c in ("kidney_disease", "heart_disease")):
        st.caption(L(T("The glass counter is hidden because of your health conditions or fluid limit. Follow your doctor's advice on fluids.",
                       "আপনার শারীরিক অবস্থা বা তরল সীমার কারণে গ্লাস গোনা লুকানো আছে। তরল নিয়ে ডাক্তারের পরামর্শ মানুন।")))
    else:
        w, tgt = water_today(), p.get("water_target")
        st.write(f"{L(T('Today', 'আজ'))}: {num(w)} {L(T('glasses', 'গ্লাস'))}"
                 + (f" {L(T('of', 'এর মধ্যে'))} {num(tgt)}" if tgt else ""))
        st.button(L(T("Add 1 glass", "১ গ্লাস যোগ করুন")), key="ql_w", on_click=_add, args=("water",), kwargs={"glasses": 1})
        if tgt and w >= tgt:
            st.caption(L(T("You have reached the target your doctor set.", "আপনি ডাক্তারের দেওয়া লক্ষ্যে পৌঁছেছেন।")))
    v = scale_0_10(T("How thirsty are you right now?", "এখন কতটা পিপাসা পাচ্ছে?"), _k("w", "t"))
    if st.button(L(T("Save thirst", "পিপাসা সংরক্ষণ করুন")), key=_k("w", "s")):
        add_log("symptom", module="thirst", key="t_thirst", severity=v, numbness=False, note="")
        st.session_state["ql_flash"] = {"kind": "ok"}
        _bump("w")
        st.rerun()


def _exercise():
    m = st.number_input(L(T("Minutes", "কত মিনিট")), min_value=1, max_value=600, step=5, value=None, key=_k("x", "m"))
    kind = st.selectbox(L(T("What kind?", "কী ধরনের?")), list(EXKIND), format_func=lambda x: L(EXKIND[x]), key=_k("x", "k"))
    st.caption(L(T("Ask your doctor what to do before and after exercise.", "ব্যায়ামের আগে ও পরে কী করবেন তা ডাক্তারকে জিজ্ঞাসা করুন।")))
    plan = str((P().get("doctor_plan") or {}).get("exercise") or "").strip()
    if plan:
        st.markdown(f"**{L(T('Your doctor' + chr(39) + 's instruction (as you entered it)', 'আপনার ডাক্তারের নির্দেশ (আপনার লেখা অনুযায়ী)'))}**")
        st.info(_esc(plan))
    if st.button(lbl("save"), type="primary", key=_k("x", "s")):
        if m is None:
            st.warning(L(T("Please enter the minutes.", "মিনিট লিখুন।")))
            return
        add_log("exercise", minutes=int(m), kind=kind)
        st.session_state["ql_flash"] = {"kind": "ok"}
        _bump("x")
        st.rerun()


def _mood():
    lv = [1, 2, 3, 4, 5]
    en = st.radio(L(T("Energy today", "আজ শরীরে শক্তি")), lv, index=None, horizontal=True, format_func=num, key=_k("m", "e"))
    md = st.radio(L(T("Mood today", "আজ মনের অবস্থা")), lv, index=None, horizontal=True, format_func=num, key=_k("m", "d"))
    st.caption(f"{num(1)} = {L(T('very low', 'খুব কম'))}, {num(5)} = {L(T('very good', 'খুব ভালো'))}")
    if st.button(lbl("save"), type="primary", key=_k("m", "s")):
        if en is None and md is None:
            st.warning(L(T("Please choose at least one.", "অন্তত একটি বেছে নিন।")))
            return
        if en is not None:
            add_log("energy", level=int(en))
        if md is not None:
            add_log("mood", level=int(md))
        st.session_state["ql_flash"] = {"kind": "ok"}
        _bump("m")
        st.rerun()
    if sum(1 for e in logs("mood", 7) if isinstance(e.get("level"), int) and e["level"] <= 2) >= 2:
        st.info(L(T("Diabetes can be tiring. Please talk to your doctor or someone you trust.",
                    "ডায়াবেটিস মানুষকে ক্লান্ত করে দিতে পারে। ডাক্তার বা বিশ্বাসের কারও সাথে কথা বলুন।")))


# ---------------------------------------------------------------- dashboard sections
def _banner():
    n = sum(1 for c in CARDS if _is_new(c["id"], c["added_on"])) + sum(
        1 for k, e in EXPLAINERS.items() if _is_new(k, e["added_on"]))
    if n:
        st.info(L(T(f"{num(n)} new chapters are waiting in Learn.", f"শিখুন অংশে {num(n)}টি নতুন অধ্যায় আছে।")))
        st.button(L(NAV["learn"]), key="db_learn", on_click=go, args=("learn",))


def _done(i, key):
    r = st.session_state.get(f"dn_r_{i}") if key in RESULT else None
    mark_done(i, r)


def _due():
    b = buckets()
    rows = [(k, i) for k in ("overdue", "today", "week") for i in b[k] if i.get("key") in TESTS]
    st.subheader(L(T("Checks and visits due", "যেসব পরীক্ষা ও ভিজিটের সময় হয়েছে")), anchor=False)
    if not rows:
        st.caption(L(T("Nothing is due this week.", "এই সপ্তাহে কিছুর সময় আসেনি।")))
    for bk, i in rows:
        key = i["key"]
        with card():
            st.markdown(f"**{L(TESTS[key]['title'])}**")
            st.caption(f"{fmt_date(i['due'])} · {L(DUE_LBL[bk])}")
            with st.expander(lbl("mark_done")):
                if key in RESULT and TESTS[key].get("result"):
                    lo, hi, step, fmt = RESULT[key]
                    st.number_input(L(TESTS[key]["result"]) + f" ({L(T('optional', 'ঐচ্ছিক'))})", value=None,
                                    min_value=lo, max_value=hi, step=step, format=fmt, key=f"dn_r_{i['id']}")
                st.button(lbl("mark_done"), type="primary", key=f"dn_b_{i['id']}", on_click=_done, args=(i["id"], key))
    st.caption(L(REMINDER_NOTE))


def _concern(k):
    s = st.session_state
    v = s.get(f"cn_{k}")
    if v in STATUS:
        add_log("concern", key=k, status=v)
    s[f"cn_{k}"] = None  # unselect, so the same answer can be given again another day


def _concerns():
    mods = [k for k in QMODULES if any(e.get("module") == k for e in logs("symptom", 14))]
    if not mods:
        return
    st.subheader(L(T("How are your concerns?", "আপনার সমস্যাগুলো কেমন আছে?")), anchor=False)
    for k in mods:
        with card():
            st.markdown(f"**{L(QMODULES[k]['title'])}**")
            st.radio(L(T("How is it now, compared with before?", "আগের তুলনায় এখন কেমন?")), list(STATUS), index=None,
                     horizontal=True, format_func=lambda x: L(STATUS[x]), key=f"cn_{k}", on_change=_concern, args=(k,))
            last = [e for e in logs("concern") if e.get("key") == k and e.get("status") in STATUS]
            if last:
                st.caption(f"{L(T('Last answer', 'সর্বশেষ উত্তর'))}: {L(STATUS[last[-1]['status']])}, {fmt_date(last[-1]['ts'])}")


def _chart():
    u = P().get("units", "mgdl")
    g = [e for e in logs("glucose", 14) if isinstance(e.get("value_mgdl"), (int, float))][-30:]
    st.subheader(L(T("Your sugar, last 14 days", "আপনার সুগার, গত ১৪ দিন")), anchor=False)
    if len(g) < 2:
        st.caption(L(T("Log a few readings to see your trend.", "ধারা দেখতে কয়েকটি মাপ লিখুন।")))
        return
    st.line_chart({f"{L(T('Sugar', 'সুগার'))} ({'mmol/L' if u == 'mmol' else 'mg/dL'})":
                   [from_mgdl(e["value_mgdl"], u) for e in g]}, height=200, color="#0F766E")
    s = glucose_summary(14)
    st.caption(f"{L(T('Average', 'গড়'))}: {fmt_glucose(s['avg'])} · "
               f"{L(T('in your range', 'আপনার সীমার মধ্যে'))}: {num(s['tir_pct'])}%")


def render_dashboard():
    name = str(P().get("name") or "").strip()
    title(NAV["dashboard"])
    if _is_demo():
        st.caption(L(DEMO_LABEL))
    if name:
        st.markdown(f"**{L(T('Welcome', 'স্বাগতম'))}, {_esc(name)}**")
    _banner()
    render_safety()
    _due()
    st.subheader(L(T("Quick log", "দ্রুত লিখুন")), anchor=False)
    _flash()
    tabs = st.tabs([L(T("Sugar", "সুগার")), L(T("Food", "খাবার")), L(T("Medicine", "ওষুধ")),
                    L(T("Water and thirst", "পানি ও পিপাসা")), L(T("Exercise", "ব্যায়াম")),
                    L(T("Energy and mood", "শক্তি ও মন"))])
    for tab, fn in zip(tabs, (_glucose, _food, _meds, _water, _exercise, _mood)):
        with tab:
            fn()
    _concerns()
    _chart()
    render_doctor_visit()
