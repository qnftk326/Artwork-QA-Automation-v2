# 패키지 아트웍 문구 검수

패키지 아트웍 PDF에서 사전에 등록한 영문(EN)·국문(KR) 문구를 **PDF 내 위치와 관계없이** 찾아 대조하는 Streamlit 앱입니다.

## 주요 기능

- PDF 전체 페이지에서 EN·KR 기준 문구 검색
- PDF 텍스트 레이어를 우선 사용하고, 페이지 OCR 결과를 보조 근거로 활용
- 공백·줄바꿈·대소문자·일부 구두점 차이를 정규화하여 비교
- OCR에서만 발견된 문구는 자동 승인하지 않고 REVIEW 처리
- 기준 문구 누락은 FAIL, 유사 문구는 REVIEW 처리
- 검수 결과 CSV 다운로드

## 실행 방법

1. Python 3.10 이상 설치
2. Tesseract OCR 설치 및 `kor`, `eng` 언어팩 설치
3. 의존성 설치 및 실행

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit Community Cloud에서는 저장소 루트의 `app.py`를 앱 진입점으로 지정합니다. 시스템 패키지는 `packages.txt`, Python 패키지는 `requirements.txt`에서 설치합니다.

## 기준 문구 관리

- `artwork_copy_reference.py`: Section, EN, KR 기준 문구
- `artwork_copy_checker.py`: 위치 무관 EN·KR 비교 로직
- `test_artwork_copy_checker.py`: 검수 로직 단위 테스트

Section은 기준 문구를 분류하고 결과를 표시하기 위한 메타데이터이며, PDF 내 인쇄 위치를 제한하거나 검증하지 않습니다.

국문 기준 셀이 비어 있는 항목은 KR 기준 미등록으로 REVIEW 처리합니다. 임의로 국문 번역을 만들어 검수 정답으로 사용하지 않습니다.

## 판정 기준

| 상태 | 의미 |
|---|---|
| OK | EN·KR 기준 문구가 PDF 텍스트 레이어에서 확인됨 |
| FAIL | EN 또는 등록된 KR 기준 문구를 찾지 못함 |
| REVIEW | OCR에서만 발견, 유사 문구, 또는 KR 기준 미등록 |

공백·줄바꿈·대소문자·일부 구두점 차이는 정규화합니다. 다만 숫자, 단위, 문장 내용의 의미가 동일하다는 보증은 하지 않으므로 최종 인쇄 아트웍과 대조해야 합니다.

## 테스트

```bash
python -m unittest -v test_artwork_copy_checker
python -m py_compile app.py artwork_copy_checker.py artwork_copy_reference.py
```

GitHub Actions는 기존 회귀 테스트와 신규 문구 검수 테스트를 실행합니다.

## 데이터 보안 및 한계

- 실제 회사 아트웍 PDF는 승인된 환경에서만 업로드하세요. 공개 저장소에 원본 PDF를 커밋하지 마세요.
- OCR 결과는 오인식할 수 있으며, OCR만으로 발견된 문구는 REVIEW로 남깁니다.
- 현재 검수는 문구의 존재·문자열 일치 여부 중심입니다. 번역의 의미 적합성, 인쇄 품질, 로고·아이콘·QR의 시각적 존재 여부는 자동 승인하지 않습니다.
- 동일 문구가 PDF 여러 위치에 인쇄된 경우 위치별 중복 여부는 판정하지 않습니다.
