"""Symptom guide, report, learn. Rules live in engine; this file only shows and collects. No JavaScript."""
import re

import streamlit as st

from ai import ask_json, ask_text, configured, explain, other_map, pick, symptom_map
from base import (APP_NAME, DISCLAIMER, EMERGENCY_NUMBER, NEW_CHAPTER_WINDOW_DAYS, SPECIALISTS, TIER_LABELS,
                  L, P, fmt_date, fmt_glucose, go, lang, logs, mark_seen, num, seen, to_date, today)
from content_learn import CARDS, CONFOUNDERS, EXPLAINERS, GLOSSARY
from content_q import QMODULES
from engine import (REMINDER_NOTE, T, TESTS, build_report, module_for_text, note_other, route_group,
                    save_answers, selfharm_text, text_triggers)
from ui import NAV, badge, card, disclaimer, lbl, scale_0_10, term, title

TREND = {"worse": T("worse than before", "আগের চেয়ে খারাপ"), "same": T("about the same", "প্রায় একই"),
         "better": T("better than before", "আগের চেয়ে ভালো"), "unknown": T("not enough information", "যথেষ্ট তথ্য নেই")}
ACTION = {
    "this_week": T("Please see your own diabetes doctor this week.", "এই সপ্তাহে আপনার নিজের ডায়াবেটিসের ডাক্তারকে দেখান।"),
    "next_visit": T("Tell your doctor at your next visit.", "পরের ভিজিটে ডাক্তারকে বলুন।"),
    "self_care": T("Keep up your self-care and keep logging. Tell your doctor if it continues.",
                   "নিজের যত্ন চালিয়ে যান এবং লিখে রাখুন। চলতে থাকলে ডাক্তারকে বলুন।")}
BUCKET = {"overdue": T("overdue", "দেরি হয়েছে"), "today": T("today", "আজ"), "week": T("this week", "এই সপ্তাহে")}
MODULE_TERMS = {"foot": "neuropathy", "night": "hypoglycemia", "thirst": "hyperglycemia"}  # glossary key shown per module
COND_TAGS = {"hypertension": ["hypertension"], "kidney_disease": ["kidney"], "heart_disease": ["heart"],
             "neuropathy_dx": ["neuropathy", "foot"], "retinopathy_dx": ["retinopathy", "eye"]}


def _esc(t):
    """Escape markdown so user or model text is shown as plain text."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|>~<$&])", r"\\\1", str(t or ""))


def _bullets(items):
    st.markdown("\n".join("- " + _esc(L(i)) for i in items))


def _emergency(group=None, crisis=False):
    """Route to the emergency view (same session keys as pages_safety.open_emergency), then stop this run."""
    s = st.session_state
    s["flag_group"], s["crisis"] = group, crisis
    go("emergency")
    st.rerun()


def _screen_text(text):
    """Any free text with self-harm or emergency words goes to the emergency/crisis route first."""
    if selfharm_text(text):
        _emergency(crisis=True)
    if text_triggers(text):
        _emergency()


# ================================================================ symptom guide
def _set(step):
    st.session_state.update({"sg_step": step, "sg_nomatch": False})


def _choose(k):
    st.session_state.update({"sg_module": k, "sg_step": "ask", "sg_nomatch": False})


def _guess(text):
    """Gemma first (validated against our module keys), then the keyword fallback. None if neither matches."""
    if configured():
        got = pick(ask_json(symptom_map(text, QMODULES)), "module", QMODULES)
        if got:
            return got[0]
    return module_for_text(text)


def _map_other(text, q):
    if not configured():
        return None
    got = pick(ask_json(other_map(text, q["options"])), "option_id", [o["id"] for o in q["options"]])
    return got[0] if got else None


def _pick():
    s = st.session_state
    if s.get("sg_nomatch"):
        n = num(EMERGENCY_NUMBER)
        st.info(L(T(f"We could not match this to our topics. Please ask a doctor or pharmacist. For emergencies call {n}.",
                    f"এটি আমাদের বিষয়গুলোর সাথে মেলাতে পারিনি। অনুগ্রহ করে ডাক্তার বা ফার্মাসিস্টকে জিজ্ঞাসা করুন। "
                    f"জরুরি অবস্থায় {n} নম্বরে ফোন করুন।")))
    with card():
        txt = st.text_area(L(T("Tell us in your own words what you notice", "আপনি কী অনুভব করছেন নিজের কথায় লিখুন")),
                           max_chars=300, height=90, key="sg_text")
        if st.button(L(T("Find the right questions", "সঠিক প্রশ্ন খুঁজুন")), type="primary", key="sg_find"):
            t = txt.strip()
            if not t:
                st.warning(L(T("Please write a few words, or choose a topic below.",
                               "অল্প কিছু লিখুন, অথবা নিচ থেকে একটি বিষয় বেছে নিন।")))
            else:
                _screen_text(t)
                with st.spinner(L(T("Reading your words...", "আপনার লেখা পড়া হচ্ছে..."))):
                    mod = _guess(t)
                s["sg_nomatch"] = mod is None
                if mod:
                    s["sg_module"], s["sg_step"] = mod, "confirm"
                st.rerun()
    st.markdown(f"**{L(T('Or choose a topic', 'অথবা একটি বিষয় বেছে নিন'))}**")
    for k, m in QMODULES.items():
        st.button(L(m["title"]), key=f"sg_topic_{k}", on_click=_choose, args=(k,))


def _confirm(k):
    with card():
        st.markdown(f"**{L(T('I understood:', 'আমি যা বুঝেছি:'))}** {L(QMODULES[k]['title'])}")
        st.write(L(T("Is that right?", "এটি কি ঠিক?")))
        st.button(lbl("yes"), type="primary", key="sg_yes", on_click=_choose, args=(k,))
        st.button(L(T("No, let me choose", "না, আমি নিজে বেছে নিই")), key="sg_no", on_click=_set, args=("pick",))


def _question(k, q):
    key = f"sg_{k}_{q['id']}"
    if q["type"] == "scale":
        a = scale_0_10(q["text"], key)
    else:
        lab = {o["id"]: L(o["label"]) for o in q["options"]}
        a = st.radio(L(q["text"]), list(lab), index=None, format_func=lambda i: lab[i], key=key)
    if q["id"] == "f_loss":  # numbness without pain is NOT reassuring
        st.info(L(T("Numbness without pain is NOT reassuring. You may not feel an injury.",
                    "ব্যথা ছাড়া অসাড়ভাব নিশ্চিন্ত থাকার কারণ নয়। আঘাত টের নাও পেতে পারেন।")))
    other = ""
    if q.get("other"):
        other = st.text_input(f"{lbl('other')} ({L(T('optional', 'ঐচ্ছিক'))})", max_chars=150, key=key + "_o")
    with st.expander(lbl("why_asked")):
        st.write(L(q["why"]))
    return a, other.strip()


def _submit(k, m, answers, others):
    qs = m["questions"]
    if not (others or any((answers[q["id"]] > 0) if q["type"] == "scale" else (answers[q["id"]] is not None)
                          for q in qs)):
        st.warning(L(T("Please answer at least one question.", "অন্তত একটি প্রশ্নের উত্তর দিন।")))
        return
    for t in others.values():  # emergency or crisis words in any box: route first, save nothing
        _screen_text(t)
    final = {qid: a for qid, a in answers.items() if a is not None}
    with st.spinner(L(T("Saving...", "সংরক্ষণ হচ্ছে..."))):
        for qid, t in others.items():
            q = next(x for x in qs if x["id"] == qid)
            opt = _map_other(t, q)
            if opt and qid not in final:
                final[qid] = opt
            else:
                note_other(t)  # not mapped: kept verbatim in the neutral "other things you noted" list
    save_answers(k, final)
    st.session_state["sg_step"] = "done"
    grp = route_group(k, final)  # e.g. vomiting with high sugar: red-flag check comes first
    if grp:
        _emergency(group=grp)
    st.rerun()


def _ask(k):
    m = QMODULES[k]
    st.subheader(L(m["title"]), anchor=False)
    st.write(L(m["intro"]))
    st.caption(L(T("You can skip any question you prefer not to answer.",
                   "যে প্রশ্নের উত্তর দিতে চান না তা বাদ দিতে পারেন।")))
    answers, others = {}, {}
    for q in m["questions"]:
        with card():
            answers[q["id"]], o = _question(k, q)
            if o:
                others[q["id"]] = o
    if st.button(lbl("save"), type="primary", key="sg_save"):
        _submit(k, m, answers, others)
    st.button(lbl("back"), key="sg_back", on_click=_set, args=("pick",))


def _done():
    with card():
        st.success(L(T("Saved. Your answers will appear in your report.", "সংরক্ষিত হয়েছে। আপনার উত্তর রিপোর্টে দেখা যাবে।")))
        st.caption(L(T("This is not a diagnosis. Your report lists possible reasons and questions for your doctor.",
                       "এটি রোগনির্ণয় নয়। রিপোর্টে সম্ভাব্য কারণ ও ডাক্তারের জন্য প্রশ্ন থাকবে।")))
        st.button(lbl("see_report"), type="primary", key="sg_report", on_click=go, args=("report",))
        st.button(L(T("Check another topic", "আরেকটি বিষয় দেখুন")), key="sg_again", on_click=_set, args=("pick",))


def render_symptom():
    s = st.session_state
    title(NAV["symptom"], T("Answer a few fixed questions. This is not a diagnosis.",
                            "কয়েকটি নির্দিষ্ট প্রশ্নের উত্তর দিন। এটি রোগনির্ণয় নয়।"))
    step, k = s.get("sg_step", "pick"), s.get("sg_module")
    if step in ("confirm", "ask") and k not in QMODULES:
        step = "pick"
    if step == "confirm":
        _confirm(k)
    elif step == "ask":
        _ask(k)
    elif step == "done":
        _done()
    else:
        _pick()


# ================================================================ report
def _facts(it):
    out = []
    if it["present_days"]:
        out.append(L(T(f"Noticed for about {num(it['present_days'])} days",
                       f"প্রায় {num(it['present_days'])} দিন ধরে লক্ষ করা গেছে")))
    if it["avg_severity"] is not None:
        a = num(it["avg_severity"])
        out.append(L(T(f"Average strength: {a} out of {num(10)}", f"গড় তীব্রতা: {num(10)} এর মধ্যে {a}")))
    out.append(f"{L(T('Trend', 'ধারা'))}: {L(TREND.get(it['trend'], TREND['unknown']))}")
    return out


def _refer(sp):
    s = SPECIALISTS[sp]
    return T(f"Your doctor may refer you to {s['en']}.", f"আপনার ডাক্তার আপনাকে {s['bn']}ের কাছে পাঠাতে পারেন।")


def _item(it):
    with card():
        badge(it["tier"])
        st.subheader(L(it["title"]), anchor=False)
        st.write(L(ACTION[it["tier"]]))
        if it["specialist"] in SPECIALISTS:  # only on a this_week item
            st.write(L(_refer(it["specialist"])))
        _bullets(_facts(it))
        if it["reasons"]:
            with st.expander(L(T("Why this is shown", "এটি কেন দেখানো হচ্ছে")), expanded=it["tier"] == "this_week"):
                _bullets(it["reasons"])
        conf = [c for c in it["confounders"] if c in CONFOUNDERS]
        if conf:
            with st.expander(L(T("Other possible reasons", "অন্য সম্ভাব্য কারণ"))):
                term("confounder")
                _bullets([CONFOUNDERS[c] for c in conf])
        if it["module"] in MODULE_TERMS:
            term(MODULE_TERMS[it["module"]])


def _report_text(r):
    out = [f"{APP_NAME}: {L(NAV['report'])}", fmt_date(r["generated"]), ""]
    if P().get("name"):
        out += [str(P()["name"]), ""]
    for it in r["items"]:
        out.append(f"[{L(TIER_LABELS[it['tier']])}] {L(it['title'])}")
        out += ["  - " + L(x) for x in it["reasons"]]
        conf = [L(CONFOUNDERS[c]) for c in it["confounders"] if c in CONFOUNDERS]
        if conf:
            out.append(f"  {L(T('Other possible reasons', 'অন্য সম্ভাব্য কারণ'))}: " + ", ".join(conf))
        out.append("")
    for head, rows in ((T("About your medicine", "আপনার ওষুধ সম্পর্কে"), r["med_notes"]),
                       (T("Questions to ask your doctor", "ডাক্তারকে যে প্রশ্নগুলো করবেন"), r["doctor_questions"]),
                       (T("Other things you noted", "আপনার জানানো অন্যান্য বিষয়"), r["other_noted"])):
        if rows:
            out += [L(head)] + ["  - " + L(x) for x in rows] + [""]
    if r["tests_due"]:
        out += [L(T("Tests coming up", "যেসব পরীক্ষার সময় আসছে"))]
        out += [f"  - {L(TESTS[i['key']]['title'])}: {fmt_date(i['due'])}" for i in r["tests_due"] if i["key"] in TESTS]
        out.append("")
    return "\n".join(out + [L(DISCLAIMER)])


def render_report():
    r = build_report()
    d = fmt_date(r["generated"])
    title(NAV["report"], T(f"Prepared on {d}", f"প্রস্তুতের তারিখ: {d}"))
    st.caption(L(T("Bring this to your own diabetes doctor. It shows patterns, not a diagnosis.",
                   "এটি আপনার নিজের ডায়াবেটিসের ডাক্তারের কাছে নিয়ে যান। এতে ধরন দেখানো হয়েছে, রোগনির্ণয় নয়।")))
    if r["items"]:
        st.subheader(L(T("What we noticed", "আমরা যা লক্ষ করেছি")), anchor=False)
        for it in r["items"]:
            _item(it)
    else:
        with card():
            st.info(L(T("Nothing stands out from what you have shared so far. Keep logging, and use the Symptom guide "
                        "if something worries you.",
                        "এ পর্যন্ত আপনার দেওয়া তথ্যে বিশেষ কিছু চোখে পড়েনি। লিখে রাখতে থাকুন, কিছু নিয়ে চিন্তা হলে উপসর্গ গাইড দেখুন।")))
            st.button(L(NAV["symptom"]), key="rp_to_sym", on_click=go, args=("symptom",))
    if r["med_notes"]:
        with card():
            st.subheader(L(T("About your medicine", "আপনার ওষুধ সম্পর্কে")), anchor=False)
            _bullets(r["med_notes"])
    g = r["glucose_summary"]
    if g["n"]:
        with card():
            st.subheader(L(T(f"Your sugar, last {num(14)} days", f"আপনার সুগার, গত {num(14)} দিন")), anchor=False)
            _bullets([T(f"Readings: {num(g['n'])}", f"মাপ: {num(g['n'])} বার"),
                      T(f"Average: {fmt_glucose(g['avg'])}", f"গড়: {fmt_glucose(g['avg'])}"),
                      T(f"In your range: {num(g['tir_pct'])}%", f"আপনার সীমার মধ্যে: {num(g['tir_pct'])}%"),
                      T(f"Low readings: {num(g['lows'])}", f"কম মাপ: {num(g['lows'])} বার"),
                      T(f"High readings: {num(g['highs'])}", f"বেশি মাপ: {num(g['highs'])} বার")])
    if r["tests_due"]:
        with card():
            st.subheader(L(T("Tests coming up", "যেসব পরীক্ষার সময় আসছে")), anchor=False)
            _bullets([T(f"{TESTS[i['key']]['title']['en']}: {fmt_date(i['due'])} ({L(BUCKET[i['bucket']])})",
                        f"{TESTS[i['key']]['title']['bn']}: {fmt_date(i['due'])} ({L(BUCKET[i['bucket']])})")
                      for i in r["tests_due"] if i["key"] in TESTS and i.get("bucket") in BUCKET])
            st.caption(L(REMINDER_NOTE))
    with st.expander(L(T("Questions to ask your doctor", "ডাক্তারকে যে প্রশ্নগুলো করবেন")), expanded=True):
        _bullets(r["doctor_questions"])
    if r["other_noted"]:
        with st.expander(L(T("Other things you noted", "আপনার জানানো অন্যান্য বিষয়"))):
            st.caption(L(T("Listed as you wrote them. We do not interpret them.",
                           "আপনার লেখা অনুযায়ীই দেওয়া হয়েছে। আমরা এর ব্যাখ্যা করি না।")))
            _bullets(r["other_noted"])
    st.download_button(L(T("Download this report (text file)", "রিপোর্ট নামান (লেখা ফাইল)")), _report_text(r),
                       file_name="report.txt", mime="text/plain", key="rp_dl")
    st.button(L(T("Check more symptoms", "আরও উপসর্গ দেখুন")), key="rp_more", on_click=go, args=("symptom",))
    disclaimer()


# ================================================================ learn
def _tags():
    p, tags = P(), set()
    if any(str(m.get("cls", "")).startswith("insulin") for m in p.get("medicines", [])):
        tags.add("insulin")
    for c in p.get("conditions", []):
        tags.update(COND_TAGS.get(c, []))
    if any(e.get("module") == "foot" for e in logs("symptom", 14)):
        tags.update({"foot", "neuropathy"})
    return tags


def _new(cid, added):
    """New if never seen and added within the window, or added after the date it was last seen."""
    try:
        age = (today() - to_date(added)).days
    except ValueError:
        return False
    last = seen().get(cid)
    return age <= NEW_CHAPTER_WINDOW_DAYS if not last else str(last)[:10] < str(added)[:10]


def _label(c_title, is_new, mine):
    tags = ([L(T("New", "নতুন"))] if is_new else []) + ([L(T("For you", "আপনার জন্য"))] if mine else [])
    return L(c_title) + (f"  ·  {' · '.join(tags)}" if tags else "")


def _card_body(c):
    st.write(L(c["simple"]))
    for head, rows in ((T("Signs to watch for", "যেসব লক্ষণে নজর রাখবেন"), c["signs"]),
                       (T("What you can do", "আপনি যা করতে পারেন"), c["tips"])):
        if rows:
            st.markdown(f"**{L(head)}**")
            _bullets(rows)
    st.markdown(f"**{L(T('When to get help', 'কখন সাহায্য নেবেন'))}**")
    st.warning(L(c["see_doctor"]))
    if c.get("myth"):
        st.markdown(f"**{L(T('Myth', 'ভুল ধারণা'))}:** {_esc(L(c['myth']['myth']))}")
        st.markdown(f"**{L(T('Fact', 'সত্য'))}:** {_esc(L(c['myth']['fact']))}")


def _explainer(key, e, is_new):
    s = st.session_state
    with st.expander(_label(e["title"], is_new, False)):
        st.markdown(f"**{L(e['analogy'])}**")
        st.write(L(e["simple"]))
        more = st.toggle(L(T("More detail", "আরও বিস্তারিত")), key=f"lx_more_{key}")
        if more:
            st.write(L(e["detailed"]))
        if not configured():
            return
        depth = "detailed" if more else "simple"
        ok = f"lx_out_{key}_{lang()}_{depth}"
        if st.button(L(T("Say it another way (AI)", "অন্যভাবে বলুন (এআই)")), key=f"lx_ai_{key}"):
            fact = f"{L(e['analogy'])} {L(e['simple'])} {L(e['detailed'])}"  # Gemma only rephrases this fact sheet
            with st.spinner(L(T("Thinking...", "ভাবছি..."))):
                s[ok] = ask_text(explain(fact, depth)) or ""
        if s.get(ok):
            st.markdown(_esc(s[ok]))
            st.caption(L(T("Rephrased by AI from the text above. It adds no new advice.",
                           "উপরের লেখা থেকে এআই আবার বলেছে। নতুন কোনো পরামর্শ যোগ করা হয়নি।")))
        elif ok in s:
            st.caption(L(T("The AI could not answer now. The text above is still correct.",
                           "এখন এআই উত্তর দিতে পারেনি। উপরের লেখাটি তবুও সঠিক।")))


def render_learn():
    title(NAV["learn"], T("Short, plain explanations. Tap to open.", "ছোট ও সহজ ব্যাখ্যা। খুলতে ট্যাপ করুন।"))
    tags = _tags()
    new = {c["id"] for c in CARDS if _new(c["id"], c["added_on"])}
    new |= {k for k, e in EXPLAINERS.items() if _new(k, e["added_on"])}
    t1, t2, t3 = st.tabs([L(T("Guides", "গাইড")), L(T("Explainers", "ব্যাখ্যা")), L(T("Words", "শব্দার্থ"))])
    with t1:
        order = sorted(enumerate(CARDS), key=lambda t: (-len((set(t[1]["relevance"]) - {"any"}) & tags), t[0]))
        for _, c in order:
            mine = bool((set(c["relevance"]) - {"any"}) & tags)
            with st.expander(_label(c["title"], c["id"] in new, mine)):
                _card_body(c)
    with t2:
        for k, e in EXPLAINERS.items():
            _explainer(k, e, k in new)
    with t3:
        for k in GLOSSARY:
            term(k)
    mark_seen([c["id"] for c in CARDS] + list(EXPLAINERS))  # shown now, so not "new" next time
