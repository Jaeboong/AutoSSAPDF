"""
강의실 > 주차별 커리큘럼에서 특정 학기/주차 이후의 교재(ebook) 링크를 모두 수집해
JSON 파일로 저장하는 스크립트.

동작:
  1. Selenium으로 로그인 (Main.py와 동일한 방식)
  2. 주차별 커리큘럼 페이지로 이동 후 대상 학기 선택
  3. 브라우저 컨텍스트에서 내부 API(crclmDayList.do, mainMatlPopup.do)를 호출해
     주차별 교재 자료 -> ebook URL/이름 추출
  4. {name, url} 배열을 OUTPUT_FILE 에 저장
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ===== 설정 =====
SEMESTER = "1학기"   # 수집 대상 학기 (탭에 표시되는 텍스트)
START_WEEK = 3        # 이 주차부터 끝까지 수집
OUTPUT_FILE = "books_fetched.json"   # 결과 저장 파일 (books.json 을 덮지 않음)

CURRICULUM_URL = "https://edu.ssafy.com/edu/lectureroom/curriculumn/curriculumnWeeklyList.do"

# 브라우저 안에서 실행될 수집 스크립트 (async)
FETCH_SCRIPT = r"""
const done = arguments[arguments.length - 1];
const termId = arguments[0];
const startWeek = arguments[1];

(async () => {
  try {
    const token = document.querySelector('meta[name="_csrf"]').content;
    const sleep = ms => new Promise(r => setTimeout(r, ms));

    // 1) 대상 학기의 주차(>= startWeek) 날짜 수집
    const units = [...document.querySelectorAll('div.unit')].map(u => ({
      week: parseInt((u.querySelector('[data-week]') || {}).dataset?.week || '0'),
      st: u.dataset.stweeks,
      ed: u.dataset.edweeks
    })).filter(w => w.week >= startWeek).sort((a, b) => a.week - b.week);

    // 2) 주차별 교재 자료ID 수집 (순서 보존, 중복 제거)
    const matIds = [];
    const seenMat = new Set();
    for (const w of units) {
      const p = new URLSearchParams({ searchTermId: termId, sttDt: w.st, edDt: w.ed, _csrf: token });
      const res = await fetch('/edu/main/crclmDayList.do', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: p.toString()
      });
      const text = await res.text();
      for (const m of text.matchAll(/fnMatlPopup\('([^']+)'\)/g)) {
        if (!seenMat.has(m[1])) { seenMat.add(m[1]); matIds.push(m[1]); }
      }
      await sleep(100);
    }

    // 3) 자료 팝업에서 ebook(atchId, 이름) 추출
    const parser = new DOMParser();
    async function fetchOne(id) {
      const body = new URLSearchParams({ clssAcctoTmtbSeq: id, _csrf: token });
      const res = await fetch('/edu/lectureroom/openlearning/mainMatlPopup.do', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
      });
      const doc = parser.parseFromString(await res.text(), 'text/html');
      const ebooks = [];
      doc.querySelectorAll('a[onclick*="fnEbook"], a[onClick*="fnEbook"]').forEach(a => {
        const oc = a.getAttribute('onclick') || a.getAttribute('onClick') || '';
        const m = oc.match(/fnEbook\('([^']+)'\)/);
        if (m) ebooks.push({
          atchId: m[1],
          name: (a.querySelector('.file-name')?.textContent || a.textContent || '').trim()
        });
      });
      return ebooks;
    }

    // 6개씩 병렬, url 기준 중복 제거
    const seenUrl = new Set();
    const books = [];
    const PREFIX = 'https://edu.ssafy.com/data/upload_files/crossUpload/openLrn/ebook/unzip/';
    for (let i = 0; i < matIds.length; i += 6) {
      const chunk = await Promise.all(matIds.slice(i, i + 6).map(fetchOne));
      for (const ebooks of chunk) for (const e of ebooks) {
        const url = PREFIX + e.atchId + '/index.html';
        if (!seenUrl.has(url)) { seenUrl.add(url); books.push({ name: e.name, url }); }
      }
    }

    done({ ok: true, weeks: units.length, materials: matIds.length, books });
  } catch (e) {
    done({ ok: false, error: e.message });
  }
})();
"""


def login(driver):
    """Main.py 와 동일한 Selenium 로그인."""
    driver.get(os.getenv("LOGIN_URL"))
    time.sleep(2)
    driver.find_element(By.ID, "userId").send_keys(os.getenv("USER_ID"))
    driver.find_element(By.ID, "userPwd").send_keys(os.getenv("USER_PW"))
    driver.find_element(By.CLASS_NAME, "btn-lg").click()
    time.sleep(4)


def select_semester(driver, semester):
    """학기 탭을 클릭하고 termId(rel 값)를 반환. 주차 목록이 갱신될 때까지 대기."""
    term_id = driver.execute_script(
        """
        const semester = arguments[0];
        const link = [...document.querySelectorAll('a[rel]')]
          .find(a => /^P\\d+/.test(a.getAttribute('rel')) && a.textContent.includes(semester));
        if (!link) return null;
        link.click();
        return link.getAttribute('rel');
        """,
        semester,
    )
    if not term_id:
        raise RuntimeError(f"'{semester}' 학기 탭을 찾지 못했습니다.")
    time.sleep(3)  # 주차 목록 AJAX 갱신 대기
    return term_id


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.set_script_timeout(600)  # 수집 fetch 가 30초 기본 제한을 넘기므로 늘림

    try:
        login(driver)
        driver.get(CURRICULUM_URL)
        time.sleep(3)

        term_id = select_semester(driver, SEMESTER)
        print(f"학기 '{SEMESTER}' 선택 (termId={term_id}), {START_WEEK}주차부터 수집합니다...")

        result = driver.execute_async_script(FETCH_SCRIPT, term_id, START_WEEK)

        if not result or not result.get("ok"):
            raise RuntimeError(f"수집 실패: {result.get('error') if result else 'no result'}")

        books = result["books"]
        print(f"주차 {result['weeks']}개 / 자료 {result['materials']}개 -> 교재 {len(books)}권 수집")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"[OK] 저장 완료: {OUTPUT_FILE} ({len(books)}권)")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
