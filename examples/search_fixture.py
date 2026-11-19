"""A small retrieval fixture: 16 Arabic news-style sentences and, for each, one query that asks for it in a different written form
(diacritics, hamza and alef forms, teh marbuta typed as heh, Persian letters, Eastern digits, a definite article or clitic added or
dropped). Written by hand for this library. It measures whether spelling variation breaks matching; it says nothing about relevance
ranking on real collections."""

DOCS = {
    "library": "افتتحت الجامعة مكتبة جديدة للطلاب في المدينة",
    "vaccine": "أعلنت وزارة الصحة عن حملة تطعيم ضد الإنفلونزا",
    "oil": "ارتفعت أسعار النفط بعد اجتماع المنتجين",
    "coding": "تعلم الأطفال البرمجة في المدارس الابتدائية",
    "solar": "نشر الباحثون دراسة عن الطاقة الشمسية",
    "history": "صدر كتاب جديد عن تاريخ دبي",
    "bookfair": "افتتح المعرض الدولي للكتاب في الشارقة",
    "visitors": "بلغ عدد الزوار ١٢٠٠ زائر في اليوم الأول",
    "holiday": "قَرَّرَ المَجْلِسُ تَمْدِيدَ العُطْلَةِ الصَّيْفِيَّةِ",
    "ecommerce": "ازدهرت التجارة الإلكترونية في الخليج",
    "research": "أسس مرکز البحوث الجديد في العاصمة",
    "summit": "انعقدت القمة العربية في الرياض",
    "weather": "تتوقع الأرصاد الجوية هطول الأمطار غدا",
    "trip": "نظمت المدرسة رحلة علمية للطلاب",
    "bridge": "افتتح الوزير الجسر الجديد على النهر",
    "airport": "توسعة مطار دبي الدولي تستقبل ملايين المسافرين",
}

QUERIES = {
    "library": "مكتبه جديده الطلاب",
    "vaccine": "حمله تطعيم الانفلونزا",
    "oil": "اسعار النفط",
    "coding": "البرمجه للاطفال",
    "solar": "الباحثين الطاقه الشمسيه",
    "history": "كتاب تاريخ دبي",
    "bookfair": "معرض الكتاب الشارقه",
    "visitors": "1200 زائر",
    "holiday": "تمديد العطله الصيفيه",
    "ecommerce": "التجاره الالكترونيه الخليج",
    "research": "مركز البحوث",
    "summit": "القمه العربيه الرياض",
    "weather": "الارصاد الجويه امطار",
    "trip": "المدرسه رحله علميه",
    "bridge": "الجسر الجديد النهر",
    "airport": "مطار دبي المسافرين",
}

# Second set: the query uses a different inflection of the key word (plural or feminine suffix, article, clitic), which spelling
# normalization alone cannot bridge.
MORPH_DOCS = {
    "teachers": "كرم الوزير المعلمين المتميزين في الحفل",
    "players": "تدرب اللاعبون على ملعب النادي",
    "staff": "كرمت الشركة الموظفات المتميزات",
    "exam": "نجح الطالب في الامتحان",
    "firms": "تصدرت الشركات قائمة الأرباح",
    "cities": "زار الوفد المدن الكبرى",
}
MORPH_QUERIES = {
    "teachers": "المعلمون",
    "players": "لاعبين",
    "staff": "موظفة",
    "exam": "بالامتحانات",
    "firms": "الشركة",
    "cities": "المدينة",  # fails: broken plural (mudun / madina) is out of reach of a light stemmer
}
