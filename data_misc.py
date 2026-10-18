"""Foods, matching and demo patients (all demo data fictional). Imports base and ai."""
import difflib
import re
from datetime import timedelta

from ai import ask_json, configured, food_parse, pick
from base import DEFAULT_TARGET, L, P, TEST_INTERVALS, now, today


def T(en, bn):
    return {"en": en, "bn": bn}


# ---------------------------------------------------------------- foods
_AL = {}  # food id -> extra spellings used for matching (en + bn)


def _f(i, en, bn, carb, al="", sugar=False, allergens=(), mixed=False):
    _AL[i] = [a for a in al.split("|") if a]
    return {"id": i, "name": T(en, bn), "carb": carb, "sugar": sugar,
            "allergens": list(allergens), "mixed": mixed}


FOODS = [  # carb levels are rough guides  # VERIFY
    _f("bhat", "Rice (bhat)", "ভাত", "high", "rice|bhat"),
    _f("ruti", "Flatbread (ruti)", "রুটি", "med", "roti|ruti|chapati|chapatti", allergens=["gluten"]),
    _f("paratha", "Paratha", "পরোটা", "high", "paratha|porota|পরাটা", allergens=["gluten"]),
    _f("khichuri", "Khichuri", "খিচুড়ি", "high", "khichuri|khichdi|খিচুড়ী", mixed=True),
    _f("dal", "Dal (lentils)", "ডাল", "med", "dal|daal|lentil|lentils"),
    _f("shak", "Leafy greens (shak)", "শাক", "low", "shak|saag|spinach|greens"),
    _f("machh", "Fish curry (machh)", "মাছের তরকারি", "low", "fish|machh|mach|fish curry|মাছ",
       allergens=["fish"], mixed=True),
    _f("murgi", "Chicken curry (murgi)", "মুরগির তরকারি", "low", "chicken|murgi|chicken curry|মুরগি|মুরগী",
       mixed=True),
    _f("egg", "Egg", "ডিম", "low", "egg|eggs|dim", allergens=["egg"]),
    _f("alu_bhorta", "Mashed potato (alu bhorta)", "আলু ভর্তা", "med", "alu bhorta|aloo bhorta|mashed potato|potato|alu|আলু"),
    _f("begun", "Brinjal (begun)", "বেগুন ভাজা", "low", "begun|brinjal|eggplant|বেগুন"),
    _f("biryani", "Biryani", "বিরিয়ানি", "high", "biryani|biriyani|বিরিয়ানী", mixed=True),
    _f("tehari", "Tehari", "তেহারি", "high", "tehari|tehri|তেহারী", mixed=True),
    _f("muri", "Puffed rice (muri)", "মুড়ি", "high", "muri|puffed rice"),
    _f("chira", "Flattened rice (chira)", "চিড়া", "high", "chira|chida|flattened rice|চিঁড়া"),
    _f("pitha", "Pitha", "পিঠা", "high", "pitha|pithe|পিঠে", sugar=True, mixed=True),
    _f("mishti", "Sweets (mishti)", "মিষ্টি", "high", "mishti|misti|sweets|sweet", True, ["milk"], True),
    _f("rasgulla", "Rasgulla", "রসগোল্লা", "high", "rasgulla|roshogolla|rosogolla", True, ["milk"]),
    _f("jilapi", "Jilapi", "জিলাপি", "high", "jilapi|jalebi|jilebi|জিলাপী", True, ["gluten"]),
    _f("payesh", "Payesh (rice pudding)", "পায়েস", "high", "payesh|kheer", True, ["milk"], True),
    _f("banana", "Banana", "কলা", "med", "banana|kola"),
    _f("mango", "Mango", "আম", "high", "mango|aam", sugar=True),
    _f("guava", "Guava", "পেয়ারা", "low", "guava|peyara|payara"),
    _f("tea_sugar", "Tea with sugar", "চিনি দিয়ে চা", "med", "tea|cha|sugar tea|sweet tea|চা", sugar=True),
    _f("soft_drink", "Soft drink", "কোমল পানীয়", "high",
       "soft drink|cola|coke|pepsi|sprite|fanta|7up|কোলা|কোক|পেপসি", sugar=True),
    _f("singara", "Singara (samosa)", "সিঙ্গারা", "high", "singara|samosa|সমুচা", allergens=["gluten"], mixed=True),
    _f("peanut", "Peanuts", "চিনাবাদাম", "low", "peanut|peanuts|groundnut|badam|বাদাম", allergens=["peanut"]),
    _f("doi", "Plain yogurt (doi)", "দই", "low", "yogurt|yoghurt|curd|doi", allergens=["milk"]),
    _f("shosha", "Cucumber (shosha)", "শসা", "low", "cucumber|shosha"),
    _f("sobji", "Mixed vegetables (sobji)", "সবজি", "low", "vegetables|vegetable|sobji|sabji|veg curry", mixed=True),
]
BY_ID = {f["id"]: f for f in FOODS}
_BNS = {"", "ের", "র", "ে", "ও", "টা", "টি", "টাও", "গুলো", "গুলি", "তে", "য়"}  # Bangla endings after a food word


def _hit(alias, toks, text):
    if " " in alias:
        return alias in text
    for w in toks:
        if w == alias:
            return True
        if alias.isascii():
            if w in (alias + "s", alias + "es"):
                return True
            if len(alias) >= 5 and difflib.SequenceMatcher(None, alias, w).ratio() >= 0.84:
                return True
        elif w.startswith(alias) and w[len(alias):] in _BNS:  # stops "আম" matching "আমি"
            return True
    return False


def match_foods(text):
    """Local matching first (en + bn names, aliases, close spellings). Gemma only if nothing matched."""
    t = " ".join(str(text or "").lower().split())[:300]
    toks = [w for w in re.split(r"[\s,;.!?()/+&:\-\"']+", t) if w]
    out = [f for f in FOODS
           if any(_hit(a.lower(), toks, t) for a in [f["id"].replace("_", " "), f["name"]["bn"]] + _AL[f["id"]])]
    if not out and t and configured():
        res = ask_json(food_parse(t, [f["id"] for f in FOODS]))
        out = [BY_ID[i] for i in pick(res, "foods", BY_ID)]
    return out


_ALG = {  # allergen key -> (en, bn, words searched in the profile's allergy list)
    "milk": ("milk", "দুধ", ("milk", "dairy", "দুধ")),
    "egg": ("egg", "ডিম", ("egg", "ডিম")),
    "fish": ("fish", "মাছ", ("fish", "মাছ")),
    "peanut": ("peanut", "চিনাবাদাম", ("peanut", "groundnut", "nut", "বাদাম")),
    "gluten": ("wheat or gluten", "গম বা গ্লুটেন", ("gluten", "wheat", "গম", "আটা", "ময়দা", "গ্লুটেন")),
}
LOW_RISK_CLS = {"sulfonylurea", "insulin_basal", "insulin_rapid", "insulin_mix"}  # VERIFY medicines where skipped food risks a low


def food_warnings(matches):
    """Heads-up items only, never a ban."""
    p, out = P(), []
    blob = " ".join(str(a).lower() for a in p.get("allergies", []))
    for f in matches:
        for a in f["allergens"]:
            en, bn, words = _ALG[a]
            if any(w in blob for w in words):
                out.append({"level": "care", "text": T(
                    f"Careful: you listed an allergy to {en}. {f['name']['en']} may contain it.",
                    f"সাবধান: আপনি {bn} অ্যালার্জির কথা লিখেছেন। {f['name']['bn']} খাবারে তা থাকতে পারে।")})
    if blob.strip() and any(f.get("mixed") for f in matches):
        out.append({"level": "info", "text": T(
            "Ingredients unknown: mixed dishes can hide allergens. Ask how it was made.",
            "উপকরণ অজানা: মিশ্র খাবারে অ্যালার্জির উপাদান লুকিয়ে থাকতে পারে। কীভাবে রান্না হয়েছে জিজ্ঞাসা করুন।")})
    heavy = [f for f in matches if f["sugar"] or f["carb"] == "high"]
    if heavy:
        out.append({"level": "info", "text": T(
            f"Heads-up: {', '.join(f['name']['en'] for f in heavy)} is rich in sugar or starch. "
            "The amount matters. Small portions with a meal are easier on your sugar.",
            f"খেয়াল রাখুন: {', '.join(f['name']['bn'] for f in heavy)} খাবারে চিনি বা শর্করা বেশি। পরিমাণ গুরুত্বপূর্ণ। "
            "খাবারের সাথে অল্প পরিমাণে খেলে সুগারের ওপর চাপ কম পড়ে।")})
    if matches and all(f["carb"] == "low" for f in matches) and any(
            m.get("cls") in LOW_RISK_CLS for m in p.get("medicines", [])):
        out.append({"level": "care", "text": T(
            "You take a medicine that can lower sugar. This looks like a light meal. "
            "Do not skip a meal because of it, and follow your own doctor's plan.",
            "আপনি সুগার কমাতে পারে এমন ওষুধ খান। এটি হালকা খাবার মনে হচ্ছে। "
            "এর জন্য খাবার বাদ দেবেন না, আপনার ডাক্তারের পরিকল্পনা মানুন।")})
    return out


# ---------------------------------------------------------------- demo patients
DEMO_LABEL = T("Demo patient (fictional)", "ডেমো রোগী (কাল্পনিক)")
DEMO_INFO = {
    "rahim": T("Rahim, 52, type 2: tingling feet, two night lows, no doctor plan yet",
               "রহিম, ৫২, টাইপ ২: পায়ে ঝিনঝিন, দুইবার রাতে সুগার কম, ডাক্তারের পরিকল্পনা এখনো নেই"),
    "salma": T("Salma, 60, type 2: new metformin, flat high mornings, kidney and blood pressure flags",
               "সালমা, ৬০, টাইপ ২: নতুন মেটফরমিন, সকালে সুগার বেশি ও স্থির, কিডনি ও রক্তচাপের সমস্যা"),
    "blank": T("Blank: start from nothing", "ফাঁকা: একদম নতুন করে শুরু"),
}


def _at(d, h=8, m=0):  # naive ISO string, d days ago
    return (now() - timedelta(days=d)).replace(hour=h, minute=m, second=0, microsecond=0).isoformat(timespec="seconds")


def _e(kind, d, h, m=0, **f):
    return {"ts": _at(d, h, m), "type": kind, **f}


def _due(key, offset, iv=None):  # offset = days from today (negative = overdue)
    return {"id": f"demo-{key}", "key": key, "due": (today() + timedelta(days=offset)).isoformat(),
            "done": None, "interval_days": iv or TEST_INTERVALS[key]}


def _start(days):
    return (today() - timedelta(days=days)).isoformat()


def _rahim():
    asp = L(T("As prescribed", "ডাক্তারের নির্দেশমতো"))
    p = {"name": L(T("Rahim", "রহিম")), "age": 52, "sex": "male", "diabetes_type": "type2",
         "diagnosed_year": today().year - 6,
         "medicines": [
             {"name": "Metformin", "cls": "metformin", "dose_text": asp, "times": ["morning", "evening"],
              "start_date": _start(1460)},
             {"name": "Insulin glargine", "cls": "insulin_basal", "dose_text": asp, "times": ["night"],
              "start_date": _start(700)}],
         "allergies": [], "conditions": [], "other_history": "", "units": "mgdl",
         "target_range": dict(DEFAULT_TARGET), "fluid_limit": False, "water_target": 8, "fasting_now": False,
         "care_person": {"name": L(T("Karim (son)", "করিম (ছেলে)")), "phone": "8801000000000"},  # fictional
         "doctor_plan": None}  # demo arc: no plan -> safety screen -> doctor visit form
    blister = L(T("Small blister on my left heel. I did not treat it for a few days.",
                  "বাঁ গোড়ালিতে ছোট ফোসকা। কয়েকদিন কিছু করিনি।"))
    lg = []
    for d in range(14, 0, -1):
        lg += [_e("glucose", d, 7, value_mgdl=125 + (d * 5) % 20, context="fasting"),
               _e("glucose", d, 22, value_mgdl=66 if d == 11 else 120 + (d * 11) % 30, context="bedtime"),
               _e("med", d, 8, name="Metformin", taken=d != 8),
               _e("med", d, 22, 5, name="Insulin glargine", taken=True)]
        if d not in (9, 4):  # foot symptom logged 12 of 14 days, severity 3 rising to 5
            lg.append(_e("symptom", d, 20, module="foot", key="f_sev", severity=3 + round(2 * (14 - d) / 13),
                         numbness=d <= 6, note=blister if d == 6 else ""))
    lg += [_e("glucose", 5, 3, 10, value_mgdl=62, context="night"),  # second low (first is bedtime, day 11)
           _e("food", 2, 13, text=L(T("rice, dal and fish curry", "ভাত, ডাল ও মাছের তরকারি")), amount="medium",
              matched=["bhat", "dal", "machh"], carb="high", warnings=[]),
           _e("water", 1, 18, glasses=5), _e("energy", 1, 19, level=3)]
    lg += [_e("concern", d, 9, key="foot", status="worse") for d in (5, 3, 1)]
    return {"profile": p, "logs": lg, "due": [_due("hba1c", -12), _due("doctor_visit", 5)]}


def _salma():
    asp = L(T("As prescribed", "ডাক্তারের নির্দেশমতো"))
    p = {"name": L(T("Salma", "সালমা")), "age": 60, "sex": "female", "diabetes_type": "type2",
         "diagnosed_year": today().year - 8,
         "medicines": [{"name": "Metformin", "cls": "metformin", "dose_text": asp, "times": ["morning", "evening"],
                        "start_date": _start(42)}],
         "allergies": [], "conditions": ["hypertension", "kidney_disease"], "other_history": "", "units": "mgdl",
         "target_range": {"low": 80, "high": 130},  # VERIFY fasting-style target; the metformin note compares against it
         "fluid_limit": False, "water_target": None, "fasting_now": False,
         "care_person": {"name": L(T("Nasrin (daughter)", "নাসরিন (মেয়ে)")), "phone": "8801000000001"},  # fictional
         "doctor_plan": None}
    lg = []
    for i, d in enumerate(range(1, 36, 2)):  # 18 fasting readings over 35 days, flat 148-162
        lg.append(_e("glucose", d, 6, 30, value_mgdl=148 + (i * 7) % 15, context="fasting"))
    for d in range(28, 0, -1):  # most doses logged, but 3 of the last 6 days missed
        lg.append(_e("med", d, 8, name="Metformin", taken=d not in (2, 4, 6)))
    for d in (12, 10, 8, 7, 5, 3, 2):
        lg.append(_e("symptom", d, 18, module="thirst", key="t_thirst", severity=4 + d % 3, numbness=False, note=""))
    lg.append(_e("concern", 1, 9, key="thirst", status="same"))
    return {"profile": p, "logs": lg, "due": [_due("bp", 0, 30), _due("kidney", 6), _due("hba1c", 20)]}


def _blank():
    return {"profile": None, "logs": [], "due": []}


DEMOS = {"rahim": _rahim, "salma": _salma, "blank": _blank}
