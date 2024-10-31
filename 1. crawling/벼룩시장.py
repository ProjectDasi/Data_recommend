import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# 크롬 드라이버 설정
driver_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=driver_options)

# 데이터 저장용 리스트 초기화 함수
def initialize_lists():
    return [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []  # 조회수 리스트 추가

출처_list, 기업명_list, 제목_list, 급여_list, 등록일_list, 마감일_list, 근무지역_list, 경력_list, 학력_list, 근무직종_list, 링크_list, 근무시간_list, 연락처_list, 근무유형_list, details_list, 조회수_list = initialize_lists()

# 페이지 수 설정
current_page = 1
pages = 10  # 크롤링할 총 페이지 수
save_interval = 10  # 몇 페이지마다 저장할지 설정

# 저장 경로 설정
save_dir = "./1. crawling/crawling_data_merged"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def save_data(file_count):
    df = pd.DataFrame({
        '출처': 출처_list,
        '기업명': 기업명_list,
        '제목': 제목_list,
        '급여': 급여_list,
        '등록일': 등록일_list,
        '마감일': 마감일_list,
        '근무지역': 근무지역_list,
        '경력': 경력_list,
        '학력': 학력_list,
        '근무직종': 근무직종_list,
        '링크': 링크_list,
        '근무시간': 근무시간_list,
        '연락처': 연락처_list,
        '근무유형': 근무유형_list,
        '세부내용': details_list,
        '조회수': 조회수_list  # 조회수 열 추가
    })
    save_path = os.path.join(save_dir, f"벼룩시장_최종{file_count}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {save_path}")

# 크롤링 실행
file_count = 1  # 저장된 파일 번호를 추적

while current_page <= pages:
    url = f"http://www.findjob.co.kr/job/category/specialistDetailJob.asp?Page={current_page}&SpID=1015&TotalCount=26&sltAreaA=14"
    driver.get(url)
    time.sleep(5)  # 페이지 로딩 시간을 5초로 늘림
    
    # 공고 리스트 추출
    links = driver.find_elements(By.CSS_SELECTOR, 'td.sbj a.name')
    num_links = len(links)
    
    i = 0
    while i < num_links:
        try:
            links = driver.find_elements(By.CSS_SELECTOR, 'td.sbj a.name')  # 링크를 반복문 내에서 다시 찾음
            num_links = len(links)  # 반복문 내에서 링크 수를 다시 계산
            
            if i >= num_links:
                print(f"Skipping index {i} as it exceeds the length of available links.")
                break
            
            link = links[i]
            link_url = link.get_attribute('href')
            if not link_url.startswith("http"):
                link_url = "http://www.findjob.co.kr" + link_url

            driver.get(link_url)
            time.sleep(5)  # 페이지 로딩 시간을 더 길게 설정
            
            # Explicit wait for the element to be visible
            wait = WebDriverWait(driver, 15)
            
            # 기업명과 제목 추출
            기업명 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.prod_name span.name"))).text
            제목 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.prod_title"))).text
            
            # 급여 처리
            try:
                급여 = driver.find_element(By.CSS_SELECTOR, "span#pay_num").text
            except NoSuchElementException:
                급여 = "정보 없음"
            
            # 등록일 추출
            try:
                등록일 = driver.find_element(By.CSS_SELECTOR, "div.fix_date span.date").text
            except NoSuchElementException:
                등록일 = "정보 없음"

            # 마감일 추출
            try:
                마감일 = driver.find_element(By.CSS_SELECTOR, "span.d_day").text.strip()
            except NoSuchElementException:
                마감일 = "정보 없음"
            
            # 근무지역 추출
            try:
                근무지역 = driver.find_element(By.CSS_SELECTOR, "span#work_place").text.strip()
            except NoSuchElementException:
                근무지역 = "정보 없음"
            
            # 근무유형, 근무요일, 근무시간 추출
            try:
                근무유형 = driver.find_element(By.XPATH, "//li[span[contains(text(), '근무유형')]]/span[@class='info btn_plus']").text.strip()
            except NoSuchElementException:
                근무유형 = "정보 없음"
                
            try:
                근무시간 = driver.find_element(By.XPATH, "//li[span[contains(text(), '근무시간')]]/span[@class='info btn_plus']").text.strip()
            except NoSuchElementException:
                근무시간 = "정보 없음"
            
            # 근무직종, 담당업무, 경력, 학력, 우대/가능, 복리후생
            try:
                근무직종 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '근무직종')]]/span[@class='info plus btn_plus']").text.strip()
            except NoSuchElementException:
                근무직종 = "정보 없음"
                
            try:
                경력 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '경력')]]/span[@class='info']").text.strip()
            except NoSuchElementException:
                경력 = "정보 없음"
                
            try:
                학력 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '학력')]]/span[@class='info btn_plus']").text.strip()
            except NoSuchElementException:
                학력 = "정보 없음"
            
            # 연락처 추출 (담당자 전화번호 우선, 없으면 대표전화)
            try:
                담당자전화 = driver.find_element(By.XPATH, "//li[span[text()='담당자 전화']]/span[@class='con num']").text.strip()
            except NoSuchElementException:
                담당자전화 = "정보 없음"
            
            try:
                대표전화 = driver.find_element(By.XPATH, "//li[span[text()='대표전화']]/span[@class='con num']").text.strip()
            except NoSuchElementException:
                대표전화 = "정보 없음"

            # 연락처 우선순위 처리
            연락처 = 담당자전화 if 담당자전화 != "정보 없음" else 대표전화
            
            # details 내용 추출
            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "DetailFrame")))  # `DetailFrame` 아이디로 `<iframe>` 찾기
                
                # 이제 `section` ID로 전체 HTML 가져오기
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "section")))
                details = driver.find_element(By.ID, "section").get_attribute("outerHTML")
            except NoSuchElementException:
                details = "정보 없음"
            finally:
                driver.switch_to.default_content()  # iframe에서 벗어나기
            
            # 조회수는 현재 구현된 정보가 없으므로 기본값 0 설정
            조회수 = 0
            
            # 리스트에 데이터 추가
            출처_list.append("국민 일자리 벼룩시장")
            기업명_list.append(기업명)
            제목_list.append(제목)
            급여_list.append(급여)
            등록일_list.append(등록일)
            마감일_list.append(마감일)
            근무지역_list.append(근무지역)
            경력_list.append(경력)
            학력_list.append(학력)
            근무직종_list.append(근무직종)
            링크_list.append(link_url)
            근무시간_list.append(근무시간)
            연락처_list.append(연락처)
            근무유형_list.append(근무유형)
            details_list.append(details)
            조회수_list.append(조회수)  # 조회수 기본값 추가
            
            i += 1
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Element not found or timeout. URL: {link_url}, Error: {e}")
            i += 1
            continue
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
            continue
        except Exception as e:
            print(f"Error: {e}")
            i += 1
            continue
        
        driver.back()
        time.sleep(5)  # 페이지 로드 대기 시간을 더 길게 설정
    
    if current_page % save_interval == 0 or current_page == pages:
        save_data(file_count)
        file_count += 1
        출처_list, 기업명_list, 제목_list, 급여_list, 등록일_list, 마감일_list, 근무지역_list, 경력_list, 학력_list, 근무직종_list, 링크_list, 근무시간_list, 연락처_list, 근무유형_list, details_list, 조회수_list = initialize_lists()
    
    current_page += 1

# 드라이버 종료
driver.quit()

# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트 초기화 함수
# def initialize_lists():
#     return [], [], [], [], [], [], [], [], [], [], [], [], [], [], []  # 마감일 리스트와 details 리스트 추가

# 출처_list, 기업명_list, 제목_list, 급여_list, 등록일_list, 마감일_list, 근무지역_list, 경력_list, 학력_list, 근무직종_list, 링크_list, 근무시간_list, 연락처_list, 근무유형_list, details_list = initialize_lists()

# # 페이지 수 설정
# current_page = 1
# pages = 27  # 크롤링할 총 페이지 수
# save_interval = 27  # 몇 페이지마다 저장할지 설정

# # 저장 경로 설정
# save_dir = "./1.crawling/crawling_data_merged"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def save_data(file_count):
#     df = pd.DataFrame({
#         '출처': 출처_list,
#         '기업명': 기업명_list,
#         '제목': 제목_list,
#         '급여': 급여_list,
#         '등록일': 등록일_list,
#         '마감일': 마감일_list,
#         '근무지역': 근무지역_list,
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '근무직종': 근무직종_list,
#         '링크': 링크_list,
#         '근무시간': 근무시간_list,
#         '연락처': 연락처_list,
#         '근무유형': 근무유형_list,
#         '세부내용': details_list  # details 열 추가
#     })
#     save_path = os.path.join(save_dir, f"벼룩시장_최종{file_count}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"Data saved to {save_path}")

# # 크롤링 실행
# file_count = 1  # 저장된 파일 번호를 추적

# while current_page <= pages:
#     url = f"http://www.findjob.co.kr/job/category/specialistDetailJob.asp?Page={current_page}&SpID=1015&TotalCount=26&sltAreaA=14"
#     driver.get(url)
#     time.sleep(5)  # 페이지 로딩 시간을 5초로 늘림
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'td.sbj a.name')
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             links = driver.find_elements(By.CSS_SELECTOR, 'td.sbj a.name')  # 링크를 반복문 내에서 다시 찾음
#             num_links = len(links)  # 반복문 내에서 링크 수를 다시 계산
            
#             if i >= num_links:
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             if not link_url.startswith("http"):
#                 link_url = "http://www.findjob.co.kr" + link_url

#             driver.get(link_url)
#             time.sleep(5)  # 페이지 로딩 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)
            
#             # 기업명과 제목 추출
#             기업명 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.prod_name span.name"))).text
#             제목 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.prod_title"))).text
            
#             # 급여 처리
#             try:
#                 급여 = driver.find_element(By.CSS_SELECTOR, "span#pay_num").text
#             except NoSuchElementException:
#                 급여 = "정보 없음"
            
#             # 등록일 추출
#             try:
#                 등록일 = driver.find_element(By.CSS_SELECTOR, "div.fix_date span.date").text
#             except NoSuchElementException:
#                 등록일 = "정보 없음"

#             # 마감일 추출
#             try:
#                 마감일 = driver.find_element(By.CSS_SELECTOR, "span.d_day").text.strip()
#             except NoSuchElementException:
#                 마감일 = "정보 없음"
            
#             # 근무지역 추출
#             try:
#                 근무지역 = driver.find_element(By.CSS_SELECTOR, "span#work_place").text.strip()
#             except NoSuchElementException:
#                 근무지역 = "정보 없음"
            
#             # 근무유형, 근무요일, 근무시간 추출
#             try:
#                 근무유형 = driver.find_element(By.XPATH, "//li[span[contains(text(), '근무유형')]]/span[@class='info btn_plus']").text.strip()
#             except NoSuchElementException:
#                 근무유형 = "정보 없음"
                
#             try:
#                 근무시간 = driver.find_element(By.XPATH, "//li[span[contains(text(), '근무시간')]]/span[@class='info btn_plus']").text.strip()
#             except NoSuchElementException:
#                 근무시간 = "정보 없음"
            
#             # 근무직종, 담당업무, 경력, 학력, 우대/가능, 복리후생
#             try:
#                 근무직종 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '근무직종')]]/span[@class='info plus btn_plus']").text.strip()
#             except NoSuchElementException:
#                 근무직종 = "정보 없음"
                
#             try:
#                 경력 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '경력')]]/span[@class='info']").text.strip()
#             except NoSuchElementException:
#                 경력 = "정보 없음"
                
#             try:
#                 학력 = driver.find_element(By.XPATH, ".//li[span[contains(text(), '학력')]]/span[@class='info btn_plus']").text.strip()
#             except NoSuchElementException:
#                 학력 = "정보 없음"
            
#             # 연락처 추출 (담당자 전화번호 우선, 없으면 대표전화)
#             try:
#                 담당자전화 = driver.find_element(By.XPATH, "//li[span[text()='담당자 전화']]/span[@class='con num']").text.strip()
#             except NoSuchElementException:
#                 담당자전화 = "정보 없음"
            
#             try:
#                 대표전화 = driver.find_element(By.XPATH, "//li[span[text()='대표전화']]/span[@class='con num']").text.strip()
#             except NoSuchElementException:
#                 대표전화 = "정보 없음"

#             # 연락처 우선순위 처리
#             연락처 = 담당자전화 if 담당자전화 != "정보 없음" else 대표전화
            
#             # details 내용 추출
#             try:
#                 details = driver.find_element(By.CSS_SELECTOR, "div.apply_view").get_attribute('innerHTML').strip()
#             except NoSuchElementException:
#                 details = "정보 없음"
            
#             # 리스트에 데이터 추가
#             출처_list.append("국민 일자리 벼룩시장")
#             기업명_list.append(기업명)
#             제목_list.append(제목)
#             급여_list.append(급여)
#             등록일_list.append(등록일)
#             마감일_list.append(마감일)
#             근무지역_list.append(근무지역)
#             경력_list.append(경력)
#             학력_list.append(학력)
#             근무직종_list.append(근무직종)
#             링크_list.append(link_url)
#             근무시간_list.append(근무시간)
#             연락처_list.append(연락처)
#             근무유형_list.append(근무유형)
#             details_list.append(details)
            
#             i += 1
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. URL: {link_url}, Error: {e}")
#             i += 1
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1
#             continue
        
#         driver.back()
#         time.sleep(5)  # 페이지 로드 대기 시간을 더 길게 설정
    
#     if current_page % save_interval == 0 or current_page == pages:
#         save_data(file_count)
#         file_count += 1
#         출처_list, 기업명_list, 제목_list, 급여_list, 등록일_list, 마감일_list, 근무지역_list, 경력_list, 학력_list, 근무직종_list, 링크_list, 근무시간_list, 연락처_list, 근무유형_list, details_list = initialize_lists()
    
#     current_page += 1

# # 드라이버 종료
# driver.quit()

