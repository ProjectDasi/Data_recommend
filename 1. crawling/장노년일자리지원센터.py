import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup

# 크롬 드라이버 설정
driver_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=driver_options)

# 데이터 저장용 리스트 초기화 함수
def initialize_lists():
    return [], [], [], [], [], [], [], [], [], []

출처_list, 기업명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 제목_list, 링크_list, 연락처_list, 조회수_list = initialize_lists()

# 페이지 수 설정
current_page = 1
pages = 16  # 총 페이지 수
save_interval = 16  # 몇 페이지마다 저장할지 설정

# 저장 경로 설정
save_dir = "./1. crawling/crawling_data_merged"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def make_df(file_count):
    # 접수기간을 등록일과 마감일로 분리
    등록일_list = [기간.split('~')[0].strip() for 기간 in 접수기간_list]
    마감일_list = [기간.split('~')[1].strip() for 기간 in 접수기간_list]
    
    df = pd.DataFrame({
        '출처': 출처_list,
        '기업명': 기업명_list,
        '제목': 제목_list,
        '등록일': 등록일_list,
        '마감일': 마감일_list,
        '근무형태': 근무형태_list,
        '링크': 링크_list,
        '연락처': 연락처_list,
        '세부내용': 세부내용_list,
        '조회수': 조회수_list  # 조회수 열 추가
    })
    
    save_path = os.path.join(save_dir, f"장노년일자리지원센터_최종1{file_count}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {save_path}")

# 크롤링 실행
file_count = 1  # 저장된 파일 번호를 추적

while current_page <= pages:
    url = f"https://www.busan50plus.or.kr/job/gojob?job_local=&company_type=&recruit_type=&pay_min=&pay_max=&query=company_name&keyword=&page={current_page}"
    driver.get(url)
    time.sleep(2)
    
    # 공고 리스트 추출
    links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
    num_links = len(links)
    
    i = 0
    while i < num_links:
        try:
            # 링크를 다시 찾아서 StaleElementReferenceException 방지
            links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
            
            if i >= len(links):
                print(f"Skipping index {i} as it exceeds the length of available links.")
                break
            
            link = links[i]
            link_url = link.get_attribute('href')
            driver.get(link_url)
            time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
            # Explicit wait for the element to be visible
            wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
            # 기업명, 채용분야, 근무형태, 접수기간 추출
            기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='기관명']]/td"))).text
            채용분야 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='채용분야']]/td"))).text
            근무형태 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='근무형태']]/td"))).text
            접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='접수기간']]/td"))).text
            
            # 공고 제목 추출
            제목 = driver.find_element(By.XPATH, "//div[@class='ed_or_title']/h4/span").text
            
            # 연락처 추출
            try:
                연락처 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='연락처']]/td"))).text
            except NoSuchElementException:
                연락처 = ""  # 연락처가 없는 경우 빈 문자열로 처리
            
            # 세부내용 추출 (table 태그 내용 제외, <br> 태그 유지)
            html_content = driver.find_element(By.XPATH, "//div[@class='ed_or_contents01 ed_or_study']").get_attribute("innerHTML")
            soup = BeautifulSoup(html_content, 'html.parser')

            # <table> 태그 제거
            for table in soup.find_all('table'):
                table.decompose()

            # 다른 태그는 제거하고 <br> 태그만 남김
            for tag in soup.find_all(True):  # 모든 태그를 찾음
                if tag.name == "br":
                    continue  # <br> 태그는 유지
                tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

            세부내용 = str(soup)  # 수정된 HTML 내용을 문자열로 변환

            # 리스트에 데이터 추가
            출처_list.append("장노년일자리지원센터")
            기업명_list.append(기업명)
            채용분야_list.append(채용분야)
            근무형태_list.append(근무형태)
            접수기간_list.append(접수기간)
            제목_list.append(제목)
            세부내용_list.append(세부내용)
            링크_list.append(link_url)
            연락처_list.append(연락처)
            조회수_list.append(0)  # 조회수는 0으로 설정

            i += 1  # 다음 링크로 이동
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Element not found or timeout. Skipping: {link_url}")
            i += 1  # 다음 링크로 이동
            continue
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
            continue
        except Exception as e:
            print(f"Error: {e}")
            i += 1  # 오류가 발생해도 다음 링크로 이동
            continue
        
        driver.back()
        time.sleep(3)
    
    if current_page % save_interval == 0 or current_page == pages:
        make_df(file_count)
        file_count += 1
        출처_list, 기업명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 제목_list, 링크_list, 연락처_list, 조회수_list = initialize_lists()
    
    current_page += 1  # 다음 페이지로 이동

# 남은 데이터 저장
if 출처_list:
    make_df(file_count)

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
# from bs4 import BeautifulSoup

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트 초기화 함수
# def initialize_lists():
#     return [], [], [], [], [], [], []

# 기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list, 링크_list = initialize_lists()

# # 페이지 수 설정
# current_page = 1
# pages = 20  # 총 페이지 수
# save_interval = 1  # 몇 페이지마다 저장할지 설정

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(file_count):
#     df = pd.DataFrame({
#         '기관명': 기관명_list,
#         '채용분야': 채용분야_list,
#         '근무형태': 근무형태_list,
#         '접수기간': 접수기간_list,
#         '공고제목': 공고제목_list,
#         '세부내용': 세부내용_list,
#         '링크': 링크_list
#     })
#     save_path = os.path.join(save_dir, f"장노년일자리지원센터_{file_count}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"Data saved to {save_path}")

# # 크롤링 실행
# file_count = 1  # 저장된 파일 번호를 추적

# while current_page <= pages:
#     url = f"https://www.busan50plus.or.kr/job/gojob?job_local=&company_type=&recruit_type=&pay_min=&pay_max=&query=company_name&keyword=&page={current_page}"
#     driver.get(url)
#     time.sleep(2)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기관명, 채용분야, 근무형태, 접수기간 추출
#             기관명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='기관명']]/td"))).text
#             채용분야 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='채용분야']]/td"))).text
#             근무형태 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='근무형태']]/td"))).text
#             접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='접수기간']]/td"))).text

#             # 공고 제목 추출
#             공고제목 = driver.find_element(By.XPATH, "//div[@class='ed_or_title']/h4/span").text
            
#             # 세부내용 추출 (table 태그 내용 제외, <br> 태그 유지)
#             html_content = driver.find_element(By.XPATH, "//div[@class='ed_or_contents01 ed_or_study']").get_attribute("innerHTML")
#             soup = BeautifulSoup(html_content, 'html.parser')

#             # <table> 태그 제거
#             for table in soup.find_all('table'):
#                 table.decompose()

#             # 다른 태그는 제거하고 <br> 태그만 남김
#             for tag in soup.find_all(True):  # 모든 태그를 찾음
#                 if tag.name == "br":
#                     continue  # <br> 태그는 유지
#                 tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

#             세부내용 = str(soup)  # 수정된 HTML 내용을 문자열로 변환

#             # 리스트에 데이터 추가
#             기관명_list.append(기관명)
#             채용분야_list.append(채용분야)
#             근무형태_list.append(근무형태)
#             접수기간_list.append(접수기간)
#             공고제목_list.append(공고제목)
#             세부내용_list.append(세부내용)
#             링크_list.append(link_url)

#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(3)
    
#     if current_page % save_interval == 0 or current_page == pages:
#         make_df(file_count)
#         file_count += 1
#         기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list, 링크_list = initialize_lists()
    
#     current_page += 1  # 다음 페이지로 이동

# # 남은 데이터 저장
# if 기관명_list:
#     make_df(file_count)

# # 드라이버 종료
# driver.quit()

# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd
# from bs4 import BeautifulSoup

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트 초기화 함수
# def initialize_lists():
#     return [], [], [], [], [], [], []

# 기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list, 링크_list = initialize_lists()

# # 페이지 수 설정
# current_page = 1
# pages = 20  # 총 페이지 수
# save_interval = 1  # 몇 페이지마다 저장할지 설정

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(file_count):
#     df = pd.DataFrame({
#         '기관명': 기관명_list,
#         '채용분야': 채용분야_list,
#         '근무형태': 근무형태_list,
#         '접수기간': 접수기간_list,
#         '공고제목': 공고제목_list,
#         '세부내용': 세부내용_list,
#         '링크': 링크_list
#     })
#     save_path = os.path.join(save_dir, f"장노년일자리지원센터_{file_count}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"Data saved to {save_path}")

# # 크롤링 실행
# file_count = 1  # 저장된 파일 번호를 추적

# while current_page <= pages:
#     url = f"https://www.busan50plus.or.kr/job/gojob?job_local=&company_type=&recruit_type=&pay_min=&pay_max=&query=company_name&keyword=&page={current_page}"
#     driver.get(url)
#     time.sleep(2)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기관명, 채용분야, 근무형태, 접수기간 추출
#             기관명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='기관명']]/td"))).text
#             채용분야 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='채용분야']]/td"))).text
#             근무형태 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='근무형태']]/td"))).text
#             접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='접수기간']]/td"))).text

#             # 공고 제목 추출
#             공고제목 = driver.find_element(By.XPATH, "//div[@class='ed_or_title']/h4/span").text
            
#             # 세부내용 추출 (table 태그 내용 제외, <br> 태그 유지)
#             html_content = driver.find_element(By.XPATH, "//div[@class='ed_or_contents01 ed_or_study']").get_attribute("innerHTML")
#             soup = BeautifulSoup(html_content, 'html.parser')

#             # <table> 태그 제거
#             for table in soup.find_all('table'):
#                 table.decompose()

#             # <br> 태그를 <br> 그대로 유지
#             for br in soup.find_all("br"):
#                 br.replace_with("\n")

#             세부내용 = soup.get_text(separator='\n', strip=False)

#             # 리스트에 데이터 추가
#             기관명_list.append(기관명)
#             채용분야_list.append(채용분야)
#             근무형태_list.append(근무형태)
#             접수기간_list.append(접수기간)
#             공고제목_list.append(공고제목)
#             세부내용_list.append(세부내용)
#             링크_list.append(link_url)

#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(3)
    
#     if current_page % save_interval == 0 or current_page == pages:
#         make_df(file_count)
#         file_count += 1
#         기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list, 링크_list = initialize_lists()
    
#     current_page += 1  # 다음 페이지로 이동

# # 남은 데이터 저장
# if 기관명_list:
#     make_df(file_count)

# # 드라이버 종료
# driver.quit()

# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd
# from bs4 import BeautifulSoup

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트 초기화 함수
# def initialize_lists():
#     return [], [], [], [], [], []

# 기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list = initialize_lists()

# # 페이지 수 설정
# current_page = 1
# pages = 20  # 총 페이지 수
# save_interval = 1  # 몇 페이지마다 저장할지 설정

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(file_count):
#     df = pd.DataFrame({
#         '기관명': 기관명_list,
#         '채용분야': 채용분야_list,
#         '근무형태': 근무형태_list,
#         '접수기간': 접수기간_list,
#         '공고제목': 공고제목_list,
#         '세부내용': 세부내용_list
#     })
#     save_path = os.path.join(save_dir, f"장노년일자리지원센터_{file_count}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"Data saved to {save_path}")

# # 크롤링 실행
# file_count = 1  # 저장된 파일 번호를 추적

# while current_page <= pages:
#     url = f"https://www.busan50plus.or.kr/job/gojob?job_local=&company_type=&recruit_type=&pay_min=&pay_max=&query=company_name&keyword=&page={current_page}"
#     driver.get(url)
#     time.sleep(2)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기관명, 채용분야, 근무형태, 접수기간 추출
#             기관명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='기관명']]/td"))).text
#             채용분야 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='채용분야']]/td"))).text
#             근무형태 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='근무형태']]/td"))).text
#             접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='접수기간']]/td"))).text

#             # 공고 제목 추출
#             공고제목 = driver.find_element(By.XPATH, "//div[@class='ed_or_title']/h4/span").text
            
#             # 세부내용 추출 (table 태그 내용 제외)
#             html_content = driver.find_element(By.XPATH, "//div[@class='ed_or_contents01 ed_or_study']").get_attribute("innerHTML")
#             soup = BeautifulSoup(html_content, 'html.parser')

#             # <table> 태그 제거
#             for table in soup.find_all('table'):
#                 table.decompose()

#             세부내용 = soup.get_text(separator='\n', strip=True)

#             # 리스트에 데이터 추가
#             기관명_list.append(기관명)
#             채용분야_list.append(채용분야)
#             근무형태_list.append(근무형태)
#             접수기간_list.append(접수기간)
#             공고제목_list.append(공고제목)
#             세부내용_list.append(세부내용)

#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(3)
    
#     if current_page % save_interval == 0 or current_page == pages:
#         make_df(file_count)
#         file_count += 1
#         기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 공고제목_list = initialize_lists()
    
#     current_page += 1  # 다음 페이지로 이동

# # 남은 데이터 저장
# if 기관명_list:
#     make_df(file_count)

# # 드라이버 종료
# driver.quit()




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

# # 데이터 저장용 리스트
# 기관명_list = []
# 채용분야_list = []
# 근무형태_list = []
# 접수기간_list = []
# 세부내용_list = []

# # 페이지 수 설정
# current_page = 1
# pages = 10

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, num):
#     df = pd.DataFrame({
#         '기관명': 기관명_list,
#         '채용분야': 채용분야_list,
#         '근무형태': 근무형태_list,
#         '접수기간': 접수기간_list,
#         '세부내용': 세부내용_list
#     })
#     save_path = os.path.join(save_dir, f"채용정보_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 크롤링 실행
# while current_page <= pages:
#     url = f"https://www.busan50plus.or.kr/job/gojob?job_local=&company_type=&recruit_type=&pay_min=&pay_max=&query=company_name&keyword=&page={current_page}"
#     driver.get(url)
#     time.sleep(2)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.CSS_SELECTOR, 'td.jg02 a')
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기관명, 채용분야, 근무형태, 접수기간 추출
#             기관명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='기관명']]/td"))).text
#             채용분야 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='채용분야']]/td"))).text
#             근무형태 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='근무형태']]/td"))).text
#             접수기간 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='ed_or_contents01']//tr[th[text()='접수기간']]/td"))).text
            
#             # 세부내용 추출 (div 안의 모든 텍스트)
#             세부내용 = driver.find_element(By.XPATH, "//div[@class='ed_or_contents01 ed_or_study']").get_attribute("innerText")
            
#             기관명_list.append(기관명)
#             채용분야_list.append(채용분야)
#             근무형태_list.append(근무형태)
#             접수기간_list.append(접수기간)
#             세부내용_list.append(세부내용)
            
#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(2)
    
#     if current_page % 5 == 0:  # 중간 저장
#         make_df(기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, current_page)
    
#     current_page += 1  # 다음 페이지로 이동

# # 최종 저장
# make_df(기관명_list, 채용분야_list, 근무형태_list, 접수기간_list, 세부내용_list, 'final')

# # 드라이버 종료
# driver.quit()

