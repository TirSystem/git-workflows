"""MIL-013 task 2 (ADR-0012): compare detection methods on the corpus.

Needs langdetect, langid and lingua-language-detector installed (not part of the
test requirements). Usage: python compare_detectors.py [-v]
"""

import csv
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

CORPUS = Path(__file__).resolve().parent
rows = []
for name in ("english.tsv", "foreign.tsv"):
    with (CORPUS / name).open(encoding="utf-8", newline="") as handle:
        rows += [(r["lang"], r["text"]) for r in csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)]

# ---------- A: rule-based
NON_ENGLISH_LETTERS = re.compile(r"[æøåäöüßéèêàâçñôîûœ]", re.I)
STOP = {
    "en": "the a an of to and is in it that this for on with as are be by or if not from at which can will we you "
    "when then use used only each all any its into has have was were been do does done so but also than how what".split(),
    "da": "og er det en at i jeg til på for med af ikke den der som vi skal kan har de om men et fra hvis her kun "
    "efter før bliver være dette denne mappen filen listen brugeren serveren tjek hent gem slet læs opret".split(),
    "ms": "dan yang untuk dengan ini itu di dalam pada akan atau tidak dari ke kita jika boleh adalah mesti sama "
    "semak fail pelayan pengguna senarai kira baris guna supaya apabila sebelum selepas daripada".split(),
    "other": "der die das und ist nicht ein eine mit von zu den dem auf für wir och att som en är inte för med "
    "på av vi le la les des est une pour pas dans que qui nous sur om det jeg å ikke vi må".split(),
}


def rule_based(text: str) -> bool:
    if NON_ENGLISH_LETTERS.search(text):
        return True
    words = re.findall(r"[a-zA-ZæøåÆØÅ']+", text.lower())
    score = {k: sum(w in set(v) for w in words) for k, v in STOP.items()}
    foreign = max(score["da"], score["ms"], score["other"])
    return foreign >= 2 and foreign > score["en"]


# ---------- B: langdetect
def make_langdetect():
    from langdetect import DetectorFactory, detect_langs

    DetectorFactory.seed = 0

    def run(text: str, threshold: float = 0.8) -> bool:
        try:
            best = detect_langs(text)[0]
        except Exception:
            return False
        return best.lang != "en" and best.prob >= threshold

    return run


# ---------- C: langid
def make_langid():
    import langid

    langid.set_languages(["en", "da", "no", "sv", "de", "fr", "ms", "id", "nl"])

    def run(text: str, threshold: float = 0.0) -> bool:
        lang, _score = langid.classify(text)
        return lang != "en"

    return run


# ---------- D: lingua
def make_lingua():
    from lingua import Language, LanguageDetectorBuilder

    names = ["ENGLISH", "DANISH", "BOKMAL", "NYNORSK", "SWEDISH", "GERMAN", "FRENCH", "MALAY", "INDONESIAN", "DUTCH"]
    languages = [getattr(Language, n) for n in names if hasattr(Language, n)]
    print("lingua languages:", [l.name for l in languages], file=sys.stderr)
    detector = LanguageDetectorBuilder.from_languages(*languages).build()

    def run(text: str, threshold: float = 0.5) -> bool:
        values = detector.compute_language_confidence_values(text)
        if not values:
            return False
        top = values[0]
        return top.language != Language.ENGLISH and top.value >= threshold

    return run


METHODS = {"rule": rule_based}
for name, factory in (("langdetect", make_langdetect), ("langid", make_langid), ("lingua", make_lingua)):
    try:
        METHODS[name] = factory()
    except Exception as error:  # a method that cannot be built is reported, not hidden
        print("cannot build", name, error, file=sys.stderr)


def report(name: str, predict) -> None:
    started = time.perf_counter()
    flagged = defaultdict(lambda: [0, 0])  # lang -> [flagged, total]
    wrong = []
    for lang, text in rows:
        is_flagged = predict(text)
        flagged[lang][1] += 1
        if is_flagged:
            flagged[lang][0] += 1
        if (lang == "en") == is_flagged:
            wrong.append((lang, text))
    elapsed = time.perf_counter() - started
    foreign = [k for k in flagged if k != "en"]
    line = f"{name:12s} " + " ".join(f"{k}={flagged[k][0]}/{flagged[k][1]}" for k in sorted(foreign))
    print(f"{line}  FALSE-POSITIVES en={flagged['en'][0]}/{flagged['en'][1]}  {elapsed:.2f}s/{len(rows)}")
    if "-v" in sys.argv:
        for lang, text in wrong[:25]:
            print("    ", lang, "|", text[:80])


for name, predict in METHODS.items():
    report(name, predict)
