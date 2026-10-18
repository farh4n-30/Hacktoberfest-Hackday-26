"""Static learning content (pure data, imports nothing local). Gemma may only rephrase these fact sheets."""


def T(en, bn):
    return {"en": en, "bn": bn}


def G(term, simple):
    return {"term": T(*term), "simple": T(*simple)}


def C(cid, cat, rel, title, simple, signs, tips, see, myth=None):
    return {"id": cid, "category": cat, "added_on": ADDED, "relevance": rel, "title": T(*title),
            "simple": T(*simple), "signs": [T(*s) for s in signs], "tips": [T(*t) for t in tips],
            "see_doctor": T(*see),
            "myth": {"myth": T(*myth[0]), "fact": T(*myth[1])} if myth else None}


def X(title, analogy, simple, detailed):
    return {"added_on": ADDED, "title": T(*title), "analogy": T(*analogy),
            "simple": T(*simple), "detailed": T(*detailed)}


ADDED = "2026-10-18"

GLOSSARY = {
    "neuropathy": G(("Neuropathy", "স্নায়ুর ক্ষতি (নিউরোপ্যাথি)"),
                    ("Damage to the nerves, often in the feet. It can cause tingling, burning or loss of feeling.",
                     "স্নায়ুর ক্ষতি, প্রায়ই পায়ে হয়। এতে ঝিনঝিন, জ্বালা বা অনুভূতি কমে যেতে পারে।")),
    "retinopathy": G(("Retinopathy", "চোখের পর্দার সমস্যা (রেটিনোপ্যাথি)"),
                     ("Damage to the tiny blood vessels at the back of the eye. Early on it often has no symptoms.",
                      "চোখের পেছনের ছোট রক্তনালির ক্ষতি। শুরুতে প্রায়ই কোনো উপসর্গ থাকে না।")),
    "hba1c": G(("HbA1c", "এইচবিএ১সি"),
               ("A blood test that shows your average sugar over about 3 months.",
                "একটি রক্তপরীক্ষা, যা প্রায় ৩ মাসের গড় সুগার দেখায়।")),
    "hypoglycemia": G(("Low blood sugar (hypoglycemia)", "সুগার কমে যাওয়া (হাইপোগ্লাইসেমিয়া)"),
                      ("Blood sugar that falls too low. It can cause shaking, sweating, hunger or confusion.",
                       "রক্তের সুগার খুব কমে যাওয়া। এতে কাঁপুনি, ঘাম, ক্ষুধা বা বিভ্রান্তি হতে পারে।")),
    "hyperglycemia": G(("High blood sugar (hyperglycemia)", "সুগার বেড়ে যাওয়া (হাইপারগ্লাইসেমিয়া)"),
                       ("Blood sugar that stays above your target. It can cause thirst and frequent urination.",
                        "রক্তের সুগার লক্ষ্যের উপরে থাকা। এতে পিপাসা ও ঘন ঘন প্রস্রাব হতে পারে।")),
    "ketones": G(("Ketones", "কিটোন"),
                 ("Acids the body makes when it cannot use sugar well. Too many can be dangerous.",
                  "শরীর সুগার ঠিকমতো কাজে লাগাতে না পারলে এই অ্যাসিড তৈরি হয়। বেশি হলে বিপজ্জনক।")),
    "insulin_resistance": G(("Insulin resistance", "ইনসুলিনের কাজ কমে যাওয়া"),
                            ("The body's cells respond less to insulin, so sugar stays in the blood.",
                             "শরীরের কোষ ইনসুলিনে কম সাড়া দেয়, তাই সুগার রক্তে থেকে যায়।")),
    "basal_rapid": G(("Basal and rapid insulin", "দীর্ঘস্থায়ী ও দ্রুত ইনসুলিন"),
                     ("Basal insulin works slowly through the day or night. Rapid insulin works fast around meals.",
                      "দীর্ঘস্থায়ী ইনসুলিন ধীরে সারাদিন বা সারারাত কাজ করে। দ্রুত ইনসুলিন খাবারের সময় দ্রুত কাজ করে।")),
    "metformin": G(("Metformin", "মেটফরমিন"),
                   ("A common diabetes tablet that helps the body use its own insulin better.",
                    "ডায়াবেটিসের একটি পরিচিত ট্যাবলেট, যা শরীরকে নিজের ইনসুলিন ভালোভাবে কাজে লাগাতে সাহায্য করে।")),
    "egfr": G(("Kidney filter score (eGFR)", "কিডনির ছাঁকনি মাপ (ই-জিএফআর)"),
              ("A number from a blood test that shows how well the kidneys clean the blood.",
               "রক্তপরীক্ষার একটি সংখ্যা, যা দেখায় কিডনি কতটা ভালোভাবে রক্ত পরিষ্কার করছে।")),
    "albumin": G(("Albumin in urine", "প্রস্রাবে অ্যালবুমিন"),
                 ("A small amount of protein in the urine. It can be an early sign of kidney strain.",
                  "প্রস্রাবে অল্প প্রোটিন। এটি কিডনির ওপর চাপের প্রথম লক্ষণ হতে পারে।")),
    "cholesterol": G(("Cholesterol", "কোলেস্টেরল"),
                     ("A fat in the blood. Too much can block blood vessels over time.",
                      "রক্তের একটি চর্বি। বেশি হলে ধীরে ধীরে রক্তনালি বন্ধ হয়ে যেতে পারে।")),
    "blood_pressure": G(("Blood pressure", "রক্তচাপ"),
                        ("The force of blood on the walls of your blood vessels. High pressure harms the heart, eyes and kidneys.",
                         "রক্তনালির দেয়ালে রক্তের চাপ। চাপ বেশি হলে হৃদয়, চোখ ও কিডনির ক্ষতি হয়।")),
    "b12": G(("Vitamin B12", "ভিটামিন বি-১২"),
             ("A vitamin your nerves need. Long-term metformin can lower it.",
              "স্নায়ুর জন্য দরকারি একটি ভিটামিন। অনেকদিন মেটফরমিন খেলে এটি কমতে পারে।")),
    "ulcer": G(("Foot ulcer", "পায়ের ঘা (আলসার)"),
               ("An open sore on the skin that heals slowly. With diabetes it can go unnoticed.",
                "চামড়ার খোলা ক্ষত, যা ধীরে সারে। ডায়াবেটিসে এটি অনেক সময় চোখ এড়িয়ে যায়।")),
    "confounder": G(("Other possible reasons", "অন্য সম্ভাব্য কারণ"),
                    ("Other things that can cause the same symptom, such as illness or a new medicine.",
                     "একই উপসর্গের অন্য কারণ, যেমন অসুস্থতা বা নতুন ওষুধ।")),
}

CONFOUNDERS = {  # keys match base.confounders_active(); the rest are asked or noted in the report
    "fasting": T("Fasting or Ramadan", "রোজা বা উপবাস"),
    "missed_doses": T("Missed doses of medicine", "ওষুধ বাদ পড়া"),
    "new_medicine": T("A new or changed medicine", "নতুন বা বদলানো ওষুধ"),
    "steroids": T("Steroid medicine", "স্টেরয়েড জাতীয় ওষুধ"),
    "illness": T("Recent illness or fever", "সাম্প্রতিক অসুস্থতা বা জ্বর"),
    "poor_sleep": T("Poor sleep", "কম ঘুম"),
    "stress": T("Stress or worry", "মানসিক চাপ বা দুশ্চিন্তা"),
    "alcohol": T("Alcohol", "মদ্যপান"),
    "feast_day": T("A feast day or special meal", "ঈদ বা বিশেষ ভোজ"),
    "exercise": T("Unusual exercise or heavy work", "অস্বাভাবিক ব্যায়াম বা ভারী কাজ"),
    "meter": T("Meter or test timing", "মাপার যন্ত্র বা মাপার সময়ের গোলমাল"),
    "b12_metformin": T("Low vitamin B12 after long-term metformin",
                       "অনেকদিন মেটফরমিন খাওয়ার পর ভিটামিন বি-১২ কম হওয়া"),
}

CARDS = [
    C("foot_check", "foot", ["foot", "neuropathy", "any"],
      ("Check your feet every day", "প্রতিদিন পা দেখুন"),
      ("Small foot problems can grow quietly. A daily look catches them early.",
       "পায়ের ছোট সমস্যা চুপচাপ বড় হতে পারে। প্রতিদিন দেখলে আগেই ধরা পড়ে।"),
      [("Cuts, blisters or cracks", "কাটা, ফোসকা বা ফাটা"),
       ("Redness, swelling or warm skin", "লালচে ভাব, ফোলা বা গরম চামড়া"),
       ("A toe that changes colour", "আঙুলের রং বদলে যাওয়া")],
      [("Look at the top, the sole and between the toes.", "পায়ের উপরে, তলায় ও আঙুলের ফাঁকে দেখুন।"),
       ("Use a mirror or ask someone to help.", "আয়না ব্যবহার করুন বা কাউকে দেখতে বলুন।"),
       ("Dry between the toes after washing.", "ধোয়ার পর আঙুলের ফাঁক শুকনো করুন।")],
      ("A wound that lasts 3 days or more needs your doctor's attention.",  # VERIFY
       "৩ দিন বা বেশি থাকা ঘা ডাক্তারকে দেখান।")),
    C("foot_barefoot", "foot", ["foot", "neuropathy"],
      ("Why walking barefoot is risky", "খালি পায়ে হাঁটা কেন ঝুঁকিপূর্ণ"),
      ("With less feeling, you may step on something and not know.",
       "অনুভূতি কম থাকলে কিছুতে পা পড়লেও টের পাবেন না।"),
      [("Not feeling a pebble or a hot floor", "কাঁকর বা গরম মেঝে টের না পাওয়া"),
       ("Small cuts you only see later", "ছোট কাটা, যা পরে চোখে পড়ে")],
      [("Wear sandals or shoes, even at home.", "ঘরেও স্যান্ডেল বা জুতা পরুন।"),
       ("Shake out your shoes before wearing them.", "জুতা পরার আগে ঝেড়ে নিন।"),
       ("Test bath water with your hand or elbow.", "গোসলের পানি হাত বা কনুই দিয়ে দেখে নিন।")],
      ("If you cannot feel your feet well, tell your doctor.",
       "পায়ের অনুভূতি ভালো না থাকলে ডাক্তারকে বলুন।"),
      (("No pain means no problem.", "ব্যথা নেই মানে সমস্যা নেই।"),
       ("Nerve damage can hide pain, so injuries go unseen.",
        "স্নায়ুর ক্ষতিতে ব্যথা টের পাওয়া যায় না, তাই আঘাত চোখ এড়িয়ে যায়।"))),
    C("foot_wounds", "foot", ["foot", "neuropathy"],
      ("Blisters, wounds and nails", "ফোসকা, ঘা ও নখ"),
      ("Treat even a small wound seriously. It can heal slowly.",
       "ছোট ঘাকেও গুরুত্ব দিন। এটি ধীরে সারতে পারে।"),
      [("A blister or sore that is not healing", "সেরে না ওঠা ফোসকা বা ঘা"),
       ("Pus, a bad smell or spreading redness", "পুঁজ, দুর্গন্ধ বা ছড়িয়ে পড়া লালচে ভাব"),
       ("Thick, ingrown or dark nails", "মোটা, ভেতরে ঢোকা বা কালচে নখ")],
      [("Do not pop blisters or cut corns yourself.", "ফোসকা ফাটাবেন না, কড়া নিজে কাটবেন না।"),
       ("Keep a wound clean and covered.", "ক্ষত পরিষ্কার ও ঢাকা রাখুন।"),
       ("Cut nails straight across, not too short.", "নখ সোজা করে কাটুন, খুব ছোট নয়।")],
      ("Spreading redness, pus or fever with a foot wound needs help the same day. "
       "Call 999 if you feel very unwell.",  # VERIFY
       "পায়ের ঘায় ছড়িয়ে পড়া লালচে ভাব, পুঁজ বা জ্বর হলে সেদিনই সাহায্য নিন। "
       "খুব অসুস্থ লাগলে ৯৯৯ নম্বরে ফোন করুন।")),
    C("foot_shoes", "foot", ["foot", "neuropathy"],
      ("Choosing shoes", "জুতা বাছাই"),
      ("Shoes that fit well protect feet that cannot feel much.",
       "ঠিক মাপের জুতা কম অনুভূতির পা বাঁচায়।"),
      [("Red marks after taking shoes off", "জুতা খোলার পর লাল দাগ"),
       ("Rubbing on the toes or heels", "আঙুল বা গোড়ালিতে ঘষা লাগা")],
      [("Buy shoes in the evening, when feet are biggest.", "বিকেলে জুতা কিনুন, তখন পা সবচেয়ে বড় থাকে।"),
       ("Choose soft, closed and roomy shoes.", "নরম, ঢাকা ও ঢিলা জুতা নিন।"),
       ("Wear clean cotton socks.", "পরিষ্কার সুতির মোজা পরুন।")],
      ("Ask your doctor about special footwear if you have had foot wounds.",
       "আগে পায়ে ঘা হয়ে থাকলে বিশেষ জুতার কথা ডাক্তারকে জিজ্ঞাসা করুন।")),
    C("silent_heart", "heart", ["heart", "hypertension", "any"],
      ("Silent heart problems", "নীরব হৃদরোগ"),
      ("With diabetes, heart trouble can cause little or no chest pain.",
       "ডায়াবেটিসে হৃদয়ের সমস্যায় বুকে ব্যথা কম হতে পারে বা নাও হতে পারে।"),
      [("Unusual tiredness or weakness", "অস্বাভাবিক ক্লান্তি বা দুর্বলতা"),
       ("Breathless on small effort", "সামান্য কাজে হাঁপিয়ে ওঠা"),
       ("Pressure in the chest, or pain in the jaw, arm or back",
        "বুকে চাপ, অথবা চোয়াল, হাত বা পিঠে ব্যথা"),
       ("Cold sweat or feeling sick", "ঠান্ডা ঘাম বা বমি বমি ভাব")],
      [("Check blood pressure and cholesterol regularly.", "রক্তচাপ ও কোলেস্টেরল নিয়মিত দেখান।"),
       ("Walk daily if your doctor agrees.", "ডাক্তার অনুমতি দিলে প্রতিদিন হাঁটুন।"),
       ("Do not smoke or chew tobacco.", "ধূমপান বা তামাক চিবানো বন্ধ করুন।")],
      ("These can be signs of a medical emergency. Call 999 now.",  # VERIFY
       "এগুলো জরুরি অবস্থার লক্ষণ হতে পারে। এখনই ৯৯৯ নম্বরে ফোন করুন।")),
    C("stroke_signs", "heart", ["heart", "hypertension", "any"],
      ("Stroke warning signs", "স্ট্রোকের সতর্ক লক্ষণ"),
      ("A stroke is an emergency. Fast help protects the brain.",
       "স্ট্রোক জরুরি অবস্থা। দ্রুত সাহায্য মস্তিষ্ক বাঁচায়।"),
      [("Sudden loss of balance or dizziness", "হঠাৎ ভারসাম্য হারানো বা মাথা ঘোরা"),
       ("Sudden change in vision", "হঠাৎ দেখার পরিবর্তন"),
       ("One side of the face drooping", "মুখের এক পাশ ঝুলে পড়া"),
       ("Weakness in one arm or leg", "এক হাত বা পায়ে দুর্বলতা"),
       ("Trouble speaking or understanding", "কথা বলতে বা বুঝতে অসুবিধা")],
      [("Note the time the signs began and tell the doctors.", "লক্ষণ কখন শুরু হয়েছে মনে রাখুন, ডাক্তারকে বলুন।"),
       ("Do not wait to see if it passes.", "কমে যায় কিনা দেখার জন্য অপেক্ষা করবেন না।"),
       ("Low sugar can look similar. Check sugar if you can, but do not delay the call.",
        "সুগার কমলেও একই রকম লাগতে পারে। পারলে সুগার মাপুন, তবে ফোন করতে দেরি করবেন না।")],
      ("Any of these signs can mean an emergency. Call 999 now.",  # VERIFY
       "এর যেকোনোটি জরুরি অবস্থা হতে পারে। এখনই ৯৯৯ নম্বরে ফোন করুন।")),
    C("eye_exam", "eye", ["eye", "retinopathy", "any"],
      ("A yearly eye check", "বছরে একবার চোখ পরীক্ষা"),
      ("Eye damage from diabetes often has no early symptoms. An eye exam with drops can find it.",
       "ডায়াবেটিসে চোখের ক্ষতি শুরুতে প্রায়ই টের পাওয়া যায় না। ড্রপ দিয়ে চোখ পরীক্ষায় তা ধরা পড়ে।"),
      [("Blurry vision that comes and goes", "ঝাপসা দেখা, যা আসে আর যায়"),
       ("Dark spots or floating shadows", "কালো দাগ বা ভেসে বেড়ানো ছায়া"),
       ("Trouble seeing at night", "রাতে দেখতে কষ্ট")],
      [("Book an eye exam at least once a year.", "বছরে অন্তত একবার চোখ দেখান।"),  # VERIFY
       ("Keep sugar and blood pressure steady.", "সুগার ও রক্তচাপ স্থির রাখুন।"),
       ("Tell the eye doctor you have diabetes.", "চোখের ডাক্তারকে ডায়াবেটিসের কথা বলুন।")],
      ("Sudden loss of sight, or a dark curtain over the eye, needs urgent help.",
       "হঠাৎ দৃষ্টি চলে যাওয়া, বা চোখের সামনে কালো পর্দা নামলে জরুরি সাহায্য নিন।"),
      (("I see fine, so I do not need an eye exam.", "আমি ভালো দেখি, তাই চোখ পরীক্ষার দরকার নেই।"),
       ("Early damage often shows no symptoms. Only an exam can find it.",
        "শুরুর ক্ষতিতে প্রায়ই উপসর্গ থাকে না। শুধু পরীক্ষাতেই তা ধরা পড়ে।"))),
    C("kidney_signs", "kidney", ["kidney", "hypertension", "any"],
      ("Kidney warning signs", "কিডনির সতর্ক লক্ষণ"),
      ("Kidneys can be harmed quietly. Yearly urine and blood tests check them.",
       "কিডনি চুপচাপ ক্ষতিগ্রস্ত হতে পারে। বছরে একবার প্রস্রাব ও রক্তপরীক্ষায় তা দেখা যায়।"),
      [("Foamy urine", "ফেনাযুক্ত প্রস্রাব"),
       ("Swelling of feet, ankles or face", "পা, গোড়ালি বা মুখ ফোলা"),
       ("Tiredness or poor appetite", "ক্লান্তি বা খিদে কম")],
      [("Ask for the urine albumin and kidney blood tests each year.",  # VERIFY
        "বছরে একবার প্রস্রাবে অ্যালবুমিন ও কিডনির রক্তপরীক্ষা করান।"),
       ("Keep blood pressure in the range your doctor set.", "রক্তচাপ ডাক্তারের দেওয়া সীমায় রাখুন।"),
       ("Ask a doctor before taking painkillers regularly.", "নিয়মিত ব্যথার ওষুধ খাওয়ার আগে ডাক্তারকে জিজ্ঞাসা করুন।")],
      ("Swelling, or much less urine than usual, needs a doctor soon.",
       "ফোলা, বা প্রস্রাব অনেক কমে গেলে শিগগির ডাক্তার দেখান।")),
    C("insulin_meals", "insulin", ["insulin"],
      ("Insulin and meals", "ইনসুলিন ও খাবার"),
      ("Insulin lowers sugar. If you take it and do not eat, sugar can drop too low.",
       "ইনসুলিন সুগার কমায়। ইনসুলিন নিয়ে না খেলে সুগার খুব কমে যেতে পারে।"),
      [("Shaking, sweating or sudden hunger", "কাঁপুনি, ঘাম বা হঠাৎ ক্ষুধা"),
       ("Headache or confusion", "মাথাব্যথা বা বিভ্রান্তি")],
      [("Follow only the plan your own doctor gave you.", "শুধু আপনার নিজের ডাক্তারের দেওয়া পরিকল্পনা মানুন।"),
       ("Check your sugar before you sleep.", "ঘুমের আগে সুগার মাপুন।"),
       ("Do not guess a dose. Ask your doctor what to do if you skip a meal.",
        "ডোজ আন্দাজ করবেন না। খাবার বাদ দিলে কী করবেন তা ডাক্তারকে জিজ্ঞাসা করুন।")],
      ("Ask your doctor what to do if you miss or delay a meal.",
       "খাবার বাদ পড়লে বা দেরি হলে কী করবেন তা ডাক্তারকে জিজ্ঞাসা করুন।")),
    C("insulin_myth", "insulin", ["insulin", "any"],
      ("Sweets and extra insulin", "মিষ্টি ও বাড়তি ইনসুলিন"),
      ("Insulin is not an eraser for sweets or chocolate.",
       "ইনসুলিন মিষ্টি বা চকলেটের হিসাব মুছে দেয় না।"),
      [("Big sugar swings after sweet food", "মিষ্টি খাবারের পর সুগারের বড় ওঠানামা")],
      [("Take insulin only as prescribed.", "ইনসুলিন শুধু নির্দেশমতো নিন।"),
       ("Have sweets rarely, in small amounts, with a meal.", "মিষ্টি কম, অল্প ও খাবারের সাথে খান।"),
       ("Ask your doctor how to handle special occasions.", "উৎসবে কী করবেন তা ডাক্তারকে জিজ্ঞাসা করুন।")],
      ("Ask your doctor before changing how you take insulin for any food.",
       "কোনো খাবারের জন্য ইনসুলিন নেওয়ার নিয়ম বদলানোর আগে ডাক্তারকে জিজ্ঞাসা করুন।"),
      (("If I eat chocolate, extra insulin will cancel it.",
        "চকলেট খেলে বাড়তি ইনসুলিন নিলেই সব ঠিক হয়ে যায়।"),
       ("Insulin matches the doses your doctor set. Repeated spikes still harm the body. "
        "Extra insulin can cause a dangerous low.",
        "ইনসুলিন ডাক্তারের ঠিক করা মাত্রার সাথে মেলানো। বারবার সুগার বাড়লে শরীরের ক্ষতি হয়। "
        "বাড়তি ইনসুলিনে সুগার বিপজ্জনকভাবে কমে যেতে পারে।"))),
    C("low_sugar", "sugar", ["insulin", "any"],
      ("Low sugar and the rule of 15", "সুগার কমে যাওয়া ও ১৫ এর নিয়ম"),
      ("Low sugar is below about 70 mg/dL. Treat it quickly. It can also happen at night.",  # VERIFY
       "সুগার প্রায় ৭০ mg/dL এর নিচে নামলে তা কম। দ্রুত ব্যবস্থা নিন। রাতেও এটি হতে পারে।"),
      [("Shaking, sweating, hunger or a fast heartbeat", "কাঁপুনি, ঘাম, ক্ষুধা বা বুক ধড়ফড়"),
       ("At night: wet sheets, nightmares, morning headache", "রাতে: ভেজা বিছানা, দুঃস্বপ্ন, সকালে মাথাব্যথা")],
      [("Rule of 15: take 15 g of fast sugar, then recheck in 15 minutes.",  # VERIFY
        "১৫ এর নিয়ম: ১৫ গ্রাম দ্রুত চিনিজাতীয় কিছু খান, ১৫ মিনিট পর আবার মাপুন।"),
       ("Fast sugar means glucose tablets, juice or sugar in water.",
        "দ্রুত চিনি মানে গ্লুকোজ ট্যাবলেট, ফলের রস বা পানিতে চিনি।"),
       ("Check your sugar before sleep to avoid night lows.", "রাতে সুগার কমা ঠেকাতে ঘুমের আগে সুগার মাপুন।"),
       ("Tell your doctor if lows keep happening.", "বারবার সুগার কমলে ডাক্তারকে জানান।")],
      ("If the person is confused, cannot swallow or faints, call 999 now. Do not give food or drink.",  # VERIFY
       "কেউ বিভ্রান্ত হলে, গিলতে না পারলে বা অজ্ঞান হলে এখনই ৯৯৯ নম্বরে ফোন করুন। খাবার বা পানীয় দেবেন না।")),
    C("high_sick", "sugar", ["any"],
      ("High sugar and sick days", "সুগার বেশি ও অসুস্থতার দিন"),
      ("Illness can raise sugar even if you eat less. Plan ahead with your doctor.",
       "কম খেলেও অসুস্থতায় সুগার বাড়তে পারে। আগে থেকে ডাক্তারের সাথে পরিকল্পনা করুন।"),
      [("Strong thirst and frequent urination", "খুব পিপাসা ও ঘন ঘন প্রস্রাব"),
       ("Vomiting or stomach pain", "বমি বা পেটব্যথা"),
       ("Fruity breath or fast, deep breathing", "ফলের মতো গন্ধের নিঃশ্বাস বা দ্রুত গভীর শ্বাস")],
      [("Sip fluids often, unless your doctor limits fluids.", "ঘন ঘন অল্প তরল খান, তবে ডাক্তার সীমা দিলে তা মানুন।"),
       ("Check your sugar more often.", "সুগার বেশি বার মাপুন।"),
       ("Do not stop or change medicines on your own. Call your doctor for your sick-day plan.",
        "নিজে ওষুধ বন্ধ বা বদলাবেন না। অসুস্থতার দিনের পরিকল্পনার জন্য ডাক্তারকে ফোন করুন।")],
      ("Vomiting with high sugar, fruity breath or drowsiness can be an emergency. Call 999 now.",  # VERIFY
       "বেশি সুগারের সাথে বমি, ফলের মতো গন্ধের নিঃশ্বাস বা ঝিমুনি জরুরি অবস্থা হতে পারে। এখনই ৯৯৯ নম্বরে ফোন করুন।")),
]

EXPLAINERS = {
    "insulin_resistance": X(
        ("Insulin resistance", "ইনসুলিনের কাজ কমে যাওয়া"),
        ("Insulin is a key. Sugar waits outside a sticky lock.", "ইনসুলিন একটি চাবি। আটকে যাওয়া তালার বাইরে সুগার অপেক্ষা করে।"),
        ("Insulin is like a key that opens the door of your body's cells so sugar can go in. "
         "In insulin resistance the lock is sticky. The key works less well, so sugar stays in the blood.",
         "ইনসুলিন একটি চাবির মতো, যা শরীরের কোষের দরজা খুলে সুগারকে ভেতরে ঢুকতে দেয়। "
         "ইনসুলিনের কাজ কমে গেলে তালা আটকে যায়। চাবি ঠিকমতো কাজ করে না, তাই সুগার রক্তে থেকে যায়।"),
        ("The body makes more insulin to push harder. Over time this can tire the body. "
         "Food choices, activity, sleep and the medicines your doctor prescribes can help the lock work better.",
         "শরীর বেশি ইনসুলিন বানিয়ে জোর খাটায়। ধীরে ধীরে এতে শরীর ক্লান্ত হয়। "
         "খাবার, চলাফেরা, ঘুম ও ডাক্তারের দেওয়া ওষুধ তালাকে ভালো কাজ করতে সাহায্য করতে পারে।")),
    "hba1c": X(
        ("HbA1c", "এইচবিএ১সি"),
        ("HbA1c is a 3-month report card. A finger-prick is today's weather.",
         "এইচবিএ১সি তিন মাসের রিপোর্ট কার্ড। আঙুল ফুটিয়ে মাপা সুগার আজকের আবহাওয়া।"),
        ("A sugar reading is like today's weather. HbA1c is like a report card for the last 3 months. "
         "It shows your average, not one good or bad day.",
         "সুগার মাপা আজকের আবহাওয়ার মতো। এইচবিএ১সি গত ৩ মাসের রিপোর্ট কার্ডের মতো। "
         "এটি গড় দেখায়, কোনো একটি ভালো বা খারাপ দিন নয়।"),
        ("Sugar sticks to red blood cells, which live about 3 months. The test measures how much has stuck. "
         "Your doctor sets your target. Some blood conditions can change the result.",
         "সুগার লাল রক্তকণিকায় লেগে থাকে, যা প্রায় ৩ মাস বাঁচে। পরীক্ষায় কতটা লেগেছে তা মাপা হয়। "
         "লক্ষ্য ডাক্তার ঠিক করেন। কিছু রক্তের সমস্যায় ফল বদলে যেতে পারে।")),
    "neuropathy": X(
        ("Neuropathy", "স্নায়ুর ক্ষতি"),
        ("Nerves are wires. High sugar can damage the wiring.", "স্নায়ু তারের মতো। বেশি সুগারে তারের ক্ষতি হতে পারে।"),
        ("Nerves are wires that carry feelings. Years of high sugar can damage the wires. "
         "Signals get weak or mixed up, so you may feel tingling, burning or nothing at all.",
         "স্নায়ু তারের মতো, যা অনুভূতি বয়ে আনে। অনেক বছর বেশি সুগার থাকলে তারের ক্ষতি হতে পারে। "
         "সংকেত দুর্বল বা এলোমেলো হয়, তাই ঝিনঝিন, জ্বালা বা কিছুই টের না পাওয়া যেতে পারে।"),
        ("The feet are affected first because their nerves are the longest. Loss of feeling hides injuries. "
         "Steady sugar, daily foot checks and yearly exams protect you. Other causes, like low B12, can also play a part.",
         "পায়ের স্নায়ু সবচেয়ে লম্বা, তাই আগে পা আক্রান্ত হয়। অনুভূতি কমলে আঘাত লুকিয়ে থাকে। "
         "স্থির সুগার, প্রতিদিন পা দেখা ও বছরে একবার পরীক্ষা আপনাকে রক্ষা করে। "
         "ভিটামিন বি-১২ কম হওয়ার মতো অন্য কারণও থাকতে পারে।")),
    "hypoglycemia": X(
        ("Low blood sugar", "সুগার কমে যাওয়া"),
        ("Your body is a car. Sugar is the fuel.", "আপনার শরীর একটি গাড়ি। সুগার তার জ্বালানি।"),
        ("Sugar is fuel for your body and brain. When the gauge is near empty, you shake, sweat and feel hungry. "
         "Fast sugar refills the tank.",
         "সুগার শরীর ও মস্তিষ্কের জ্বালানি। জ্বালানির কাঁটা শূন্যের কাছে গেলে কাঁপুনি, ঘাম ও ক্ষুধা হয়। "
         "দ্রুত চিনি ট্যাংক আবার ভরে দেয়।"),
        ("Low sugar can follow medicine without enough food, extra activity or alcohol. At night it can be silent. "
         "Treat it fast and tell your doctor if it repeats. Severe lows need emergency help.",
         "খাবার কম রেখে ওষুধ নিলে, বাড়তি পরিশ্রমে বা মদ্যপানে সুগার কমতে পারে। রাতে এটি নীরবে হতে পারে। "
         "দ্রুত ব্যবস্থা নিন, বারবার হলে ডাক্তারকে জানান। তীব্র কমে গেলে জরুরি সাহায্য লাগে।")),
}
