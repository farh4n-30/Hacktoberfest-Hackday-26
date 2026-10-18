"""Start screen and profile form (split from F09). Imports base, data_misc, engine, ui, pages_safety. No JavaScript."""
import re
from datetime import timedelta

import streamlit as st

from base import (APP_NAME, MAX_IMPORT_BYTES, L, P, blank_profile, export_json, from_mgdl, go, import_json,
                  load_demo, med_label, reset, set_profile, to_mgdl, today)
from data_misc import DEMO_INFO, DEMO_LABEL
from engine import T
from pages_safety import TARGET_BOUNDS, _esc, _med_fields
from ui import NAV, card, lbl, title

SEX = {"male": T("Male", "পুরুষ"), "female": T("Female", "নারী"), "other": T("Other / prefer not to say", "অন্য / বলতে চাই না")}
DTYPE = {"type1": T("Type 1", "টাইপ ১"), "type2": T("Type 2", "টাইপ ২"),
         "gestational": T("Gestational (in pregnancy)", "গর্ভকালীন"), "prediabetes": T("Prediabetes", "প্রি-ডায়াবেটিস"),
         "unsure": T("Not sure", "নিশ্চিত নই")}
COND = {"hypertension": T("High blood pressure", "উচ্চ রক্তচাপ"), "kidney_disease": T("Kidney disease", "কিডনির রোগ"),
        "heart_disease": T("Heart disease", "হৃদরোগ"), "thyroid": T("Thyroid problem", "থাইরয়েডের সমস্যা"),
        "neuropathy_dx": T("Nerve damage (a doctor told me)", "স্নায়ুর ক্ষতি (ডাক্তার বলেছেন)"),
        "retinopathy_dx": T("Eye damage from diabetes (a doctor told me)", "ডায়াবেটিসে চোখের ক্ষতি (ডাক্তার বলেছেন)"),
        "pregnancy": T("Pregnant", "গর্ভবতী"), "liver": T("Liver disease", "লিভারের রোগ"),
        "other": T("Other long-term illness", "অন্য দীর্ঘমেয়াদি রোগ")}
STARTED = {  # new medicine: when started -> approximate days ago  # VERIFY estimates
    "unsure": (T("Not sure, or a long time ago", "নিশ্চিত নই, বা অনেক আগে"), None),
    "m1": (T("Less than 1 month ago", "১ মাসের কম আগে"), 15),
    "m12": (T("1 to 12 months ago", "১ থেকে ১২ মাস আগে"), 180),
    "y1": (T("More than 1 year ago", "১ বছরের বেশি আগে"), 400)}
_ASCII = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def _flag(key, value):
    st.session_state[key] = value


def _clip(v, lo, hi):
    return min(max(v, lo), hi)


def _phone(raw):
    """Digits only, international form (8801XXXXXXXXX). None if blank or not plausible."""
    d = re.sub(r"\D", "", str(raw or "").translate(_ASCII))
    if len(d) == 11 and d.startswith("01"):
        d = "880" + d[1:]
    return d if 8 <= len(d) <= 15 else None


# ---------------------------------------------------------------- start
def _upload():
    up = st.file_uploader(L(T("Choose your profile file (.json)", "আপনার প্রোফাইল ফাইল বেছে নিন (.json)")),
                          type=["json"], key="st_file")
    if up is None:
        return
    if up.size > MAX_IMPORT_BYTES:
        st.error(L(T("This file is too big.", "ফাইলটি অনেক বড়।")))
        return
    try:
        text = up.getvalue().decode("utf-8-sig")
    except UnicodeDecodeError:
        text = None
    if st.button(L(T("Load this file", "এই ফাইল লোড করুন")), type="primary", key="st_load"):
        ok, msg = import_json(text)
        if ok:
            st.rerun()
        st.error(msg)


def render_start():
    title(APP_NAME, T("A diabetes companion for the time between doctor visits.",
                      "ডাক্তার দেখানোর মাঝের সময়ের জন্য ডায়াবেটিসের সঙ্গী।"))
    with card():
        st.write(L(T("Log your sugar and stay safe with meals and medicine. "
                     "We also look for early signs of problems in feet, eyes, kidneys, nerves and heart. "
                     "You get a careful report to bring to your doctor.",
                     "আপনার সুগার লিখে রাখুন এবং খাবার ও ওষুধের ব্যাপারে নিরাপদ থাকুন। "
                     "পা, চোখ, কিডনি, স্নায়ু ও হৃদয়ের সমস্যার প্রথম লক্ষণও আমরা খেয়াল রাখি। "
                     "ডাক্তারের কাছে নেওয়ার জন্য আপনি একটি সতর্ক রিপোর্ট পাবেন।")))
        st.button(L(T("Create my profile", "আমার প্রোফাইল তৈরি করুন")), type="primary", key="st_new",
                  on_click=go, args=("profile",))
        st.caption(L(T("Your data stays in this session only. Download your profile file to keep it.",
                       "আপনার তথ্য শুধু এই সেশনে থাকে। রাখতে চাইলে প্রোফাইল ফাইল নামিয়ে নিন।")))
    with card():
        st.subheader(L(T("Try a demo patient", "একজন ডেমো রোগীকে দিয়ে দেখুন")), anchor=False)
        st.caption(L(DEMO_LABEL))
        for k in ("rahim", "salma"):
            st.write(L(DEMO_INFO[k]))
            st.button(L(T("Open this demo", "এই ডেমো খুলুন")), key=f"st_demo_{k}", on_click=load_demo, args=(k,))
    with st.expander(L(T("I have a profile file", "আমার কাছে প্রোফাইল ফাইল আছে"))):
        _upload()


# ---------------------------------------------------------------- profile
def _data_tools():
    s = st.session_state
    with card():
        st.subheader(L(T("Your data", "আপনার তথ্য")), anchor=False)
        st.caption(L(T("Your data stays in this session only. Download your file to keep it, and load it next time.",
                       "আপনার তথ্য শুধু এই সেশনে থাকে। রাখতে ফাইল নামিয়ে নিন, পরের বার সেটি লোড করুন।")))
        st.download_button(lbl("export"), export_json(), file_name="my_profile.json", mime="application/json",
                           key="pf_export")
        if s.get("pf_confirm"):
            st.warning(L(T("This erases your profile and all records from this session. It cannot be undone.",
                           "এতে এই সেশনের প্রোফাইল ও সব রেকর্ড মুছে যাবে। এটি ফেরানো যাবে না।")))
            st.button(lbl("confirm_reset"), type="primary", key="pf_yes", on_click=reset)
            st.button(lbl("cancel"), key="pf_no", on_click=_flag, args=("pf_confirm", False))
        else:
            st.button(lbl("reset"), key="pf_reset", on_click=_flag, args=("pf_confirm", True))


def render_profile():
    s = st.session_state
    new = not P()
    p = {**blank_profile(), **P()}
    n = s.setdefault("pf_n", 0)  # bumps on save so widget keys never point at a shifted medicine list
    if s.pop("pf_msg", False):
        st.toast(L(T("Saved.", "সংরক্ষিত হয়েছে।")))

    def k(x):
        return f"pf{n}_{x}"

    title(T("Create my profile", "আমার প্রোফাইল তৈরি করুন") if new else NAV["profile"])
    if new:
        st.caption(L(T("This takes about two minutes. You can change everything later.",
                       "এতে প্রায় দুই মিনিট লাগে। সবকিছু পরে বদলাতে পারবেন।")))
        st.button(lbl("back"), key="pf_back", on_click=go, args=("dashboard",))
    units = ["mgdl", "mmol"]
    unit = st.radio(L(T("Sugar units", "সুগার মাপার একক")), units, index=units.index(p["units"]), horizontal=True,
                    format_func=lambda u: "mmol/L" if u == "mmol" else "mg/dL", key=k("units"))
    mm = unit == "mmol"
    ulab = "mmol/L" if mm else "mg/dL"
    t = p["target_range"]
    with st.form(f"pf_form_{n}"):
        name = st.text_input(L(T("Your name", "আপনার নাম")), value=p["name"], max_chars=60, key=k("name"))
        age = st.number_input(L(T("Age", "বয়স")), min_value=1, max_value=129, step=1,
                              value=_clip(int(p["age"]), 1, 129), key=k("age"))
        sex = st.selectbox(L(T("Sex", "লিঙ্গ")), list(SEX), index=list(SEX).index(p["sex"]),
                           format_func=lambda x: L(SEX[x]), key=k("sex"))
        dt = st.selectbox(L(T("Type of diabetes", "ডায়াবেটিসের ধরন")), list(DTYPE),
                          index=list(DTYPE).index(p["diabetes_type"]), format_func=lambda x: L(DTYPE[x]), key=k("dt"))
        yr = st.number_input(L(T("Year you were diagnosed (0 = not sure)", "যে বছর ধরা পড়েছে (০ = নিশ্চিত নই)")),
                             min_value=0, max_value=today().year, step=1, format="%d", key=k("yr"),
                             value=_clip(int(p["diagnosed_year"] or 0), 0, today().year))
        st.markdown(f"**{L(T('Medicines', 'ওষুধ'))}**")
        st.caption(L(T("Write each dose exactly as your doctor told you. We never calculate or change doses.",
                       "প্রতিটি ডোজ ডাক্তারের বলা অনুযায়ী হুবহু লিখুন। আমরা কখনো ডোজ হিসাব বা পরিবর্তন করি না।")))
        rows = []
        for i, m in enumerate(p["medicines"]):
            st.markdown(f"**{_esc(med_label(m.get('name')))}**")
            rows.append((m, _med_fields(k(f"m{i}"), m, True)))
        st.markdown(f"**{L(T('Add a medicine (optional)', 'একটি ওষুধ যোগ করুন (ঐচ্ছিক)'))}**")
        nm = _med_fields(k("new"), {"cls": "other"}, False)
        started = st.selectbox(L(T("When did you start it?", "কবে শুরু করেছেন?")), list(STARTED), key=k("start"),
                               format_func=lambda x: L(STARTED[x][0]))
        st.markdown(f"**{L(T('Your sugar target range', 'আপনার সুগারের লক্ষ্যসীমা'))}**")
        st.caption(L(T("Use the range your doctor gave you. If you have none, keep the default.",
                       "ডাক্তারের দেওয়া সীমা লিখুন। না থাকলে আগের মান রেখে দিন।")))
        kw = {"min_value": 1.0, "max_value": 40.0 if mm else 600.0, "step": 0.1 if mm else 1.0,
              "format": "%.1f" if mm else "%.0f"}
        lo = st.number_input(f"{L(T('Lowest', 'সর্বনিম্ন'))} ({ulab})", key=k(f"lo_{unit}"),
                             value=_clip(float(from_mgdl(t["low"], unit)), kw["min_value"], kw["max_value"]), **kw)
        hi = st.number_input(f"{L(T('Highest', 'সর্বোচ্চ'))} ({ulab})", key=k(f"hi_{unit}"),
                             value=_clip(float(from_mgdl(t["high"], unit)), kw["min_value"], kw["max_value"]), **kw)
        conds = st.multiselect(L(T("Other health conditions", "অন্যান্য শারীরিক সমস্যা")), list(COND), key=k("cond"),
                               default=[c for c in p["conditions"] if c in COND], format_func=lambda c: L(COND[c]))
        alg = st.text_input(L(T("Allergies, separated by commas", "অ্যালার্জি, কমা দিয়ে আলাদা করে লিখুন")),
                            value=", ".join(p["allergies"]), max_chars=200, key=k("alg"))
        hist = st.text_area(L(T("Other health history (optional)", "অন্যান্য স্বাস্থ্যের ইতিহাস (ঐচ্ছিক)")),
                            value=p["other_history"][-2000:], max_chars=2000, height=80, key=k("hist"))
        fl = st.checkbox(L(T("My doctor limits how much fluid I drink", "ডাক্তার আমার পানি পানের পরিমাণ সীমিত করেছেন")),
                         value=bool(p["fluid_limit"]), key=k("fl"))
        wt = st.number_input(L(T("Water target from your doctor, glasses a day (0 = none)",
                                 "ডাক্তারের দেওয়া পানির লক্ষ্য, দিনে কত গ্লাস (০ = নেই)")),
                             min_value=0, max_value=30, step=1, value=_clip(int(p["water_target"] or 0), 0, 30),
                             key=k("wt"))
        fast = st.checkbox(L(T("I am fasting now, for example Ramadan", "আমি এখন রোজা বা উপবাস রাখছি")),
                           value=bool(p["fasting_now"]), key=k("fast"))
        st.markdown(f"**{L(T('A trusted person for emergencies (optional)', 'জরুরি অবস্থার জন্য বিশ্বাসের একজন (ঐচ্ছিক)'))}**")
        cp = p["care_person"] or {}
        cname = st.text_input(L(T("Their name", "তাঁর নাম")), value=cp.get("name", ""), max_chars=60, key=k("cn"))
        cphone = st.text_input(L(T("Their phone number, with country code", "তাঁর ফোন নম্বর, দেশের কোড সহ")),
                               value=cp.get("phone", ""), max_chars=20, key=k("cph"))
        ok = st.form_submit_button(lbl("save"), type="primary")
    if ok:
        nl, nh = to_mgdl(lo, unit), to_mgdl(hi, unit)
        phone = _phone(cphone)
        err = None
        if not name.strip():
            err = T("Please write your name.", "অনুগ্রহ করে আপনার নাম লিখুন।")
        elif 0 < yr < 1930:
            err = T("The diagnosis year does not look right.", "ডায়াবেটিস ধরা পড়ার বছর ঠিক মনে হচ্ছে না।")
        elif not (TARGET_BOUNDS[0] <= nl < nh <= TARGET_BOUNDS[1]):
            err = T("The target range does not look right. Please check the two numbers.",
                    "লক্ষ্যসীমা ঠিক মনে হচ্ছে না। দুটি সংখ্যা আবার দেখুন।")
        elif (cname.strip() or cphone.strip()) and not phone:
            err = T("Please enter a valid phone number for your trusted person, with the country code.",
                    "বিশ্বাসের মানুষের জন্য দেশের কোড সহ সঠিক ফোন নম্বর লিখুন।")
        if err:
            st.error(L(err))
        else:
            meds = [{**m, "name": f["name"].strip() or m.get("name", ""), "cls": f["cls"],
                     "dose_text": f["dose"].strip(), "times": f["times"]} for m, f in rows if not f["stop"]]
            if nm["name"].strip():
                d = STARTED[started][1]
                meds.append({"name": nm["name"].strip(), "cls": nm["cls"], "dose_text": nm["dose"].strip(),
                             "times": nm["times"],
                             "start_date": (today() - timedelta(days=d)).isoformat() if d else None})
            set_profile({**P(), "name": name.strip(), "age": int(age), "sex": sex, "diabetes_type": dt,
                         "diagnosed_year": int(yr) or None, "medicines": meds,
                         "allergies": [a.strip()[:40] for a in re.split(r"[,;\n]", alg) if a.strip()][:10],
                         "conditions": conds, "other_history": hist.strip(), "units": unit,
                         "target_range": {"low": round(nl, 1), "high": round(nh, 1)},
                         "fluid_limit": bool(fl), "water_target": int(wt) or None, "fasting_now": bool(fast),
                         "care_person": {"name": cname.strip(), "phone": phone} if phone else None})
            s["pf_n"] = n + 1
            if new:
                go("dashboard")
            else:
                s["pf_msg"] = True
            st.rerun()
    if not new:
        _data_tools()
