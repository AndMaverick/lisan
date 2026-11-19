"""Name pairs the matcher is checked against. Written by hand for this library: a regression set, not an independent benchmark.
Arabic is written as literal text. Each pair is (a, b)."""

SAME = [
    # Latin to Latin: spelling variants of one name
    ("Mohammed", "Muhammad"), ("Mohamed", "Mohammad"), ("Muhammed", "Mohamad"), ("Khaled", "Khalid"), ("Abdullah", "Abdallah"),
    ("Abdullah", "Abd Allah"), ("Abdul Rahman", "Abdurrahman"), ("Abd al-Rahman", "Abdel Rahman"), ("Youssef", "Yusuf"),
    ("Hussein", "Husain"), ("Mustafa", "Moustafa"), ("Ibrahim", "Ebrahim"), ("Ismail", "Esmail"), ("Fatima", "Fatimah"),
    ("Aisha", "Ayesha"), ("Nour al-Din", "Noureddine"), ("Mohammed bin Rashid Al Maktoum", "Muhammad ibn Rashid Al Maktum"),
    ("Omar", "Umar"), ("Osama", "Usama"), ("Tariq", "Tarek"), ("Qasim", "Kassim"), ("Jamal", "Gamal"), ("Saeed", "Said"),
    ("Waleed", "Walid"), ("Zainab", "Zaynab"), ("Rashid", "Rasheed"), ("Alhajri", "Al Hajri"), ("Dawood", "Daoud"),
    ("Abdul Aziz", "Abdelaziz"), ("Abdul Latif", "Abdellatif"), ("Sultan", "Soltan"), ("Mansour", "Mansoor"), ("Hassan", "Hasan"),
    ("Ahmed Al Mansoori", "Ahmad Almansouri"), ("Khalifa", "Khalifah"), ("Sheikh Zayed bin Sultan", "Shaikh Zayed ibn Sultan"),
    # arabizi
    ("7amad", "Hamad"), ("3omar", "Omar"), ("5alid", "Khalid"),
    # Arabic to Latin
    ("محمد", "Muhammad"), ("عبد الرحمن", "Abdul Rahman"), ("عبدالله", "Abdullah"), ("عبد الله", "Abdullah"), ("خالد", "Khaled"),
    ("يوسف", "Yousef"), ("فاطمة", "Fatima"), ("عائشة", "Aisha"), ("نور الدين", "Noureddine"), ("مصطفى", "Mostafa"),
    ("إبراهيم", "Ibrahim"), ("حسين", "Hussein"), ("عمر", "Omar"), ("عبد اللطيف", "Abdul Latif"), ("سلطان", "Sultan"),
    ("منصور", "Mansour"), ("حمدان", "Hamdan"), ("زينب", "Zainab"), ("راشد", "Rashid"), ("طارق", "Tariq"), ("قاسم", "Qasim"),
    ("جمال", "Jamal"), ("عثمان", "Osman"), ("سعيد", "Saeed"), ("وليد", "Waleed"), ("محمد بن راشد آل مكتوم", "Mohammed bin Rashid Al Maktoum"),
    ("أحمد المنصوري", "Ahmed Al Mansoori"), ("خليفة بن زايد", "Khalifa bin Zayed"), ("الشيخ زايد", "Sheikh Zayed"),
    # Arabic to Arabic: spelling variants
    ("أحمد", "احمد"), ("عبدالله", "عبد الله"), ("مُحَمَّد", "محمد"), ("إبراهيم", "ابراهيم"), ("آمنة", "امنة"), ("فاطمة", "فاطمه"),
    ("الحسن", "حسن"), ("عبدالرحمن", "عبد الرحمن"),
]

DIFFERENT = [
    ("Mohammed", "Ahmed"), ("Khalid", "Walid"), ("Hassan", "Hamza"), ("Salim", "Salman"), ("Karim", "Kamal"), ("Fatima", "Aisha"),
    ("Yusuf", "Yunus"), ("Ali", "Omar"), ("Abdullah", "Abdulaziz"), ("Abdul Rahman", "Abdul Rahim"), ("Mohammed Ali", "Mohammed Omar"),
    ("Khalid bin Walid", "Khalid bin Salman"), ("Ibrahim", "Ismail"), ("Hamdan", "Hamad"), ("Sultan", "Salman"), ("Nasser", "Nasim"),
    ("Tamer", "Samer"), ("Jaber", "Jamal"), ("Faisal", "Fahad"), ("Nabil", "Nadim"), ("Saif", "Saleh"), ("Mohammed Al Rashid", "Ahmed Al Rashid"),
    ("Sheikh Zayed", "Sheikh Hamdan"), ("Layla", "Lubna"), ("Hind", "Hanan"),
    ("محمد", "Ahmed"), ("خالد", "Walid"), ("فاطمة", "Aisha"), ("يوسف", "Yunus"), ("عبد الله", "Abdulaziz"), ("عبد الرحمن", "Abdul Rahim"),
    ("سلمان", "Sultan"), ("كريم", "Kamal"), ("نبيل", "Nadim"), ("حمدان", "Hamad"), ("ليلى", "Lubna"),
    ("حسن", "حسين"), ("محمد", "أحمد"), ("خالد", "وليد"), ("سلمان", "سليمان"), ("كريم", "كمال"), ("عبد الله", "عبد العزيز"),
]

# Pairs the skeleton cannot tell apart or tells apart too finely. They are listed so the limits are explicit, and the tests pin them.
COLLIDE = [  # different names, matched: vowels are what separates them
    ("Rashid", "Rashad"), ("Omar", "Amir"), ("حسن", "Hussein"), ("Nawaf", "Naif"), ("Abdulrahman", "Abdulrahim"),
]
MISSED = [  # the same name, not matched: the spellings differ by more than the scorer forgives
    ("Mohammed", "Mohd"), ("Yusuf", "Joseph"),
]
