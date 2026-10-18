"""Presentation layer: CSS constant + helpers. Imports base and content_learn only. No JavaScript."""
from contextlib import contextmanager
from urllib.parse import quote

import streamlit as st

from base import DISCLAIMER, L, TIER_LABELS, lang, num
from content_learn import GLOSSARY

QUOTA_HOURS = 4

# ---------------------------------------------------------------- shared labels
NAV = {
    "dashboard": {"en": "Dashboard", "bn": "ড্যাশবোর্ড"},
    "symptom": {"en": "Symptom guide", "bn": "উপসর্গ গাইড"},
    "learn": {"en": "Learn", "bn": "শিখুন"},
    "report": {"en": "Report", "bn": "রিপোর্ট"},
    "profile": {"en": "My profile", "bn": "আমার প্রোফাইল"},
}
LABELS = {
    "emergency": {"en": "Emergency", "bn": "জরুরি"},
    "save": {"en": "Save", "bn": "সংরক্ষণ করুন"},
    "back": {"en": "Back", "bn": "পিছনে"},
    "next": {"en": "Next", "bn": "পরের ধাপ"},
    "cancel": {"en": "Cancel", "bn": "বাতিল"},
    "yes": {"en": "Yes", "bn": "হ্যাঁ"},
    "no": {"en": "No", "bn": "না"},
    "other": {"en": "Other", "bn": "অন্য কিছু"},
    "mark_done": {"en": "Mark done", "bn": "হয়েছে বলে চিহ্নিত করুন"},
    "why_asked": {"en": "Why am I asked this?", "bn": "এটি কেন জিজ্ঞাসা করা হচ্ছে?"},
    "in_simple_words": {"en": "In simple words", "bn": "সহজ কথায়"},
    "see_report": {"en": "See my report", "bn": "আমার রিপোর্ট দেখুন"},
    "export": {"en": "Download my profile file", "bn": "আমার প্রোফাইল ফাইল নামান"},
    "reset": {"en": "Reset my data", "bn": "আমার তথ্য মুছে ফেলুন"},
    "confirm_reset": {"en": "Yes, erase everything", "bn": "হ্যাঁ, সব মুছে ফেলুন"},
}
SCALE = {
    "none": {"en": "none", "bn": "নেই"},
    "mild": {"en": "mild", "bn": "হালকা"},
    "moderate": {"en": "moderate", "bn": "মাঝারি"},
    "severe": {"en": "severe", "bn": "তীব্র"},
}


def lbl(key):
    return L(LABELS.get(key))


# ---------------------------------------------------------------- CSS (the only unsafe_allow_html use)
CSS = """@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');
:root{--bg:#F5F5F7;--card:#FFFFFF;--text:#1D1D1F;--muted:#6E6E73;--hair:rgba(0,0,0,.08);--accent:#0F766E;--danger:#C62828;--warn-bg:#FFF4E0;--warn:#B45309;--info-bg:#EEF5FF;--info:#0A5FBF;--ok-bg:#EEF7F0;--ok:#2F6B46;--r1:10px;--r2:16px;--shadow:0 1px 2px rgba(0,0,0,.04),0 4px 16px rgba(0,0,0,.06);--ease:cubic-bezier(.2,.8,.2,1);--anim:rise 220ms var(--ease)}
@keyframes rise{from{opacity:0;transform:translateY(6px) scale(.99)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
.stApp,[data-testid="stAppViewContainer"]{background:var(--bg);color:var(--text)}
.stApp,.stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea,.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",system-ui,"Noto Sans Bengali",sans-serif}
.stApp p,.stApp li,.stApp label{line-height:var(--lh-body);letter-spacing:var(--track-small)}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{line-height:var(--lh-head);letter-spacing:var(--track-large);font-weight:700;color:var(--text)}
.stApp h1{font-size:2rem}.stApp h2{font-size:1.5rem}.stApp h3{font-size:1.25rem}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted);font-size:.8125rem}
.block-container{max-width:720px;padding:4rem 1rem 6rem}
[data-testid="stElementContainer"]:has(style){display:none}
.stApp :is(.stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a){min-height:2.75rem;border-radius:var(--r1);font-weight:600;transition:transform 100ms ease-out,opacity 100ms ease-out}
.stApp :is(.stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a):hover{opacity:.9}
.stApp :is(.stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a):active{transform:scale(.97);transition:transform 100ms ease-out}
.stApp :is(button,a,input,textarea,summary,[role="radio"],[role="tab"]):focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.stApp [data-testid="stBaseButton-primary"],.stApp [data-testid="stBaseLinkButton-primary"]{background:var(--accent);border-color:var(--accent);color:#fff}
.stApp [data-testid="stBaseButton-secondary"],.stApp [data-testid="stBaseLinkButton-secondary"]{background:var(--card);border:1px solid var(--hair);color:var(--text)}
.stApp .st-key-emergency_btn :is(button,a){background:var(--danger);border:1px solid var(--danger);color:#fff}
.stApp .st-key-emergency_btn p{color:#fff}
.stApp :is([data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div){border-radius:var(--r1)}
[data-testid="stVerticalBlockBorderWrapper"][class*="st-key-card_"],[data-testid="stVerticalBlockBorderWrapper"]:has(>[class*="st-key-card_"]){background:var(--card);border:1px solid var(--hair);border-radius:var(--r2);box-shadow:var(--shadow);padding:1rem;animation:var(--anim)}
[data-testid="stExpander"]{background:var(--card);border:1px solid var(--hair);border-radius:var(--r2);box-shadow:var(--shadow);overflow:hidden;animation:var(--anim)}
[data-testid="stExpander"] details{border:0}
[data-testid="stAlert"]{border-radius:var(--r1);animation:var(--anim)}
[class*="st-key-badge-"]{width:fit-content;padding:.25rem .75rem;border-radius:var(--r1);font-size:.875rem;font-weight:600}
[class*="st-key-badge-"] p{color:inherit;margin:0;font-size:.875rem}
[class*="st-key-badge-emergency-"]{background:var(--danger);color:#fff}
[class*="st-key-badge-this_week-"]{background:var(--warn-bg);color:var(--warn)}
[class*="st-key-badge-next_visit-"]{background:var(--info-bg);color:var(--info)}
[class*="st-key-badge-self_care-"]{background:var(--ok-bg);color:var(--ok)}
[data-testid="stSidebar"]{background:rgba(255,255,255,.72);-webkit-backdrop-filter:blur(20px) saturate(180%);backdrop-filter:blur(20px) saturate(180%);border-right:1px solid var(--hair);box-shadow:inset 0 1px 0 rgba(255,255,255,.9)}
[data-testid="stSidebarContent"],[data-testid="stSidebarHeader"]{background:transparent}
[data-testid="stHeader"]{background:rgba(255,255,255,.72);-webkit-backdrop-filter:blur(20px) saturate(180%);backdrop-filter:blur(20px) saturate(180%);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 1px 0 var(--hair)}
@media (max-width:640px){.block-container{padding:3.5rem .75rem 5rem}[data-testid="stLinkButton"],[data-testid="stLinkButton"] a{width:100%}}
@media (prefers-reduced-motion:reduce){:root{--anim:fade 150ms ease-out}.stApp :is(.stButton button,.stDownloadButton button,[data-testid="stLinkButton"] a):active{transform:none}}
@media (prefers-reduced-transparency:reduce){[data-testid="stSidebar"],[data-testid="stHeader"]{background:#FFFFFF;-webkit-backdrop-filter:none;backdrop-filter:none}}
@media (prefers-contrast:more){:root{--hair:rgba(0,0,0,.6);--muted:#3A3A3C}[data-testid="stSidebar"],[data-testid="stHeader"]{background:rgba(255,255,255,.96)}[class*="st-key-badge-"]{border:1px solid currentColor}}"""

_VARS = {
    "en": ":root{--lh-body:1.5;--lh-head:1.15;--track-large:-0.02em;--track-small:0.01em}",
    "bn": ":root{--lh-body:1.75;--lh-head:1.4;--track-large:0;--track-small:0}",
}


def inject_css():
    """Call once at the top of every run (it also resets the key counter used by card/badge)."""
    st.session_state["_ui_n"] = 0
    st.markdown(f"<style>{CSS}{_VARS.get(lang(), _VARS['en'])}</style>", unsafe_allow_html=True)


def _n():
    n = st.session_state.get("_ui_n", 0) + 1
    st.session_state["_ui_n"] = n
    return n


# ---------------------------------------------------------------- helpers
@contextmanager
def card():
    with st.container(border=True, key=f"card_{_n()}"):
        yield


def title(text, sub=None):
    st.header(L(text), anchor=False)
    if sub:
        st.caption(L(sub))


def badge(tier):
    t = tier if tier in TIER_LABELS else "self_care"
    with st.container(key=f"badge-{t}-{_n()}"):
        st.markdown(f"**{L(TIER_LABELS[t])}**")


def scale_0_10(label, key):
    kw = {} if key in st.session_state else {"value": 0}
    v = st.select_slider(L(label), options=list(range(11)), key=key, format_func=num, **kw)
    s = {k: L(x) for k, x in SCALE.items()}
    st.caption(f"{num(0)} {s['none']} · {num(1)}-{num(3)} {s['mild']} · "
               f"{num(4)}-{num(6)} {s['moderate']} · {num(7)}-{num(10)} {s['severe']}")
    return int(v)


def term(key):
    g = GLOSSARY.get(key)
    if g:
        st.caption(f"**{L(g.get('term'))}** - {lbl('in_simple_words')}: {L(g.get('simple'))}")


def disclaimer():
    if st.session_state.get("ai_limit"):
        st.info(L({"en": f"AI help has reached its limit for now. Please try again after about {QUOTA_HOURS} hours. "
                         "Everything else works as usual.",
                   "bn": f"এআই সহায়তা আপাতত সীমায় পৌঁছেছে। প্রায় {num(QUOTA_HOURS)} ঘণ্টা পরে আবার চেষ্টা করুন। "
                         "বাকি সবকিছু আগের মতোই চলবে।"}))
    st.caption(L(DISCLAIMER))


def link_button(label, url, kind="secondary"):
    label = L(label)
    try:
        st.link_button(label, url, type="primary" if kind == "primary" else "secondary")
    except Exception:  # scheme rejected: plain markdown link
        st.markdown(f"[{label}]({quote(str(url), safe=':/?&=#+@%')})")
