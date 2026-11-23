import io

import fitz
import pandas as pd
import pytesseract
import streamlit as st
from PIL import Image

from artwork_copy_checker import check_artwork

st.set_page_config(page_title="패키지 아트웍 문구 검수", layout="wide")
st.title("패키지 아트웍 문구 검수")
st.caption("등록된 EN–KR 기준 문구를 PDF 전체에서 위치와 관계없이 확인합니다.")

uploads = st.file_uploader("패키지 아트웍 PDF 업로드", type=["pdf"], accept_multiple_files=True)
st.info("PDF 텍스트 레이어를 우선 확인하고, 페이지 OCR 결과도 보조 근거로 활용합니다. OCR에서만 발견된 문구는 자동 승인하지 않고 검토로 표시합니다.")


def extract_observed(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    native_pages, ocr_pages = [], []
    try:
        for page in doc:
            native_pages.append(page.get_text("text") or "")
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            try:
                ocr_pages.append(pytesseract.image_to_string(
                    image, lang="kor+eng", config="--oem 3 --psm 11", timeout=45
                ))
            except Exception:
                ocr_pages.append("")
    finally:
        doc.close()
    return {"native": "\n".join(native_pages), "ocr": "\n".join(ocr_pages)}


if uploads and st.button("검수 시작", type="primary"):
    outputs, errors = {}, []
    progress = st.progress(0)
    for i, uploaded in enumerate(uploads):
        try:
            outputs[uploaded.name] = extract_observed(uploaded.getvalue())
        except Exception as exc:
            errors.append(f"{uploaded.name}: {type(exc).__name__}: {exc}")
        progress.progress((i + 1) / len(uploads))
    for error in errors:
        st.error(error)
    if outputs:
        results = check_artwork(outputs)
        frame = pd.DataFrame(results)
        counts = frame.groupby("status").size().to_dict()
        cols = st.columns(3)
        cols[0].metric("전체 기준 항목", len(frame))
        cols[1].metric("확인 완료", counts.get("OK", 0))
        cols[2].metric("누락·검토 필요", counts.get("FAIL", 0) + counts.get("REVIEW", 0))
        st.subheader("문구별 검수 결과")
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.download_button(
            "검수 결과 CSV 다운로드",
            frame.to_csv(index=False).encode("utf-8-sig"),
            "artwork_copy_qa.csv",
            "text/csv",
        )
        st.caption("Section은 기준 데이터 관리용이며 PDF 내 실제 위치는 검수 조건에 사용하지 않습니다. 국문 기준이 비어 있는 항목은 기준 미등록으로 REVIEW 처리합니다.")
