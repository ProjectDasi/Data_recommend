import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
import time
import pandas as pd

# 크롬 드라이버 설정
driver_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=driver_options)

# 데이터 저장용 리스트
강좌명_list = []
학습기관_list = []
학습기간_list = []
접수기간_list = []
강사명_list = []
수강료_list = []
교육방법_list = []
교육대상_list = []
교육주기_list = []
교육정원_list = []
교육장소_list = []
교육문의전화_list = []
접수방법_list = []
직업능력개발_훈련비지원_list = []
교육공고_링크_list = []
조회수_list = []  # 조회수 리스트 추가

# 저장 경로 설정
save_dir = "./1.1 crawling_education/data"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def get_non_duplicate_filename(base_dir, base_filename):
    filename, extension = os.path.splitext(base_filename)
    counter = 1
    new_filename = base_filename
    while os.path.exists(os.path.join(base_dir, new_filename)):
        new_filename = f"{filename}_{counter}{extension}"
        counter += 1
    return os.path.join(base_dir, new_filename)

def make_df(num):
    max_length = max(
        len(강좌명_list),
        len(학습기관_list),
        len(학습기간_list),
        len(접수기간_list),
        len(강사명_list),
        len(수강료_list),
        len(교육방법_list),
        len(교육대상_list),
        len(교육주기_list),
        len(교육정원_list),
        len(교육장소_list),
        len(교육문의전화_list),
        len(접수방법_list),
        len(직업능력개발_훈련비지원_list),
        len(교육공고_링크_list),
        len(조회수_list)  # 조회수 리스트 추가
    )

    # 리스트의 길이를 max_length에 맞추기
    def pad_list(lst):
        return lst + [''] * (max_length - len(lst))

    df = pd.DataFrame({
        '강좌명': pad_list(강좌명_list),
        '학습기관': pad_list(학습기관_list),
        '학습기간': pad_list(학습기간_list),
        '접수기간': pad_list(접수기간_list),
        '강사명': pad_list(강사명_list),
        '수강료': pad_list(수강료_list),
        '교육방법': pad_list(교육방법_list),
        '교육대상': pad_list(교육대상_list),
        '교육주기': pad_list(교육주기_list),
        '교육정원': pad_list(교육정원_list),
        '교육장소': pad_list(교육장소_list),
        '교육문의전화': pad_list(교육문의전화_list),
        '접수방법': pad_list(접수방법_list),
        '직업능력개발_훈련비지원': pad_list(직업능력개발_훈련비지원_list),
        '교육공고_링크': pad_list(교육공고_링크_list),
        '조회수': pad_list(조회수_list)  # 조회수 열 추가
    })
    
    save_path = get_non_duplicate_filename(save_dir, f"부산평생교육정보망_{num}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')

# 초기 페이지 설정
url = "https://www.ble.or.kr/Home/Lecture/LECList.mbz?action=MAPP_0000000156"
driver.get(url)
time.sleep(5)

# 'organ_name' 필드에 접근하여 값 입력
input_field = driver.find_element(By.ID, 'organ_name')
input_field.clear()
input_field.send_keys("평생학습관")

# '검색' 버튼 클릭
search_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"].submit1')
search_button.click()

# 페이지가 새로 로드될 때까지 잠시 대기
time.sleep(5)

# 첫 번째 페이지에 있는 강좌 리스트 처리
for page in range(1, 50):  # 페이지 번호를 1부터 시작, 2페이지까지 탐색
    if page > 1:
        try:
            page_button = driver.find_element(By.XPATH, f"//a[contains(@onclick,'postPage({page})')]")
            page_button.click()
            time.sleep(10)  # 페이지 로드 대기
        except NoSuchElementException:
            print(f"Page {page} not found or could not be loaded.")
            continue

    links = driver.find_elements(By.XPATH, '//strong[@class="title"]/a')
    num_links = len(links)

    for i in range(num_links):
        try:
            links = driver.find_elements(By.XPATH, '//strong[@class="title"]/a')
            links[i].click()
            time.sleep(5)

            wait = WebDriverWait(driver, 5)

            강좌명 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '강좌명')]/following-sibling::td"))).text
            강좌명_list.append(강좌명)

            학습기관 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '학습기관')]/following-sibling::td"))).text
            학습기관_list.append(학습기관)

            학습기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '학습기간')]/following-sibling::td"))).text
            학습기간_list.append(학습기간)

            접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '접수기간')]/following-sibling::td"))).text
            접수기간_list.append(접수기간)

            강사명 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '강사명')]/following-sibling::td"))).text
            강사명_list.append(강사명)

            수강료 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '수강료')]/following-sibling::td"))).text
            수강료_list.append(수강료)

            교육방법 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육방법')]/following-sibling::td"))).text
            교육방법_list.append(교육방법)

            교육대상 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육대상')]/following-sibling::td"))).text
            교육대상_list.append(교육대상)

            교육주기 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육주기')]/following-sibling::td"))).text
            교육주기_list.append(교육주기)

            교육정원 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육정원')]/following-sibling::td"))).text
            교육정원_list.append(교육정원)

            교육장소 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육장소')]/following-sibling::td"))).text
            교육장소_list.append(교육장소)

            교육문의전화 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '교육문의전화')]/following-sibling::td"))).text
            교육문의전화_list.append(교육문의전화)

            접수방법_elements = driver.find_elements(By.XPATH, "//th[contains(text(), '접수방법')]/following-sibling::td/a/img")
            접수방법 = ", ".join([element.get_attribute('alt').strip() for element in 접수방법_elements])
            접수방법_list.append(접수방법)

            직업능력개발_훈련비지원 = wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(), '직업능력개발')]/following-sibling::td"))).text
            직업능력개발_훈련비지원_list.append(직업능력개발_훈련비지원)

            조회수_list.append(0)  # 조회수 기본값을 0으로 설정

            교육공고_링크_elements = driver.find_elements(By.XPATH, "//th[contains(text(), 'URL')]/following-sibling::td/a")
            교육공고_링크 = " ".join([element.get_attribute('href').strip() for element in 교육공고_링크_elements])
            교육공고_링크_list.append(교육공고_링크 if 교육공고_링크 else "")

            driver.back()
            time.sleep(5)

        except NoSuchWindowException:
            print("Error: Target window is already closed. Ending script.")
            break

        except (TimeoutException, Exception) as e:
            print(f"Error: {e}")
            driver.back()
            time.sleep(3)

# 최종 저장
make_df('final')

# 드라이버 종료
driver.quit()
