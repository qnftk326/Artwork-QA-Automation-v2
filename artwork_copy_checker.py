"""Position-independent bilingual copy checks for the packaging artwork."""
import re
import unicodedata
from difflib import SequenceMatcher

from artwork_copy_reference import REFERENCES


def normalize(text):
    text = unicodedata.normalize("NFKC", str(text or "")).casefold()
    text = text.replace("–", "-").replace("—", "-")
    return re.sub(r"[^0-9a-z가-힣°%./+-]+", "", text)


def _find(expected, observed):
    target = normalize(expected)
    if not target:
        return "NOT_CONFIGURED", "기준 문구 미등록"
    native = normalize(observed.get("native", ""))
    ocr = normalize(observed.get("ocr", ""))
    if target in native:
        return "EXACT", "PDF 텍스트 레이어에서 확인"
    if target in ocr:
        return "OCR_REVIEW", "OCR에서만 확인 · 원본 PDF 대조 필요"
    best = 0.0
    for source in (native, ocr):
        if not source:
            continue
        width = len(target)
        for start in range(max(1, len(source) - width + 1)):
            candidate = source[start:start + width]
            best = max(best, SequenceMatcher(None, target, candidate, autojunk=False).ratio())
    if best >= 0.72:
        return "REVIEW", f"유사 문구 후보({best:.0%}) · 원본 확인 필요"
    return "MISSING", "PDF에서 기준 문구를 찾지 못함"


def check_artwork(observed_by_file):
    results = []
    for filename, observed in observed_by_file.items():
        for ref in REFERENCES:
            en_status, en_reason = _find(ref["en"], observed)
            kr_status, kr_reason = _find(ref["kr"], observed)
            if en_status == "MISSING" or kr_status == "MISSING":
                overall = "FAIL"
            elif en_status in ("REVIEW", "OCR_REVIEW") or kr_status in ("REVIEW", "OCR_REVIEW", "NOT_CONFIGURED"):
                overall = "REVIEW"
            else:
                overall = "OK"
            results.append({
                "file": filename,
                "section": ref["section"],
                "english_reference": ref["en"],
                "korean_reference": ref["kr"],
                "english_status": en_status,
                "english_finding": en_reason,
                "korean_status": kr_status,
                "korean_finding": kr_reason,
                "status": overall,
            })
    return results
