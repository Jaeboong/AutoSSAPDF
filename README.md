# AutoSSAPDF

SSAFY 온라인 교재(e-book)를 자동으로 캡처하여 PDF로 저장하는 Python 스크립트입니다.
`books.json`에 여러 교재를 등록해두면 한 번의 실행으로 순차적으로 모두 PDF로 만들어 줍니다.

## 목차

- [시작하기](#시작하기)
  - [사전 요구 사항](#사전-요구-사항)
- [설치](#설치)
- [환경설정](#환경설정)
- [교재 목록 설정 (books.json)](#교재-목록-설정-booksjson)
- [실행](#실행)
- [교재 링크 자동 수집 (FetchBooks.py)](#교재-링크-자동-수집-fetchbookspy)
- [결과물](#결과물)

## 시작하기

프로젝트를 로컬에서 실행하기 위한 안내입니다.

### 사전 요구 사항

*   Python 3.8 이상
*   pip
*   Google Chrome (Selenium Manager가 드라이버를 자동 관리하므로 ChromeDriver는 별도 설치 불필요)

## 설치

1.  **저장소 복제**
    ```sh
    git clone https://github.com/Jaeboong/AutoSSAPDF.git
    cd AutoSSAPDF
    ```

2.  **가상 환경 생성 및 활성화**

    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **필요 패키지 설치**

    ```sh
    pip install -r requirements.txt
    ```

## 환경설정

프로젝트 루트에 `.env` 파일을 생성하고 로그인 정보와 임시 이미지 폴더를 설정합니다.
(`.env-sample` 참고)

```env
IMAGE_FILE_DIR=./image                                       # 임시 캡처 이미지 저장 폴더
USER_ID=개인 ID                                              # SSAFY 계정 ID
USER_PW=개인 PW                                              # SSAFY 계정 PW
LOGIN_URL=https://edu.ssafy.com/comm/login/SecurityLoginForm.do
```

> 캡처할 교재 URL은 더 이상 `.env`가 아니라 `books.json`에서 관리합니다.

## 교재 목록 설정 (books.json)

PDF로 만들고 싶은 교재들을 `{ "name", "url" }` 배열로 작성합니다.
`name`은 생성되는 PDF 파일명이 되고, `url`은 교재 e-book 주소입니다.

```json
[
  {
    "name": "알고리즘",
    "url": "https://edu.ssafy.com/.../ebook/unzip/AXXXXXXXX/index.html"
  },
  {
    "name": "자료구조",
    "url": "https://edu.ssafy.com/.../ebook/unzip/AYYYYYYYY/index.html"
  }
]
```

*   파일명으로 쓸 수 없는 문자(`\ / : * ? " < > |`)는 자동으로 `_`로 치환됩니다.
*   URL을 일일이 찾기 번거롭다면 아래 [FetchBooks.py](#교재-링크-자동-수집-fetchbookspy)로 자동 수집할 수 있습니다.

## 실행

```sh
python Main.py
```

로그인은 한 번만 수행하고, `books.json`의 교재를 위에서부터 순차적으로 캡처해 PDF로 저장합니다.
한 교재에서 오류가 나도 다음 교재 처리는 계속되며, 마지막에 `성공 N권 / 실패 M권`이 출력됩니다.
결과 폴더(`outputs/`)는 코드가 자동으로 생성합니다.

## 교재 링크 자동 수집 (FetchBooks.py)

`강의실 > 주차별 커리큘럼`에서 특정 학기/주차 이후의 교재 e-book 링크를 모두 수집해
JSON 파일로 저장하는 보조 스크립트입니다.

```sh
python FetchBooks.py
```

스크립트 상단의 설정값으로 동작을 조정할 수 있습니다.

```python
SEMESTER = "1학기"                  # 수집 대상 학기 (탭에 표시되는 텍스트)
START_WEEK = 3                       # 이 주차부터 끝까지 수집
OUTPUT_FILE = "books_fetched.json"   # 결과 저장 파일
```

*   로그인 후 대상 학기를 선택하고, 주차별 자료에서 e-book URL과 교재명을 추출합니다.
*   결과는 `books.json`을 덮어쓰지 않도록 별도 파일(`books_fetched.json`)에 저장됩니다.
    수집된 내용을 확인한 뒤 원하는 교재를 `books.json`으로 옮겨 사용하세요.

## 결과물

생성된 PDF는 `outputs/` 디렉터리에 `<교재명>.pdf` 형태로 저장됩니다.
PDF 생성이 끝나면 임시 캡처 이미지는 자동으로 삭제됩니다.
