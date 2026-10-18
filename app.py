"""Entry point: page config, language gate, header, sidebar, routing. No logic beyond routing."""
import streamlit as st

st.set_page_config(page_title="APP_NAME", layout="centered", initial_sidebar_state="auto")  # must be first

from base import APP_NAME, EMERGENCY_NUMBER, LANGS, L, P, go, init_state, lang, set_lang
from engine import ensure_defaults
from pages_guide import render_learn, render_report, render_symptom
from pages_home import render_dashboard, render_profile, render_start
from pages_safety import open_emergency, render_emergency
from ui import NAV, disclaimer, inject_css, lbl, link_button, title

VIEWS = {"dashboard": render_dashboard, "symptom": render_symptom, "learn": render_learn,
         "report": render_report, "profile": render_profile, "emergency": render_emergency}
NO_PROFILE_OK = ("emergency", "profile")  # every other view needs a profile


def _gate():
    """First run: pick a language. Emergency call stays reachable from here."""
    title(APP_NAME, "Choose your language / ভাষা বেছে নিন")
    for code, name in LANGS.items():
        st.button(name, key=f"gate_{code}", type="primary", use_container_width=True,
                  on_click=set_lang, args=(code,))
    link_button(f"Emergency / জরুরি: {EMERGENCY_NUMBER}", f"tel:{EMERGENCY_NUMBER}", "secondary")


def _header():
    """Same positions on every screen: name left, Emergency middle, language right."""
    c1, c2, c3 = st.columns([4, 3, 4], vertical_alignment="center")
    c1.subheader(APP_NAME, anchor=False)
    c2.button(lbl("emergency"), key="emergency_btn", use_container_width=True, on_click=open_emergency)
    codes = list(LANGS)
    c3.radio(L({"en": "Language", "bn": "ভাষা"}), codes, index=codes.index(lang()), horizontal=True,
             format_func=LANGS.get, key="lang_radio", label_visibility="collapsed",
             on_change=lambda: set_lang(st.session_state["lang_radio"]))


def _sidebar(view):
    with st.sidebar:
        for k, label in NAV.items():
            st.button(L(label), key=f"nav_{k}", use_container_width=True,
                      type="primary" if view == k else "secondary", on_click=go, args=(k,))


def main():
    init_state()
    inject_css()  # first on every run: it also resets the card/badge key counter
    if not st.session_state.get("lang"):
        _gate()
        return
    _header()
    view = st.session_state.get("view")
    if view not in VIEWS:
        view = "dashboard"
    has_profile = bool(P())
    if has_profile:
        ensure_defaults()  # idempotent: adds a reminder only for a test with no open one
        _sidebar(view)
    if not has_profile and view not in NO_PROFILE_OK:
        render_start()
    else:
        VIEWS[view]()
    if view != "report":  # render_report draws its own disclaimer
        disclaimer()


main()
