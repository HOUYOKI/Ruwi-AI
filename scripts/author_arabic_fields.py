"""One-time data-authoring script: adds name_ar/age_ar/location_ar/material_ar/
description_ar to every entry in data/artifacts.json, grounded in the existing
ocr_arabic OCR blob (or, where that's absent, a faithful translation of the
existing English fields). Run once, then this file has done its job.
"""
import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "artifacts.json"

# LRM/RLM and other stray bidi-control characters that show up as OCR/encoding
# noise (e.g. id 50's ocr_arabic has ~2500 trailing U+200E marks after the
# real text) - stripped before parsing so they never leak into stored content.
_BIDI_CODEPOINTS = (
    0x200B, 0x200C, 0x200D, 0x200E, 0x200F,
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
    0x2066, 0x2067, 0x2068, 0x2069,
)
BIDI_NOISE = re.compile("[" + "".join(chr(c) for c in _BIDI_CODEPOINTS) + "]")


def clean(text: str) -> str:
    text = BIDI_NOISE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


AGE_KEYWORDS = ("قبل الميلاد", "الميلادي", "الميلاد", "قرن", "عام", "سنة", "عصر", "هـ")
# A line/paragraph reads as a standalone age field if it carries one of the
# Arabic era keywords (or is basically just a number/date range, e.g. "2000",
# "8000 - 4000", "1327 هـ (1909 م)") AND has no sentence punctuation. Real
# description prose always has at least one "،" or "." somewhere in it (every
# sampled description does); a dual Hijri/Gregorian age line never does, even
# a long one like "القرن الثالث - القرن السادس الهجري (القرن التاسع - القرن
# الثاني عشر الميلادي)" — so punctuation-absence is a much more reliable
# signal here than a raw length cutoff (that cutoff false-negatived on
# exactly these long-but-real age lines).
_NUMERIC_ONLY = re.compile(r"^[\d,،\-–\s]+$")
_HAS_SENTENCE_PUNCTUATION = re.compile(r"[،.]")

_ARABIC_LETTER = re.compile(r"[؀-ۿ]")
_LATIN_LETTER = re.compile(r"[A-Za-z]")


def looks_like_age(text: str) -> bool:
    text = text.strip()
    if not text or _HAS_SENTENCE_PUNCTUATION.search(text):
        return False
    if _NUMERIC_ONLY.match(text):
        return True
    return any(kw in text for kw in AGE_KEYWORDS)


def is_noise_line(line: str) -> bool:
    """A couple of source panels have a leading or trailing exhibit-hall
    label baked into the OCR text (e.g. id 13's "قاعة الإسلام والجزيرة
    العربية\\nIslam and Arabia Gallery", id 45's trailing "قاعة الممالك
    العربية\\nArabian Kingdoms Gallery") — not part of the artifact's own
    name/age/location/description, so it's filtered out before parsing."""
    line = line.strip()
    if line.startswith("قاعة"):
        return True
    # A line with Latin letters and no Arabic letters at all is the
    # gallery's English name (the bilingual label's second line).
    if _LATIN_LETTER.search(line) and not _ARABIC_LETTER.search(line):
        return True
    return False


_MAX_LOCATION_FRAGMENT_LEN = 40


def split_body(lines: list[str], peel_trailing_location: bool = False) -> tuple[str, str, str]:
    """Given the lines that follow the title (still one physical line each),
    finds the age within them and splits into (description, age, trailing).
    Age can be a single line or wrap across several (e.g. a dual Hijri/
    Gregorian range) — found as the LAST contiguous run of lines that each
    individually pass looks_like_age. Everything before that run is
    description; anything after it (rare — usually only when a location
    follows the age with no blank line) is trailing.

    If no age-line is found anywhere, behavior depends on peel_trailing_location:
    - False (used when the caller already has a separate paragraph to hold
      any location — see the len(paragraphs)==2 branch below): the whole
      thing is treated as description. A short, comma-free, wrapped
      continuation line (e.g. id 101's second title/description line) reads
      exactly like a location fragment would, so without another source for
      the location this can't be told apart from real (if terse) prose —
      description is the safer default since it never silently drops text.
    - True (used by the line-style branch, which has nowhere else to put a
      location): walks backward peeling off trailing lines that have no
      comma and are short (<=40 chars — real description sentences run much
      longer; a bare place-name line doesn't) into a trailing location
      block, stopping at the first line that doesn't qualify.
    """
    if not lines:
        return "", "", ""

    is_age = [looks_like_age(line) for line in lines]
    run_start = run_end = None
    i = 0
    while i < len(lines):
        if is_age[i]:
            j = i
            while j < len(lines) and is_age[j]:
                j += 1
            run_start, run_end = i, j - 1  # keep overwriting -> last run wins
            i = j
        else:
            i += 1

    if run_start is not None:
        description = " ".join(lines[:run_start])
        age = " ".join(lines[run_start : run_end + 1])
        trailing = " ".join(lines[run_end + 1 :])
        return clean(description), clean(age), clean(trailing)

    if peel_trailing_location:
        idx = len(lines)
        while idx > 0 and "،" not in lines[idx - 1] and len(lines[idx - 1]) <= _MAX_LOCATION_FRAGMENT_LEN:
            idx -= 1
        description = " ".join(lines[:idx])
        trailing = " ".join(lines[idx:])
        return clean(description), "", clean(trailing)

    if any(_HAS_SENTENCE_PUNCTUATION.search(line) for line in lines):
        return clean(" ".join(lines)), "", ""
    return "", "", clean(" ".join(lines))


def parse_ocr(ocr: str) -> dict | None:
    """ocr_arabic comes in two shapes, confirmed by sampling ~10 entries
    across the file:
    - "paragraph style" (blank-line separated): title+description, then an
      age paragraph, then a location paragraph — each may itself span
      multiple lines (e.g. id 1's location is 2 lines).
    - "line style" (no blank lines): title \\n description \\n [age] \\n
      location, one field per line, and the age line is sometimes absent
      entirely (the date is mentioned inline in the description instead —
      in that case it's left out rather than guessed).
    Returns None only if there's no usable title line at all.
    """
    ocr = "\n".join(line for line in ocr.split("\n") if not is_noise_line(line))
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", ocr.strip()) if p.strip()]
    if not paragraphs:
        return None

    if len(paragraphs) >= 2:
        first_lines = [line.strip() for line in paragraphs[0].splitlines() if line.strip()]
        if not first_lines:
            return None
        name_ar = clean(first_lines[0])
        # Usually first_lines[1:] is pure description, but some panels have
        # no blank line between the description (or even the title, if
        # there's no description at all) and the age — split_body finds and
        # extracts that blended age instead of leaving it stuck in the text.
        description_ar, blended_age_ar, extra = split_body(first_lines[1:])

        if len(paragraphs) == 2:
            # One trailing paragraph only. It's sometimes itself two lines
            # glued together with no blank line between them (age then
            # location) rather than a single field, so check inside it too.
            inner_lines = [line.strip() for line in paragraphs[1].splitlines() if line.strip()]
            if inner_lines and looks_like_age(inner_lines[0]):
                age_ar = clean(inner_lines[0])
                location_ar = clean(" ".join(inner_lines[1:])) if len(inner_lines) > 1 else ""
            elif looks_like_age(paragraphs[1]):
                age_ar, location_ar = clean(paragraphs[1]), ""
            else:
                age_ar, location_ar = "", clean(paragraphs[1])
            if blended_age_ar and not age_ar:
                age_ar = blended_age_ar
            if extra:
                location_ar = clean(f"{extra} {location_ar}") if location_ar else extra
        else:
            age_ar = clean(paragraphs[1])
            location_ar = clean(" ".join(paragraphs[2:]))

        return {"name_ar": name_ar, "description_ar": description_ar, "age_ar": age_ar, "location_ar": location_ar}

    # Line style: no blank lines anywhere in the OCR text.
    lines = [line.strip() for line in ocr.splitlines() if line.strip()]
    if not lines:
        return None
    name_ar = clean(lines[0])
    remaining = lines[1:]
    if not remaining:
        return {"name_ar": name_ar, "description_ar": "", "age_ar": "", "location_ar": ""}

    description_ar, age_ar, location_ar = split_body(remaining, peel_trailing_location=True)
    return {"name_ar": name_ar, "description_ar": description_ar, "age_ar": age_ar, "location_ar": location_ar}


# Faithful Arabic translations for ids 51/52 (no ocr_arabic ground truth -
# composed directly from their existing English fields).
MANUAL_TRANSLATIONS = {
    51: {
        "name_ar": "جرة مزجّجة ومصباح زيت برونزي وتمثال جمل من قرية الفاو",
        "description_ar": (
            "مجموعة أثرية رائعة مكوّنة من ثلاث قطع اكتُشفت في قرية الفاو، عاصمة مملكة كِندة القديمة. "
            "تُظهر هذه المجموعة براعة الصناعة اليدوية وتنوع الروابط التجارية للمنطقة. على اليسار جرة فخارية "
            "صغيرة مزجّجة محفوظة بعناية، بطلاء أخضر مائل إلى الفيروزي يدل على تأثيرات فارثية أو رافدينية. "
            "وفي المنتصف مصباح زيت برونزي بفوهة ممدودة أنيقة ومقبض على شكل ورقة زخرفية. وعلى اليمين تمثال "
            "برونزي مصغّر لجمل يجسّد حيوان الحمل الذي شكّل عصب طرق التجارة عبر الجزيرة العربية. تعكس هذه "
            "القطع معًا الحياة اليومية والبراعة الفنية والحيوية الاقتصادية لمحطة قوافل رئيسية على حافة الربع الخالي."
        ),
        "age_ar": "القرن الأول قبل الميلاد - القرن الثالث الميلادي",
        "location_ar": "قرية الفاو، المملكة العربية السعودية",
    },
    52: {
        "name_ar": "إبريق صغير مزجّج ومصباح زيت برونزي من العصر الإسلامي المبكر",
        "description_ar": (
            "زوج أنيق من الأدوات اليومية يعكس الحياة المنزلية والبراعة الفنية في العصر الإسلامي المبكر. "
            "يتميز الإبريق الصغير الفخاري الأخضر المزجّج بطلاء قلوي سميك زاهي، وهي تقنية صُقلت كثيرًا في "
            "العصر العباسي لمحاكاة الأواني المستوردة الفاخرة. وبجانبه مصباح زيت برونزي مصبوب بمقبض حلقي "
            "ومسند إبهام على شكل نخلة مزخرفة، وفوهة ممدودة لحمل الفتيلة. اكتُشفت هذه القطع في تنقيبات أثرية "
            "بالمملكة العربية السعودية، وتقدّم لمحة حميمة عن التطور التقني والاحتياجات العملية والذوق الجمالي "
            "لمجتمعات العصر الإسلامي المبكر على طول طرق التجارة والحج التاريخية."
        ),
        "age_ar": "العصر الإسلامي المبكر (القرن الثامن - العاشر الميلادي)",
        "location_ar": "الربذة، المملكة العربية السعودية",
    },
    # ids 17 and 55: ocr_arabic exists but only covers title+age (single
    # sparse line/pair, no description or location at all) — name_ar/age_ar
    # below are taken verbatim from that OCR text; description_ar/location_ar
    # have no Arabic source to ground in, so they're translated from the
    # entry's own English fields instead, same as the no-ocr_arabic ids above.
    17: {
        "name_ar": "محبرة خشبية مزخرفة",
        "description_ar": (
            "محبرة خشبية تقليدية منحوتة بعناية، بغطاء دائري زخرفي وجسم ممدود مزيّن بزخارف هندسية ونباتية. "
            "تعود إلى القرن التاسع عشر والعشرين الميلادي، وتمثل أدوات الكتابة والحرفية الفنية في عصر توحيد "
            "المملكة العربية السعودية."
        ),
        "age_ar": "القرن التاسع عشر - القرن العشرين الميلادي",
        "location_ar": "المملكة العربية السعودية",
    },
    55: {
        "name_ar": "سلطانية فضية مزخرفة",
        "description_ar": (
            "سلطانية فضية بديعة الزخرفة تعود إلى عام 750هـ (1258م)، تعكس براعة الصناعة في العصر الذهبي "
            "الإسلامي. يتميز الإناء بجسم مستدق برفق يرتكز على قاعدة صغيرة، ومُزيّن بأشرطة محفورة يدويًا "
            "بزخارف هندسية ونباتية دقيقة حول الحافة العلوية، إضافة إلى مدالية مركزية بخط الكتابة العربية. "
            "كانت مثل هذه الأواني الفضية الفاخرة تُستخدم كأدوات مائدة راقية، تعبّر عن الثراء والمكانة الرفيعة "
            "والرقي الفني الذي ساد المجتمعات الإسلامية في منتصف القرن الثالث عشر الميلادي."
        ),
        "age_ar": "750 هـ (1258 م)",
        "location_ar": "المملكة العربية السعودية (معروضة في قاعة الإسلام والجزيرة العربية)",
    },
    # id 53: ocr_arabic's title itself wraps across 2 physical lines with no
    # delimiter separating it from the age text that follows (also wrapped,
    # across 4 lines with keyword-less bridge fragments like "عشر- التاسع
    # عشر") — not reliably splittable by the general parser. name_ar/age_ar
    # below are the OCR lines themselves, just correctly joined by hand;
    # description_ar/location_ar have no Arabic source text at all (same gap
    # as ids 17/55) so they're translated from the English fields.
    53: {
        "name_ar": "مصباح نحاسي على شكل طائر طويل العنق",
        "description_ar": (
            "مصباح نحاسي بديع مصنوع من سبيكة النحاس على هيئة طائر طويل العنق، يعود إلى الفترة ما بين "
            "القرن العاشر والثالث عشر الهجري (السادس عشر إلى التاسع عشر الميلادي). تُظهر هذه التحفة من "
            "الأعمال المعدنية الإسلامية براعة صناعية فائقة، بعنق منحنٍ برشاقة يعمل كمقبض عملي، وينتهي برأس "
            "طائر مصمم بأسلوب مُجرّد. صُمم المصباح للاستخدام والجمال معًا، ويعكس التقليد الفني الغني لدمج "
            "العناصر الحيوانية في الأدوات اليومية خلال العصور الإسلامية."
        ),
        "age_ar": "القرن العاشر- الثالث عشر الهجري (القرن السادس عشر- التاسع عشر الميلادي)",
        "location_ar": "المتحف الوطني السعودي",
    },
}

# The material isn't part of the standard title/description/age/location
# shape, but it does sometimes show up inside ocr_arabic anyway — most often
# baked into the title itself (e.g. id 90's "مذبح من الحجر الجيري" = "altar
# OF limestone"), occasionally in the description. So material_ar isn't a
# blind translation: for every entry, the full ocr_arabic text is checked
# for one of these Arabic root words for its known English `material` first;
# only when none of them appear anywhere does it fall back to translating
# the English field with no ocr_arabic confirmation at all.
MATERIAL_AR = {
    "Alabaster": "الألباستر",
    "Basalt": "البازلت",
    "Brass": "النحاس الأصفر",
    "Bronze": "البرونز",
    "Bronze and Glazed Ceramic": "البرونز والخزف المزجج",
    "Cast Bronze": "البرونز المصبوب",
    "Ceramic": "الخزف",
    "Clay": "الطين",
    "Clay (Ceramic)": "الطين (الخزف)",
    "Clay (Pottery)": "الطين (الفخار)",
    "Copper": "النحاس",
    "Fossilized Bone": "عظم متحجر",
    "Gilded Copper": "النحاس المذهّب",
    "Gilded Pottery": "الفخار المذهّب",
    "Gilded Silver (Gold-Plated Silver)": "الفضة المذهّبة (فضة مطلية بالذهب)",
    "Glass": "الزجاج",
    "Glazed Ceramic": "الخزف المزجج",
    "Glazed Ceramic and Bronze": "الخزف المزجج والبرونز",
    "Glazed Pottery": "الفخار المزجج",
    "Glazed ceramic and gold": "الخزف المزجج والذهب",
    "Gold": "الذهب",
    "Hammered Copper with Gilding": "النحاس المطروق المذهّب",
    "Iron and Nickel": "الحديد والنيكل",
    "Iron with gold and silver inlay": "الحديد المطعّم بالذهب والفضة",
    "Limestone": "الحجر الجيري",
    "Marble": "الرخام",
    "Obsidian (Volcanic Glass)": "السبج (الزجاج البركاني)",
    "Petrified Wood": "الخشب المتحجر",
    "Plaster and pigment": "الجص والأصباغ",
    "Pottery": "الفخار",
    "Pottery (Clay)": "الفخار (الطين)",
    "Pottery (Clay) and Bitumen": "الفخار (الطين) والقار",
    "Red Clay": "الطين الأحمر",
    "Sandstone": "الحجر الرملي",
    "Silver": "الفضة",
    "Silver and semi-precious stone": "الفضة وأحجار شبه كريمة",
    "Silver, Steel, and Leather": "الفضة والصلب والجلد",
    "Soapstone": "حجر الصابون",
    "Soapstone (Steatite)": "حجر الصابون (الستياتيت)",
    "Stone": "الحجر",
    "Stone (carved, Islamic calligraphy inscription)": "الحجر (منقوش، نقش بخط عربي إسلامي)",
    "White Marble": "الرخام الأبيض",
    "Wood": "الخشب",
    "Wood, Iron, and Brass": "الخشب والحديد والنحاس الأصفر",
}

# Arabic root words to search ocr_arabic for, per English material — used
# only to decide whether MATERIAL_AR's translation is OCR-confirmed or not
# (see MATERIAL_AR's comment above).
MATERIAL_ROOTS: dict[str, tuple[str, ...]] = {
    "Alabaster": ("ألباستر", "مرمر"),
    "Basalt": ("بازلت",),
    "Brass": ("نحاس أصفر", "نحاس"),
    "Bronze": ("برونز",),
    "Bronze and Glazed Ceramic": ("برونز", "خزف"),
    "Cast Bronze": ("برونز",),
    "Ceramic": ("خزف",),
    "Clay": ("طين",),
    "Clay (Ceramic)": ("طين", "خزف"),
    "Clay (Pottery)": ("طين", "فخار"),
    "Copper": ("نحاس",),
    "Fossilized Bone": ("عظم",),
    "Gilded Copper": ("نحاس", "مذهّب", "مذهب"),
    "Gilded Pottery": ("فخار", "مذهّب", "مذهب"),
    "Gilded Silver (Gold-Plated Silver)": ("فضة", "فضي", "مذهّب", "مذهب"),
    "Glass": ("زجاج",),
    "Glazed Ceramic": ("خزف",),
    "Glazed Ceramic and Bronze": ("خزف", "برونز"),
    "Glazed Pottery": ("فخار",),
    "Glazed ceramic and gold": ("خزف", "ذهب"),
    "Gold": ("ذهب",),
    "Hammered Copper with Gilding": ("نحاس",),
    "Iron and Nickel": ("حديد", "نيكل"),
    "Iron with gold and silver inlay": ("حديد",),
    "Limestone": ("حجر جيري", "حجر"),
    "Marble": ("رخام",),
    "Obsidian (Volcanic Glass)": ("سبج",),
    "Petrified Wood": ("خشب",),
    "Plaster and pigment": ("جص",),
    "Pottery": ("فخار",),
    "Pottery (Clay)": ("فخار", "طين"),
    "Pottery (Clay) and Bitumen": ("فخار", "قار"),
    "Red Clay": ("طين",),
    "Sandstone": ("حجر رملي", "حجر"),
    "Silver": ("فضة", "فضي"),
    "Silver and semi-precious stone": ("فضة", "فضي"),
    "Silver, Steel, and Leather": ("فضة", "فضي", "جلد"),
    "Soapstone": ("حجر الصابون",),
    "Soapstone (Steatite)": ("حجر الصابون",),
    "Stone": ("حجر",),
    "Stone (carved, Islamic calligraphy inscription)": ("حجر",),
    "White Marble": ("رخام",),
    "Wood": ("خشب",),
    "Wood, Iron, and Brass": ("خشب", "حديد", "نحاس"),
}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    assert len(data) == 102, f"expected 102 entries, found {len(data)}"

    manual_ids = set(MANUAL_TRANSLATIONS)
    flagged_paragraph_count: list[int] = []
    flagged_no_material: list[int] = []
    flagged_unparseable: list[int] = []
    flagged_material_confirmed: list[int] = []
    flagged_material_translated: list[int] = []

    for entry in data:
        aid = entry["id"]

        if aid in manual_ids:
            entry.update(MANUAL_TRANSLATIONS[aid])
        else:
            parsed = parse_ocr(entry.get("ocr_arabic") or "")
            if parsed is None:
                flagged_unparseable.append(aid)
                continue
            if not parsed["age_ar"]:
                # Not necessarily wrong — some source panels state the date
                # inline in the description rather than as its own line —
                # but worth a human glance.
                flagged_paragraph_count.append(aid)
            entry["name_ar"] = parsed["name_ar"]
            entry["description_ar"] = parsed["description_ar"]
            entry["age_ar"] = parsed["age_ar"]
            entry["location_ar"] = parsed["location_ar"]

        material_en = entry.get("material")
        if material_en:
            material_ar = MATERIAL_AR.get(material_en)
            if material_ar is None:
                flagged_no_material.append(aid)
            else:
                entry["material_ar"] = material_ar
                ocr_text = entry.get("ocr_arabic") or ""
                roots = MATERIAL_ROOTS.get(material_en, ())
                if any(root in ocr_text for root in roots):
                    flagged_material_confirmed.append(aid)
                else:
                    flagged_material_translated.append(aid)
        else:
            flagged_no_material.append(aid)

    DATA_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Wrote {DATA_PATH}")
    print(f"Unparseable ocr_arabic (no _ar fields written): {flagged_unparseable}")
    print(f"No standalone age line found (date likely inline in description, spot-check): {flagged_paragraph_count}")
    print(f"material_ar confirmed by ocr_arabic: {len(flagged_material_confirmed)} ids")
    print(f"material_ar translated only, not stated in ocr_arabic: {flagged_material_translated}")
    print(f"No material_ar (missing English material field): {flagged_no_material}")

    reloaded = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    assert len(reloaded) == 102
    assert {e["id"] for e in reloaded} == set(range(1, 103))
    missing_name_ar = [e["id"] for e in reloaded if not e.get("name_ar")]
    missing_desc_ar = [e["id"] for e in reloaded if not e.get("description_ar")]
    missing_age_ar = [e["id"] for e in reloaded if not e.get("age_ar")]
    missing_loc_ar = [e["id"] for e in reloaded if not e.get("location_ar")]
    missing_mat_ar = [e["id"] for e in reloaded if not e.get("material_ar")]
    print(f"Missing name_ar: {missing_name_ar}")
    print(f"Missing description_ar: {missing_desc_ar}")
    print(f"Missing age_ar: {missing_age_ar}")
    print(f"Missing location_ar: {missing_loc_ar}")
    print(f"Missing material_ar: {missing_mat_ar}")


if __name__ == "__main__":
    main()
