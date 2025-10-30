# AutoSSAPDF


이 프로젝트는 자동 캡처를 수행하는 Python 스크립트입니다.

## 목차

- [시작하기](#시작하기)
  - [사전 요구 사항](#사전-요구-사항)
- [설치](#설치)
- [환경설정](#환경설정)
- [실행](#실행)
- [결과물](#결과물)

## 시작하기

프로젝트를 로컬에서 실행하기 위한 안내입니다.

### 사전 요구 사항

*   Python 3.8 이상
*   pip

## 설치

1.  **저장소 복제**
    ```sh
    git clone https://github.com/smj1513/AutoSSAPDF.git
    cd AutoCaputre
    ```

2.  **가상 환경 생성 및 활성화**
    *   가상 환경을 생성하여 프로젝트의 의존성을 시스템의 다른 패키지와 격리합니다.

    ```sh
    python -m venv .venv
    ```

    *   생성된 가상 환경을 활성화합니다. (Windows 기준)

    ```sh
    .venv\Scripts\activate
    ```

3.  **필요 패키지 설치**
    *   `requirements.txt` 파일을 사용하여 필요한 모든 패키지를 설치합니다.

    ```sh
    pip install -r requirements.txt
    ```

## 환경설정

프로젝트 실행에 필요한 환경 변수를 설정해야 합니다.

1.  프로젝트 루트 디렉토리(`.gitignore` 파일이 있는 위치)에 `.env` 파일을 생성하세요.

2.  아래 내용을 `.env` 파일에 복사하고, 각 변수에 맞는 값을 입력하세요.
   
    ```env
    # .env 파일 예시
    # 필요한 환경 변수를 여기에 추가하세요.
    # 예: 로그인 정보, 로그인 페이지 URL, 캡쳐할 페이지 URL, 캡쳐한 이미지를 임시 저장할 폴더

    IMAGE_FILE_DIR= 임시 캡쳐 이미지가 저장될 디렉터리
    USER_ID=개인 ID
    USER_PW=개인 PW
    LOGIN_URL=SSAFY 로그인 URL
    PAGE_URL=PDF로 만들고 싶은 교재 URL
    ```
3. 프로젝트 루트 디렉토리에 outputs 디렉토리를 생성하세요. (필수)

## 실행

모든 설정이 완료되면 `Main.py` 스크립트를 실행하여 프로그램을 시작합니다.

```sh
python Main.py
```

## 결과물

스크립트 실행 후 생성되는 결과물은 `outputs/` 디렉토리에 저장됩니다.
