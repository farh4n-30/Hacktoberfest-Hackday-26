"""Meal/insulin safety, emergency screen, doctor-visit form. Imports base, engine, ui. Never outputs a dose."""
import re
from datetime import datetime, timedelta

import streamlit as st

from base import (DEFAULT_TARGET, EMERGENCY_NUMBER, HYPO_L1, L, MED_NAMES, P, TEST_INTERVALS,
                  classify_glucose, fmt_date, fmt_glucose, from_mgdl, go, latest_glucose, med_label,
                  now, num, set_profile, to_mgdl, today)
from engine import (DEFAULT_OFFSETS, GROUPS, QUESTION_PACK, T, TESTS, add_due, care_links,
                    check_flags, screen_items)
from ui import LABELS, badge, card, lbl, link_button, title

RECENT_H = 3  # VERIFY hours a glucose reading counts as current
TARGET_BOUNDS = (30, 500)  # VERIFY mg/dL limits accepted for a new target range
PLAN_KEYS = ["missed_meal", "small_meal", "sick_day", "low_sugar", "bedtime", "exercise"]
CLS = ["metformin", "sulfonylurea", "sglt2", "dpp4", "insulin_basal", "insulin_rapid", "insulin_mix", "other"]
TIMES = {"morning": T("Morning", "সকাল"), "noon": T("Noon", "দুপুর"),
         "evening": T("Evening", "সন্ধ্যা"), "night": T("Night", "রাত")}
LOWQ = T("What should I do if my sugar is low?", "সুগার কমে গেলে আমি কী করব?")
QS = {**QUESTION_PACK, "low_sugar": LOWQ}
GLU = {"severe_low": T("very low", "খুব কম"), "low": T("low", "কম"), "in_range": T("in your range", "আপনার সীমার মধ্যে"),
       "high": T("high", "বেশি"), "very_high": T("very high", "খুব বেশি")}
SC = {  # scenario -> (label, doctor_plan field)
    "skip": (T("I am skipping a meal", "আমি একটি খাবার বাদ দিচ্ছি"), "missed_meal"),
    "noeat": (T("I took my medicine but I am not eating", "ওষুধ বা ইনসুলিন নিয়েছি, কিন্তু খাচ্ছি না"), "missed_meal"),
    "sleep": (T("I am going to sleep after insulin", "ইনসুলিন নিয়ে ঘুমাতে যাচ্ছি"), "bedtime"),
    "low": (T("I feel low now", "এখন আমার সুগার কম মনে হচ্ছে"), "low_sugar"),
    "sick": (T("I am sick and cannot eat", "আমি অসুস্থ, খেতে পারছি না"), "sick_day"),
}
STEPS = {
    "skip": [T("Check your sugar now.", "এখনই সুগার মাপুন।"),
             T("Do not guess your medicine. Follow your doctor's plan below.", "ওষুধ আন্দাজে নেবেন না। নিচে ডাক্তারের পরিকল্পনা দেখুন।")],
    "noeat": [T("Check your sugar now, then keep checking it until you eat.", "এখনই সুগার মাপুন, তারপর খাওয়া পর্যন্ত বারবার মাপুন।"),
              T("Do not take extra medicine. Follow your doctor's plan below.", "বাড়তি ওষুধ নেবেন না। নিচে ডাক্তারের পরিকল্পনা দেখুন।"),
              T("Tell someone near you that your sugar may go low.", "কাছের কাউকে বলুন যে আপনার সুগার কমে যেতে পারে।")],
    "sleep": [T("Check your sugar before you sleep. Do this first.", "ঘুমের আগে সুগার মাপুন। এটি আগে করুন।"),
              T("If it is low, treat it and recheck before you sleep.", "কম হলে আগে ব্যবস্থা নিন, ঘুমের আগে আবার মাপুন।"),
              T("Follow your doctor's bedtime plan below. Tell someone at home.", "নিচে ডাক্তারের শোয়ার আগের পরিকল্পনা দেখুন। বাসার কাউকে জানান।")],
    "low": [T("Treat it now. The steps are below.", "এখনই ব্যবস্থা নিন। ধাপগুলো নিচে আছে।")],
    "sick": [T("Sip fluids often, unless your doctor limits fluids.", "ঘন ঘন অল্প তরল খান, তবে ডাক্তার সীমা দিলে তা মানুন।"),
             T("Check your sugar more often.", "সুগার বেশি বার মাপুন।"),
             T("Do not stop or change medicine on your own. Follow your doctor's sick-day plan below.",
               "নিজে ওষুধ বন্ধ বা বদলাবেন না। নিচে ডাক্তারের অসুস্থতার দিনের পরিকল্পনা দেখুন।")],
}
WARN = T("Signs of low sugar: shaking, sweating, sudden hunger, headache, fast heartbeat, feeling confused.",
         "সুগার কমে যাওয়ার লক্ষণ: কাঁপুনি, ঘাম, হঠাৎ ক্ষুধা, মাথাব্যথা, বুক ধড়ফড়, বিভ্রান্ত লাগা।")
STILL = T("Still low, or not sure? Ask someone to stay with you and call your doctor.",
          "এখনো কম, বা নিশ্চিত নন? কাউকে আপনার কাছে থাকতে বলুন এবং ডাক্তারকে ফোন করুন।")


def _esc(t):
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~<$&])", r"\\\1", str(t or ""))


def _rule15():
    x = fmt_glucose(HYPO_L1)
    return T(f"Rule of 15 (sugar below {x}, or with these signs): take 15 g of fast sugar, such as glucose tablets, "
             "juice or sugar in water. Recheck in 15 minutes.",  # VERIFY
             f"১৫ এর নিয়ম (সুগার {x} এর নিচে, বা এই লক্ষণ থাকলে): ১৫ গ্রাম দ্রুত চিনিজাতীয় কিছু খান, যেমন গ্লুকোজ "
             "ট্যাবলেট, ফলের রস বা পানিতে চিনি। ১৫ মিনিট পর আবার মাপুন।")


def _help999():
    n = num(EMERGENCY_NUMBER)
    return T(f"Get emergency help (call {n}) if the person is confused, cannot swallow, has a fit or faints. "
             "Do not give food or drink.",  # VERIFY
             f"কেউ বিভ্রান্ত হলে, গিলতে না পারলে, খিঁচুনি হলে বা অজ্ঞান হলে জরুরি সাহায্য নিন ({n} নম্বরে ফোন করুন)। "
             "খাবার বা পানীয় দেবেন না।")


def _call_label():
    n = num(EMERGENCY_NUMBER)
    return T(f"Call {n} now", f"এখনই {n} নম্বরে ফোন করুন")


# ---------------------------------------------------------------- navigation state
def open_emergency(group=None, crisis=False):
    """Open the emergency view cleanly. group = red-flag group to check first, crisis = self-harm route."""
    st.session_state["flag_group"] = group if group in GROUPS else None
    st.session_state["crisis"] = bool(crisis)
    go("emergency")


def _leave(view="dashboard"):
    st.session_state["flag_group"], st.session_state["crisis"] = None, False
    go(view)


def _open_visit():
    st.session_state["visit_open"] = True


# ---------------------------------------------------------------- emergency
def _care_buttons():
    links, cp = care_links(), P().get("care_person")
    if not links:
        st.caption(L(T("You have not added a trusted person. You can add one in My profile.",
                       "আপনি কোনো বিশ্বাসের মানুষকে যোগ করেননি। আমার প্রোফাইলে যোগ করতে পারেন।")))
        st.button(L(T("Add a trusted person", "বিশ্বাসের একজনকে যোগ করুন")), key="em_add_cp",
                  on_click=_leave, args=("profile",))
        return
    name = _esc((cp.get("name") or "").strip()) or L(T("my trusted person", "আমার বিশ্বাসের মানুষ"))
    st.markdown(f"**{L(T('Tell your trusted person', 'আপনার বিশ্বাসের মানুষকে জানান'))}:** {name}")
    link_button(f"{L(T('Call', 'ফোন করুন'))}: {name}", links["tel"], "secondary")
    link_button(f"{L(T('WhatsApp', 'হোয়াটসঅ্যাপ'))}: {name}", links["wa"], "secondary")
    link_button(f"{L(T('Text message', 'এসএমএস'))}: {name}", links["sms"], "secondary")


def _call_block():
    n = num(EMERGENCY_NUMBER)
    with card():
        badge("emergency")
        st.error("## " + L(T(f"These can be signs of a medical emergency. Call {n} now.",
                             f"এগুলো জরুরি অবস্থার লক্ষণ হতে পারে। এখনই {n} নম্বরে ফোন করুন।")))
        link_button(_call_label(), f"tel:{EMERGENCY_NUMBER}", "primary")
        st.caption(L(T("Stay where you are. Tell someone near you. Do not drive yourself.",
                       "যেখানে আছেন সেখানেই থাকুন। কাছের কাউকে জানান। নিজে গাড়ি চালাবেন না।")))
    _care_buttons()


def _checklist(groups):
    sel = []
    for g in groups:
        st.markdown(f"**{L(GROUPS[g]['title'])}**")
        for it in screen_items(g):
            if st.checkbox(L(it["text"]), key="fl_" + it["id"]):
                sel.append(it["id"])
    return sel


def _not_met():
    n = num(EMERGENCY_NUMBER)
    st.info(L(T(f"What you ticked does not meet our emergency rules. This is not a diagnosis. "
                f"If you feel very unwell, call {n} anyway.",
                f"আপনার বাছাই করা লক্ষণ আমাদের জরুরি নিয়মের সাথে মেলেনি। এটি রোগনির্ণয় নয়। "
                f"খুব অসুস্থ বোধ করলে তবুও {n} নম্বরে ফোন করুন।")))


def render_emergency():
    s = st.session_state
    title(LABELS["emergency"])
    grp = s.get("flag_group")
    if s.get("crisis"):
        n = num(EMERGENCY_NUMBER)
        st.error(L(T(f"What you are feeling matters, and you do not have to face it alone. Please tell someone you "
                     f"trust right now and stay near them. If you think you might hurt yourself, call {n} now or "
                     f"go to the nearest hospital.",
                     f"আপনি যা অনুভব করছেন তা গুরুত্বপূর্ণ, আর আপনাকে একা সামলাতে হবে না। এখনই আপনার বিশ্বাসের "
                     f"কাউকে জানান এবং তার কাছে থাকুন। নিজের ক্ষতি করতে পারেন মনে হলে এখনই {n} নম্বরে ফোন করুন "
                     f"অথবা কাছের হাসপাতালে যান।")))
        link_button(_call_label(), f"tel:{EMERGENCY_NUMBER}", "primary")
        _care_buttons()
    elif grp in GROUPS:  # routed here by another page: check the signs first
        st.write(L(T("Please tick any sign that applies to you right now. This is not a diagnosis.",
                     "এই মুহূর্তে যে লক্ষণগুলো আছে তাতে টিক দিন। এটি রোগনির্ণয় নয়।")))
        sel = _checklist([grp])
        if check_flags(sel)["level"] == "emergency":
            _call_block()
        else:
            if sel:
                _not_met()
            link_button(_call_label(), f"tel:{EMERGENCY_NUMBER}", "secondary")
    else:  # Emergency button: call first, no questions in the way
        _call_block()
        with st.expander(L(T("Not sure what is happening? Check the signs", "কী হচ্ছে বুঝতে পারছেন না? লক্ষণগুলো দেখুন"))):
            sel = _checklist(list(GROUPS))
            if sel:
                res = check_flags(sel)
                if res["level"] == "emergency":
                    n = num(EMERGENCY_NUMBER)
                    st.error(L(T(f"These can be signs of a medical emergency ({', '.join(L(GROUPS[g]['title']) for g in res['groups'])}). Call {n} now.",
                                 f"এগুলো জরুরি অবস্থার লক্ষণ হতে পারে ({', '.join(L(GROUPS[g]['title']) for g in res['groups'])})। এখনই {n} নম্বরে ফোন করুন।")))
                else:
                    _not_met()
    st.button(lbl("back"), key="em_back", on_click=_leave)


# ---------------------------------------------------------------- meal / insulin safety
def render_safety():
    with st.expander(L(T("I'm skipping a meal / going to sleep after insulin",
                         "আমি খাবার বাদ দিচ্ছি / ইনসুলিন নিয়ে ঘুমাতে যাচ্ছি"))):
        sc = st.radio(L(T("What is happening?", "কী হচ্ছে?")), list(SC), index=None,
                      format_func=lambda k: L(SC[k][0]), key="sf_sc")
        if not sc:
            st.caption(L(T("Choose one to see safety steps.", "নিরাপত্তার ধাপ দেখতে একটি বেছে নিন।")))
            return
        g = latest_glucose()
        cls, recent = None, False
        if g:
            cls = classify_glucose(g["value_mgdl"])
            age = now() - datetime.fromisoformat(g["ts"]).replace(tzinfo=None)
            recent = age.total_seconds() < RECENT_H * 3600
        conf = st.checkbox(L(T("Right now I am confused, cannot swallow, had a fit, or fainted.",
                               "এই মুহূর্তে আমি বিভ্রান্ত, গিলতে পারছি না, খিঁচুনি হয়েছে, বা অজ্ঞান হয়েছিলাম।")), key="sf_conf")
        if conf or (recent and cls == "severe_low"):
            open_emergency()
            st.rerun()
        if g:  # (a) latest glucose class
            st.markdown(f"**{L(T('Your latest reading', 'আপনার সর্বশেষ মাপ'))}:** {fmt_glucose(g['value_mgdl'])} "
                        f"({L(GLU[cls])}), {fmt_date(g['ts'])} {num(g['ts'][11:16])}")
            if not recent:
                st.caption(L(T("This reading is not recent. Check your sugar again now.",
                               "এই মাপ সাম্প্রতিক নয়। এখনই আবার সুগার মাপুন।")))
        else:
            st.caption(L(T("No reading yet. Check your sugar now.", "এখনো কোনো মাপ নেই। এখনই সুগার মাপুন।")))
        st.markdown("\n".join("- " + L(x) for x in STEPS[sc]))
        low_now = recent and cls in ("low", "severe_low")
        if sc == "low" or low_now:
            st.warning(f"**{L(T('Treat low sugar now', 'কম সুগারের ব্যবস্থা এখনই নিন'))}**\n\n- {L(_rule15())}\n- {L(STILL)}")
        field = SC[sc][1]  # (b) the user's own plan, verbatim, or a no-plan message
        plan = P().get("doctor_plan") or {}
        txt = str(plan.get(field) or "").strip()
        if txt:
            st.markdown(f"**{L(T(chr(39).join(['Your doctor', 's instruction (as you entered it)']), 'আপনার ডাক্তারের নির্দেশ (আপনার লেখা অনুযায়ী)'))}**")
            st.info(_esc(txt))
            if plan.get("updated"):
                st.caption(f"{L(T('Entered on', 'লেখা হয়েছে'))}: {fmt_date(plan['updated'])}")
        else:
            st.warning(L(T("No plan yet: don't guess. Check your sugar. Ask your doctor.",
                           "এখনো কোনো পরিকল্পনা নেই: আন্দাজ করবেন না। সুগার মাপুন। ডাক্তারকে জিজ্ঞাসা করুন।")))
            st.caption(f"{L(T('Ask your doctor', 'ডাক্তারকে জিজ্ঞাসা করুন'))}: {L(QS[field])}")
            st.button(L(T("Open the question list for my doctor", "ডাক্তারের জন্য প্রশ্নের তালিকা খুলুন")),
                      key="sf_pack", on_click=_open_visit)
            if st.session_state.get("visit_open"):
                st.info(L(T("The form is open at the bottom of this page: \"I went to the doctor today\".",
                            "ফর্মটি এই পাতার নিচে খোলা আছে: \"আজ আমি ডাক্তার দেখিয়েছি\"।")))
        st.markdown(f"- {L(WARN)}\n- {L(_help999())}")  # (c) fixed safety text
        if sc == "sleep":
            st.markdown("- " + L(T("Before you sleep, check your sugar first.", "ঘুমের আগে প্রথমে সুগার মাপুন।")))
        if sc == "sick" or (recent and cls == "very_high"):
            st.button(L(T("Check for emergency signs", "জরুরি লক্ষণ আছে কিনা দেখুন")), key="sf_flags",
                      on_click=open_emergency, args=("high_emergency",))


# ---------------------------------------------------------------- doctor visit
def _schedule(key, due, iv=None):
    st.session_state["due"] = [i for i in st.session_state.get("due", []) if i.get("done") or i.get("key") != key]
    add_due(key, due, iv)


def _med_fields(k, m, existing):
    name = st.text_input(L(T("Medicine name", "ওষুধের নাম")), value=m.get("name", ""), max_chars=60, key=k + "n")
    cls = st.selectbox(L(T("Type of medicine", "ওষুধের ধরন")), CLS, key=k + "c",
                       index=CLS.index(m["cls"]) if m.get("cls") in CLS else len(CLS) - 1,
                       format_func=lambda c: L(MED_NAMES[c]))
    dose = st.text_input(L(T("Dose and timing, as your doctor told you", "ডোজ ও সময়, ডাক্তারের বলা অনুযায়ী")),
                         value=m.get("dose_text", ""), max_chars=80, key=k + "d")
    times = st.multiselect(L(T("When do you take it?", "কখন খান?")), list(TIMES), key=k + "t",
                           default=[x for x in m.get("times", []) if x in TIMES], format_func=lambda x: L(TIMES[x]))
    stop = existing and st.checkbox(L(T("My doctor stopped this medicine", "ডাক্তার এই ওষুধ বন্ধ করেছেন")), key=k + "s")
    return {"name": name, "cls": cls, "dose": dose, "times": times, "stop": stop}


def render_doctor_visit():
    s = st.session_state
    if s.pop("visit_msg", False):
        st.toast(L(T("Saved. Your profile and reminders are updated.", "সংরক্ষিত হয়েছে। আপনার প্রোফাইল ও রিমাইন্ডার হালনাগাদ হয়েছে।")))
    n, p = s.setdefault("visit_n", 0), P()
    u = p.get("units", "mgdl")
    t = p.get("target_range") or DEFAULT_TARGET
    mm = u == "mmol"
    unit = "mmol/L" if mm else "mg/dL"
    with st.expander(L(T("I went to the doctor today", "আজ আমি ডাক্তার দেখিয়েছি")), expanded=bool(s.get("visit_open"))):
        st.caption(L(T("Write what your doctor told you. Leave blank what did not change.",
                       "ডাক্তার যা বলেছেন তা লিখুন। যা বদলায়নি তা ফাঁকা রাখুন।")))
        with st.form(f"visit_form_{n}"):
            dx = st.text_area(L(T("Any change in diagnosis or health conditions", "রোগনির্ণয় বা শারীরিক অবস্থায় কোনো পরিবর্তন")),
                              max_chars=300, height=68, key=f"v{n}_dx")
            st.markdown(f"**{L(T('Medicines', 'ওষুধ'))}**")
            st.caption(L(T("Change a medicine, tick Stopped, or add a new one below. Write the dose exactly as your doctor "
                           "told you. We never calculate or change doses.",
                           "ওষুধ বদলান, 'বন্ধ' চিহ্ন দিন, অথবা নিচে নতুন ওষুধ যোগ করুন। ডোজ ডাক্তারের বলা অনুযায়ী হুবহু লিখুন। "
                           "আমরা কখনো ডোজ হিসাব বা পরিবর্তন করি না।")))
            rows = []
            for i, m in enumerate(p.get("medicines", [])):
                st.markdown(f"**{_esc(med_label(m.get('name')))}**")
                rows.append((m, _med_fields(f"v{n}_m{i}", m, True)))
            st.markdown(f"**{L(T('Add a new medicine (optional)', 'নতুন ওষুধ যোগ করুন (ঐচ্ছিক)'))}**")
            new = _med_fields(f"v{n}_new", {"cls": "other"}, False)
            tests = st.multiselect(L(T("Tests your doctor ordered", "ডাক্তার যেসব পরীক্ষা দিয়েছেন")),
                                   [k for k in TESTS if k != "doctor_visit"], key=f"v{n}_tests",
                                   format_func=lambda k: L(TESTS[k]["title"]))
            st.caption(L(T("They will show as reminders on your dashboard.", "এগুলো ড্যাশবোর্ডে রিমাইন্ডার হিসেবে দেখাবে।")))
            st.markdown(f"**{L(T('New sugar target range, if your doctor changed it', 'ডাক্তার বদলালে নতুন সুগারের লক্ষ্যসীমা'))}**")
            kw = {"min_value": 1.0, "max_value": 40.0 if mm else 600.0, "step": 0.1 if mm else 1.0,
                  "format": "%.1f" if mm else "%.0f"}
            lo = st.number_input(f"{L(T('Lowest', 'সর্বনিম্ন'))} ({unit})", value=float(from_mgdl(t["low"], u)), key=f"v{n}_lo", **kw)
            hi = st.number_input(f"{L(T('Highest', 'সর্বোচ্চ'))} ({unit})", value=float(from_mgdl(t["high"], u)), key=f"v{n}_hi", **kw)
            has_next = st.checkbox(L(T("I have a date for my next visit", "পরের ভিজিটের তারিখ আমার কাছে আছে")), key=f"v{n}_hn")
            nv = st.date_input(L(T("Next visit date", "পরের ভিজিটের তারিখ")), key=f"v{n}_nv", min_value=today(),
                               value=today() + timedelta(days=TEST_INTERVALS["doctor_visit"]))
            st.markdown(f"**{L(T('Your doctor’s answers to the common questions', 'সাধারণ প্রশ্নে আপনার ডাক্তারের উত্তর'))}**")
            st.caption(L(T("Write what your doctor said, in their words. We show it back exactly as you wrote it.",
                           "ডাক্তার যা বলেছেন তাঁর কথায় লিখুন। আমরা ঠিক আপনার লেখা অনুযায়ীই দেখাব।")))
            old = p.get("doctor_plan") or {}
            plan_in = {k: st.text_area(L(QS[k]), value=str(old.get(k, "")), max_chars=500, height=68, key=f"v{n}_p{k}")
                       for k in PLAN_KEYS}
            ok = st.form_submit_button(lbl("save"), type="primary")
        if not ok:
            return
        nl, nh = to_mgdl(lo, u), to_mgdl(hi, u)
        moved = abs(lo - float(from_mgdl(t["low"], u))) > 1e-6 or abs(hi - float(from_mgdl(t["high"], u))) > 1e-6
        if moved and not (TARGET_BOUNDS[0] <= nl < nh <= TARGET_BOUNDS[1]):
            st.error(L(T("The target range does not look right. Please check the two numbers.",
                         "লক্ষ্যসীমা ঠিক মনে হচ্ছে না। দুটি সংখ্যা আবার দেখুন।")))
            return
        meds = [{**m, "name": f["name"].strip() or m.get("name", ""), "cls": f["cls"], "dose_text": f["dose"].strip(),
                 "times": f["times"]} for m, f in rows if not f["stop"]]
        if new["name"].strip():
            meds.append({"name": new["name"].strip(), "cls": new["cls"], "dose_text": new["dose"].strip(),
                         "times": new["times"], "start_date": today().isoformat()})
        vals = {k: v.strip() for k, v in plan_in.items()}
        same = vals == {k: str(old.get(k, "")) for k in PLAN_KEYS}
        q = {**p, "medicines": meds}
        if moved:
            q["target_range"] = {"low": round(nl, 1), "high": round(nh, 1)}
        if dx.strip():
            prev = p.get("other_history") or ""
            q["other_history"] = (prev + "\n" if prev else "") + f"{today().isoformat()}: {dx.strip()}"
        if any(vals.values()) or old:
            q["doctor_plan"] = {**vals, "updated": old["updated"] if same and old.get("updated") else today().isoformat()}
        set_profile(q)
        for k in tests:
            _schedule(k, today() + timedelta(days=DEFAULT_OFFSETS.get(k, 14)))
        if has_next:
            _schedule("doctor_visit", nv, TEST_INTERVALS["doctor_visit"])
        s["visit_n"], s["visit_open"], s["visit_msg"] = n + 1, False, True
        st.rerun()
