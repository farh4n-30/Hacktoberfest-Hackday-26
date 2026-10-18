"""Fixed screening questions (pure data, imports nothing local). Rules decide; Gemma never writes these."""


def T(en, bn):
    return {"en": en, "bn": bn}


def O(i, en, bn, w=0, s=False):
    return {"id": i, "label": T(en, bn), "weight": w, "signal": s}


def Q(i, kind, en, bn, wen, wbn, opts=None, other=False):
    return {"id": i, "type": kind, "text": T(en, bn), "why": T(wen, wbn),
            "options": opts or [], "other": other}


def YN(p, w=0, s=False):
    return [O(p + "_yes", "Yes", "হ্যাঁ", w, s), O(p + "_no", "No", "না")]


ADDED = "2026-10-18"
SCALE_WEIGHTS = ((7, 2), (4, 1))  # VERIFY (min scale value, weight), checked top down
CUTS = {"foot": {"low": 4, "high": 9}, "night": {"low": 3, "high": 7},
        "thirst": {"low": 3, "high": 6}}  # VERIFY score cuts used by triage
DURATION_DAYS = {"d1": 1, "d7": 5, "d14": 10, "d30": 21, "d90": 60, "d180": 120}  # midpoint days
REDFLAG_OPTIONS = {"thirst": ["nv_vomit"]}  # chosen option -> route to red-flag screen (high_emergency)


def _duration(i="duration"):
    return Q(i, "single", "How long has this been going on?", "এটি কতদিন ধরে চলছে?",
             "Symptoms that last longer matter more than a single bad day.",
             "যে উপসর্গ অনেকদিন থাকে তা এক দিনের সমস্যার চেয়ে বেশি গুরুত্বপূর্ণ।", [
                 O("d1", "Less than 3 days", "৩ দিনের কম"),
                 O("d7", "3 to 7 days", "৩ থেকে ৭ দিন"),
                 O("d14", "1 to 2 weeks", "১ থেকে ২ সপ্তাহ", 1),
                 O("d30", "2 to 4 weeks", "২ থেকে ৪ সপ্তাহ", 1),
                 O("d90", "1 to 3 months", "১ থেকে ৩ মাস", 2),
                 O("d180", "More than 3 months", "৩ মাসের বেশি", 2)])


FOOT = {
    "key": "foot", "added_on": ADDED,
    "title": T("Feet and nerves", "পা ও স্নায়ু"),
    "intro": T("These questions look at tingling, numbness and foot problems. They cannot tell what the cause is. "
               "They help you decide what to tell your doctor.",
               "এই প্রশ্নগুলো পায়ের ঝিনঝিন, অসাড়ভাব ও পায়ের সমস্যা নিয়ে। এগুলো কারণ বলতে পারে না। "
               "ডাক্তারকে কী বলবেন তা ঠিক করতে সাহায্য করে।"),
    "keywords": {
        "en": ["foot", "feet", "toe", "tingling", "numb", "burning", "pins and needles", "blister",
               "wound", "ulcer", "cramp", "sole", "heel", "leg"],
        "bn": ["পা", "পায়ে", "আঙুল", "ঝিনঝিন", "অসাড়", "জ্বালা", "ফোসকা", "ঘা", "ক্ষত", "তলা", "গোড়ালি", "খিল"]},
    "min_days": 7,  # VERIFY
    "specialist": "foot",
    "fast_track": ["wound_old", "skin_color"],  # VERIFY foot exception: wound 3+ days, colour or warmth change
    "questions": [
        Q("f_where", "single", "Where do you feel it?", "কোথায় অনুভব করছেন?",
          "Both feet at once is a common pattern worth mentioning.",
          "দুই পায়ে একসাথে হলে সেটি ডাক্তারকে জানানো ভালো।", [
              O("both_feet", "Both feet", "দুই পায়ে", 1),
              O("one_foot", "One foot only", "এক পায়ে", 1),
              O("toes", "Toes only", "শুধু আঙুলে"),
              O("sole", "Sole or heel", "পায়ের তলা বা গোড়ালিতে"),
              O("leg", "Lower leg", "নিচের পায়ে")]),
        Q("f_type", "single", "What does it feel like?", "কেমন অনুভব হচ্ছে?",
          "The type of feeling helps your doctor think about the cause.",
          "অনুভূতির ধরন থেকে ডাক্তার কারণ নিয়ে ভাবতে পারেন।", [
              O("tingle", "Tingling or pins and needles", "ঝিনঝিন বা সুই ফোটার মতো", 1),
              O("burn", "Burning", "জ্বালাপোড়া", 1),
              O("numb", "Numb, like wearing a sock", "অসাড়, যেন মোজা পরা আছে", 2),
              O("sharp", "Sharp or shooting", "তীক্ষ্ণ বা ছুটে যাওয়া ব্যথা", 1),
              O("none_feel", "No unusual feeling", "অস্বাভাবিক কিছু নয়")], other=True),
        Q("f_sev", "scale", "How strong is it right now? (0 = none, 10 = worst)",
          "এখন কতটা তীব্র? (০ = নেই, ১০ = সবচেয়ে বেশি)",
          "A number lets you and your doctor see if it changes over time.",
          "সংখ্যা দিয়ে সময়ের সাথে পরিবর্তন বোঝা সহজ হয়।"),
        Q("f_loss", "single", "Have you lost feeling in your feet?", "পায়ের অনুভূতি কি কমে গেছে?",
          "Numbness without pain is NOT reassuring. You may not feel an injury, so it can go unnoticed.",
          "ব্যথা ছাড়া অসাড়ভাব নিশ্চিন্ত থাকার কারণ নয়। আঘাত টের নাও পেতে পারেন, তাই তা চোখ এড়িয়ে যেতে পারে।", [
              O("loss_none", "No, I feel normally", "না, স্বাভাবিক অনুভব করি"),
              O("loss_hot", "I could not feel hot water on my feet", "পায়ে গরম পানি টের পাইনি", 2, True),
              O("loss_pebble", "I did not feel a pebble in my shoe", "জুতার ভেতরে কাঁকর টের পাইনি", 2, True),
              O("loss_unsure", "Not sure", "নিশ্চিত নই", 1)]),
        Q("f_wound", "single", "Do you have a wound, blister or sore on your foot?",
          "আপনার পায়ে কি কোনো ঘা, ফোসকা বা ক্ষত আছে?",
          "Small foot wounds heal slowly with diabetes and can get worse without pain.",
          "ডায়াবেটিসে পায়ের ছোট ক্ষত ধীরে সারে এবং ব্যথা ছাড়াই খারাপ হতে পারে।", [
              O("wound_none", "No", "না"),
              O("wound_heal", "A small one that is healing", "ছোট একটি, সেরে উঠছে", 1),
              O("wound_new", "Yes, for less than 3 days", "হ্যাঁ, ৩ দিনের কম", 1, True),
              O("wound_old", "Yes, for 3 days or more, or not healing", "হ্যাঁ, ৩ দিন বা বেশি, অথবা সারছে না", 3, True)]),
        Q("f_skin", "single", "Have you noticed changes in skin colour, swelling or warmth?",
          "চামড়ার রং, ফোলা বা গরমভাবে কোনো পরিবর্তন দেখেছেন?",
          "Colour or temperature changes can mean a circulation or infection problem.",
          "রং বা তাপমাত্রার পরিবর্তন রক্তসঞ্চালন বা সংক্রমণের সমস্যা হতে পারে।", [
              O("skin_none", "No change", "কোনো পরিবর্তন নেই"),
              O("skin_dry", "Dry or cracked skin", "শুকনো বা ফাটা চামড়া", 1),
              O("skin_swell", "Swelling", "ফোলা", 1),
              O("skin_color", "Red, dark or pale skin, or one foot hotter or colder", 
                "লাল, কালচে বা ফ্যাকাসে চামড়া, অথবা এক পা বেশি গরম বা ঠান্ডা", 3, True)], other=True),
        Q("f_shoes", "single", "What do you wear on your feet?", "পায়ে কী পরেন?",
          "Walking barefoot or in tight shoes makes unnoticed injuries more likely.",
          "খালি পায়ে বা আঁটসাঁট জুতায় হাঁটলে অজান্তে আঘাত লাগার সম্ভাবনা বেশি।", [
              O("shoe_ok", "Well-fitting shoes or sandals", "ঠিক মাপের জুতা বা স্যান্ডেল"),
              O("shoe_tight", "Tight or worn-out shoes", "আঁটসাঁট বা পুরোনো জুতা", 1),
              O("shoe_some", "Barefoot sometimes", "মাঝে মাঝে খালি পায়ে", 1),
              O("shoe_often", "Barefoot most of the time", "বেশিরভাগ সময় খালি পায়ে", 2)]),
        Q("f_night", "yesno", "Is it worse at night?", "রাতে কি বেশি হয়?",
          "Night-time worsening is common with nerve irritation and is useful to tell your doctor.",
          "স্নায়ুর সমস্যায় রাতে বাড়া সাধারণ, তাই ডাক্তারকে বলা কাজের।", YN("fn", 1)),
        _duration(),
        Q("f_other", "single", "Do any of these apply to you?", "এগুলোর কোনোটি কি আপনার ক্ষেত্রে প্রযোজ্য?",
          "Other things can also cause foot symptoms. Knowing them lowers false alarms.",
          "পায়ের উপসর্গের অন্য কারণও থাকতে পারে। জানা থাকলে অকারণ দুশ্চিন্তা কমে।", [
              O("oc_none", "None of these", "এগুলোর কোনোটি নয়"),
              O("oc_b12", "Long-term metformin, or told my vitamin B12 is low",
                "অনেকদিন মেটফরমিন খাচ্ছি, অথবা ভিটামিন বি-১২ কম বলা হয়েছে"),
              O("oc_alcohol", "I drink alcohol regularly", "আমি নিয়মিত মদ্যপান করি"),
              O("oc_illness", "Recent illness or a new medicine", "সম্প্রতি অসুস্থতা বা নতুন ওষুধ")], other=True),
    ],
}

NIGHT = {
    "key": "night", "added_on": ADDED,
    "title": T("Low sugar at night", "রাতে সুগার কমে যাওয়া"),
    "intro": T("Low sugar can happen while you sleep and you may not notice. These questions look for hidden signs.",
               "ঘুমের মধ্যে সুগার কমে যেতে পারে, আর আপনি টের নাও পেতে পারেন। এই প্রশ্নগুলো লুকানো লক্ষণ খোঁজে।"),
    "keywords": {
        "en": ["night", "sweat", "nightmare", "morning headache", "shaking", "hunger", "low sugar",
               "hypo", "wake up", "sleep"],
        "bn": ["রাত", "ঘাম", "দুঃস্বপ্ন", "মাথাব্যথা", "কাঁপুনি", "ক্ষুধা", "সুগার কম", "ঘুম", "জেগে"]},
    "min_days": 3,  # VERIFY
    "specialist": "endocrine",
    "fast_track": [],
    "questions": [
        Q("n_sweat", "single", "Do you wake up sweaty, with wet sheets or clothes?",
          "ঘেমে, ভেজা বিছানা বা কাপড়সহ কি ঘুম ভাঙে?",
          "Night sweats can be a sign of low sugar during sleep.",
          "রাতে ঘাম ঘুমের মধ্যে সুগার কমে যাওয়ার লক্ষণ হতে পারে।", [
              O("sw_no", "No", "না"),
              O("sw_some", "Sometimes", "মাঝে মাঝে", 1),
              O("sw_often", "Often", "প্রায়ই", 2, True)]),
        Q("n_dream", "single", "Do you have nightmares or restless sleep?", "দুঃস্বপ্ন দেখেন বা ঘুম অস্থির হয়?",
          "Bad dreams can happen when sugar drops at night.",
          "রাতে সুগার কমলে খারাপ স্বপ্ন দেখা যেতে পারে।", [
              O("dr_no", "No", "না"),
              O("dr_some", "Sometimes", "মাঝে মাঝে", 1),
              O("dr_often", "Often", "প্রায়ই", 1)]),
        Q("n_head", "single", "Do you wake up with a headache?", "মাথাব্যথা নিয়ে কি ঘুম থেকে ওঠেন?",
          "Morning headache can follow a low during the night.",
          "রাতে সুগার কমে গেলে সকালে মাথাব্যথা হতে পারে।", [
              O("hd_no", "No", "না"),
              O("hd_some", "Sometimes", "মাঝে মাঝে", 1),
              O("hd_often", "Often", "প্রায়ই", 2, True)]),
        Q("n_shake", "single", "Do you wake up shaking, very hungry or confused?",
          "কাঁপুনি, তীব্র ক্ষুধা বা বিভ্রান্তি নিয়ে কি ঘুম ভাঙে?",
          "These are classic warning signs of low sugar. Confusion needs urgent help.",
          "এগুলো সুগার কমে যাওয়ার পরিচিত সতর্ক লক্ষণ। বিভ্রান্তি হলে জরুরি সাহায্য দরকার।", [
              O("sh_no", "No", "না"),
              O("sh_some", "Sometimes", "মাঝে মাঝে", 2, True),
              O("sh_often", "Often", "প্রায়ই", 3, True)], other=True),
        Q("n_insulin", "yesno", "Did you take insulin or a sugar-lowering tablet at night without eating?",
          "রাতে না খেয়ে কি ইনসুলিন বা সুগার কমানোর ট্যাবলেট নিয়েছেন?",
          "Medicine without food is a common reason for a low at night. We do not advise on doses.",
          "খাবার ছাড়া ওষুধ নিলে রাতে সুগার কমার সম্ভাবনা বাড়ে। ডোজ নিয়ে আমরা পরামর্শ দিই না।",
          YN("ni", 2, True)),
        Q("n_bed", "single", "How was your sugar at bedtime in the last few days?",
          "গত কয়েকদিন শোয়ার সময় আপনার সুগার কেমন ছিল?",
          "A low or missing bedtime reading makes a night-time low more likely.",
          "শোয়ার সময় সুগার কম থাকলে বা মাপা না হলে রাতে কমার সম্ভাবনা বাড়ে।", [
              O("bed_ok", "In my usual range", "আমার স্বাভাবিক সীমার মধ্যে"),
              O("bed_high", "Higher than usual", "স্বাভাবিকের চেয়ে বেশি"),
              O("bed_low", "Lower than usual", "স্বাভাবিকের চেয়ে কম", 2),
              O("bed_none", "I did not check", "মাপিনি", 1)]),
    ],
}

THIRST = {
    "key": "thirst", "added_on": ADDED,
    "title": T("Thirst and high sugar", "পিপাসা ও বেশি সুগার"),
    "intro": T("Strong thirst and frequent urination can go with high sugar. These questions look at the pattern.",
               "খুব পিপাসা ও ঘন ঘন প্রস্রাব বেশি সুগারের সাথে হতে পারে। এই প্রশ্নগুলো ধরনটি দেখে।"),
    "keywords": {
        "en": ["thirst", "thirsty", "urination", "urine", "dry mouth", "tired", "fatigue", "high sugar",
               "vomit", "nausea", "drink water"],
        "bn": ["পিপাসা", "তেষ্টা", "প্রস্রাব", "মুখ শুকিয়ে", "ক্লান্ত", "দুর্বল", "সুগার বেশি", "বমি", "বমি বমি", "পানি"]},
    "min_days": 3,  # VERIFY
    "specialist": "endocrine",
    "fast_track": [],
    "questions": [
        Q("t_thirst", "scale", "How thirsty are you? (0 = not at all, 10 = extreme)",
          "কতটা পিপাসা পাচ্ছে? (০ = একদম না, ১০ = অসহ্য)",
          "Thirst that does not go away can be linked to high sugar.",
          "যে পিপাসা মেটে না তা বেশি সুগারের সাথে যুক্ত হতে পারে।"),
        Q("t_urine", "single", "How often do you pass urine?", "কতবার প্রস্রাব করেন?",
          "Passing more urine than usual, especially at night, is a common sign of high sugar.",
          "স্বাভাবিকের চেয়ে বেশি প্রস্রাব, বিশেষ করে রাতে, বেশি সুগারের সাধারণ লক্ষণ।", [
              O("ur_norm", "As usual", "যেমন সবসময়"),
              O("ur_more", "More than usual in the day", "দিনে স্বাভাবিকের চেয়ে বেশি", 1),
              O("ur_night", "Also 2 or more times at night", "রাতেও ২ বার বা বেশি", 2, True)], other=True),
        Q("t_dry", "yesno", "Is your mouth very dry?", "আপনার মুখ কি খুব শুকিয়ে যায়?",
          "A dry mouth often goes with thirst and can have other causes too.",
          "মুখ শুকিয়ে যাওয়া প্রায়ই পিপাসার সাথে হয়, তবে অন্য কারণও থাকতে পারে।", YN("td", 1)),
        Q("t_tired", "single", "How tired do you feel?", "কতটা ক্লান্ত লাগছে?",
          "Tiredness is common with high sugar, but poor sleep and stress cause it too.",
          "বেশি সুগারে ক্লান্তি সাধারণ, তবে কম ঘুম ও দুশ্চিন্তাতেও হয়।", [
              O("ti_no", "Not more than usual", "স্বাভাবিকের বেশি নয়"),
              O("ti_some", "More tired than usual", "স্বাভাবিকের চেয়ে বেশি ক্লান্ত", 1),
              O("ti_lot", "Very tired, hard to do daily tasks", "খুব ক্লান্ত, দৈনন্দিন কাজ কঠিন", 2, True)]),
        Q("t_ill", "single", "Have you been ill or started a new medicine recently?",
          "সম্প্রতি কি অসুস্থ হয়েছেন বা নতুন ওষুধ শুরু করেছেন?",
          "Fever, infection and some medicines such as steroids can raise sugar for a while.",
          "জ্বর, সংক্রমণ ও কিছু ওষুধ, যেমন স্টেরয়েড, কিছুদিন সুগার বাড়াতে পারে।", [
              O("ill_no", "No", "না"),
              O("ill_sick", "Yes, fever or infection", "হ্যাঁ, জ্বর বা সংক্রমণ"),
              O("ill_med", "Yes, a new medicine", "হ্যাঁ, নতুন ওষুধ")]),
        Q("t_nv", "single", "Do you feel sick in the stomach or are you vomiting?",
          "বমি বমি লাগছে বা বমি হচ্ছে কি?",
          "Vomiting with high sugar can be serious. If you choose vomiting, we will check for emergency signs first.",
          "বেশি সুগারের সাথে বমি গুরুতর হতে পারে। বমি বেছে নিলে আগে জরুরি লক্ষণ যাচাই করা হবে।", [
              O("nv_none", "No", "না"),
              O("nv_nausea", "Feeling sick, no vomiting", "বমি বমি লাগছে, বমি হয়নি", 1),
              O("nv_vomit", "Yes, vomiting", "হ্যাঁ, বমি হচ্ছে", 3, True)]),
    ],
}

QMODULES = {"foot": FOOT, "night": NIGHT, "thirst": THIRST}
