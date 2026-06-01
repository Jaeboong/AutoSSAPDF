from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import re
import time
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# 캡처 저장 폴더 지정 (임시 이미지)
image_files_dir = os.getenv("IMAGE_FILE_DIR")
os.makedirs(image_files_dir, exist_ok=True)

# 최종 PDF 저장 폴더
output_dir = "./outputs"
os.makedirs(output_dir, exist_ok=True)

# 처리할 교재 목록 로드 (books.json)
with open("books.json", "r", encoding="utf-8") as f:
    books = json.load(f)


def sanitize_filename(name):
    """파일명으로 쓸 수 없는 문자 제거 (Windows 기준)"""
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip() or "교재"


def capture_book(driver, book, index):
    """교재 한 권을 캡처해서 PDF로 저장. 성공 여부 반환."""
    name = book.get("name") or f"교재_{index + 1}"
    url = book["url"]
    print(f"\n===== [{index + 1}/{len(books)}] '{name}' 처리 시작 =====")

    driver.get(url)
    time.sleep(5)  # 페이지 로딩 대기

    num_pages = int(driver.find_element(By.CLASS_NAME, "label-page").text.split("/")[1].strip())
    print(f"전체 페이지 수: {num_pages}")

    captured = []
    for i in range(num_pages):
        try:
            element_to_capture = driver.find_element(By.CLASS_NAME, "book")
            shot_path = os.path.join(image_files_dir, f"page_{i + 1}.png")
            element_to_capture.screenshot(shot_path)
            captured.append(shot_path)
            print(f"{i + 1}페이지 캡처 저장: {shot_path}")
        except Exception as e:
            print(f"캡처 요소(.book)를 찾는 데 실패했습니다: {e}")
            break

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".btn-side-next-page")
            next_btn.click()
            time.sleep(2)
        except Exception as e:
            if i < num_pages - 1:  # 마지막 페이지가 아닌데 버튼을 못 찾으면 에러 출력
                print("다음 페이지 버튼 탐색 실패:", e)
            break

    if not captured:
        print(f"❌ '{name}': 캡처된 이미지가 없어 PDF를 건너뜁니다.")
        return False

    # 페이지 순서대로 정렬 후 PDF 생성
    captured.sort(key=lambda f: int(os.path.splitext(os.path.basename(f))[0].split("_")[1]))
    images = [Image.open(f).convert("RGB") for f in captured]

    pdf_filename = os.path.join(output_dir, f"{sanitize_filename(name)}.pdf")
    images[0].save(pdf_filename, save_all=True, append_images=images[1:])
    for img in images:
        img.close()
    print(f"✅ '{name}': 총 {len(images)}개 이미지를 PDF로 저장했습니다: {pdf_filename}")

    # 임시 캡처 이미지 삭제 (다음 교재와 섞이지 않도록)
    for file_path in captured:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"❌ 파일 삭제 중 오류: {e}")

    return True


# Chrome 드라이버 세팅
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # 로그인 (한 번만)
    login_url = os.getenv("LOGIN_URL")
    user_id = os.getenv("USER_ID")
    user_pw = os.getenv("USER_PW")

    driver.get(login_url)
    time.sleep(2)  # 로딩 대기

    driver.find_element(By.ID, "userId").send_keys(user_id)
    driver.find_element(By.ID, "userPwd").send_keys(user_pw)
    driver.find_element(By.CLASS_NAME, "btn-lg").click()
    time.sleep(4)  # 로그인 대기

    # 교재 목록 순차 처리 (한 권이 실패해도 다음 권 계속)
    success, fail = 0, 0
    for index, book in enumerate(books):
        try:
            if capture_book(driver, book, index):
                success += 1
            else:
                fail += 1
        except Exception as e:
            fail += 1
            print(f"❌ '{book.get('name', index + 1)}' 처리 중 오류: {e}")

    print(f"\n===== 전체 완료: 성공 {success}권 / 실패 {fail}권 =====")
finally:
    driver.quit()
