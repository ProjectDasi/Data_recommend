import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# 크롬 드라이버 설정
driver_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=driver_options)

# 데이터 저장용 리스트
출처_list = []
기업명_list = []
제목_list = []
급여_list = []
등록일_list = []
마감일_list = []
근무지역_list = []
링크_list = []
근무시간_list = []
문의_연락처_list = []
이메일_list = []
직무내용_list = []
조회수_list = []
우대사항_list = []  # 우대사항 리스트 추가

# 저장 경로 설정
save_dir = "./1. crawling/crawling_data_merged"
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

def extract_company_name(title):
    if '[채용중]' in title and '-' in title:
        return title.split('[채용중]')[1].split('-')[0].strip()
    else:
        return title

def make_df(num):
    df = pd.DataFrame({
        '출처': 출처_list,
        '기업명': 기업명_list,
        '제목': 제목_list,
        '급여': 급여_list,
        '등록일': 등록일_list,
        '마감일': 마감일_list,
        '근무지역': 근무지역_list,
        '링크': 링크_list,
        '근무시간': 근무시간_list,
        '연락처': 문의_연락처_list,
        '이메일': 이메일_list,
        '근무직종': 직무내용_list,
        '조회수': 조회수_list,
        '우대사항': 우대사항_list  # 우대사항 열 추가
    })
    save_path = get_non_duplicate_filename(save_dir, f"부산경영자총협회_최종_{num}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')

# 페이지 번호 반복 설정
for page in range(1, 5):  # 1부터 2페이지까지
    url = f"https://bsefapp.co.kr/board/joboffer/?page={page}"
    driver.get(url)
    time.sleep(5)

    # 공고 리스트 추출
    links = driver.find_elements(By.CSS_SELECTOR, 'div.bo_tit a')

    # 각 링크의 JavaScript 함수를 통해 추출한 코드 사용
    link_ids = [link.get_attribute('href').split("'")[1] for link in links]
    link_texts = [link.text.strip() for link in links]
    num_links = len(link_ids)

    # 등록일 추출
    dates = driver.find_elements(By.CSS_SELECTOR, 'td.td_datetime')
    dates_texts = [date.text for date in dates]

    # 조회수 추출
    조회수_elements = driver.find_elements(By.CSS_SELECTOR, 'td.td-hit')
    조회수_texts = [element.text.strip() for element in 조회수_elements]

    i = 0
    while i < num_links:
        try:
            # 해당 링크로 이동
            detail_url = f"https://bsefapp.co.kr/board/joboffer/details/?schCode={link_ids[i]}&page={page}"
            driver.get(detail_url)
            time.sleep(4)  # 페이지 로드 시간을 더 길게 설정

            # Explicit wait for the element to be visible
            wait = WebDriverWait(driver, 15)

            # 채용 제목 추출 (div id="bo_v_con" 안의 p 태그)
            제목 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='bo_v_con']//p/b/span"))).text
            제목_list.append(제목)

            # 기업명 추출 및 리스트에 추가
            기업명 = extract_company_name(제목)
            기업명_list.append(기업명)

            # 급여 추출
            급여_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[5]//td[2]//p")
            급여 = " ".join([element.text.strip() for element in 급여_elements])
            급여_list.append(급여)

            # 등록일 추가
            등록일_list.append(dates_texts[i])

            # 마감일 추출
            마감일_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[7]//td[2]//p")
            마감일 = " ".join([element.text.strip() for element in 마감일_elements])
            마감일_list.append(마감일)

            # 근무지역 추출
            근무지역_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[3]//td[2]//p")
            근무지역 = " ".join([element.text.strip() for element in 근무지역_elements])
            근무지역_list.append(근무지역)

            # 상세보기 링크 추가
            링크_list.append(detail_url)

            # 근무시간 추출
            근무시간_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[2]//td[2]//p")
            근무시간 = " ".join([element.text.strip() for element in 근무시간_elements])
            근무시간_list.append(근무시간)

            # 이메일 추출
            이메일_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[8]//td[2]//p")
            이메일 = " ".join([element.text.strip() for element in 이메일_elements])
            이메일_list.append(이메일)

            # 직무내용 추출
            직무내용_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[1]//td[2]//p")
            직무내용 = " ".join([element.text for element in 직무내용_elements])
            직무내용_list.append(직무내용)

            # 문의 연락처 추출
            try:
                문의_연락처 = driver.find_element(By.XPATH, "//b[contains(text(),'문의')]").text
            except NoSuchElementException:
                문의_연락처 = ""
            문의_연락처_list.append(문의_연락처)

            # 우대사항 추출 (예: "만 60세 이상")
            try:
                우대사항 = driver.find_element(By.XPATH, "//td[p[contains(text(),'연령')]]/following-sibling::td").text.strip()
                우대사항_list.append(우대사항)
            except NoSuchElementException:
                우대사항_list.append("정보 없음")

            # 조회수 추가
            조회수 = 조회수_texts[i]
            조회수_list.append(조회수)

            # 출처 추가
            출처_list.append("부산경영자총협회")

            i += 1  # 다음 링크로 이동

        except (TimeoutException, Exception) as e:
            print(f"Error: {e}")

            # 모든 리스트에 빈 값을 추가하여 길이를 맞춤
            출처_list.append("부산경영자총협회")
            기업명_list.append("")
            제목_list.append("")
            급여_list.append("")
            등록일_list.append("")
            마감일_list.append("")
            근무지역_list.append("")
            링크_list.append("")
            근무시간_list.append("")
            문의_연락처_list.append("")
            이메일_list.append("")
            직무내용_list.append("")
            조회수_list.append("")
            우대사항_list.append("")

            i += 1  # 다음 링크로 이동하여 계속 크롤링 진행
            continue  # 루프의 다음 반복으로 넘어감

        # 목록 페이지로 돌아가기
        driver.get(url)
        time.sleep(3)

# 최종 저장
make_df('final')

# 드라이버 종료
driver.quit()


# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트
# 출처_list = []
# 기업명_list = []
# 제목_list = []
# 급여_list = []
# 등록일_list = []
# 마감일_list = []
# 근무지역_list = []
# 링크_list = []
# 근무시간_list = []
# 문의_연락처_list = []
# 이메일_list = []
# 직무내용_list = []
# 조회수_list = []

# # 저장 경로 설정
# save_dir = "./1. crawling/crawling_data_merged"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def get_non_duplicate_filename(base_dir, base_filename):
#     filename, extension = os.path.splitext(base_filename)
#     counter = 1
#     new_filename = base_filename
#     while os.path.exists(os.path.join(base_dir, new_filename)):
#         new_filename = f"{filename}_{counter}{extension}"
#         counter += 1
#     return os.path.join(base_dir, new_filename)

# def extract_company_name(title):
#     if '[채용중]' in title and '-' in title:
#         return title.split('[채용중]')[1].split('-')[0].strip()
#     else:
#         return title

# def make_df(num):
#     df = pd.DataFrame({
#         '출처': 출처_list,
#         '기업명': 기업명_list,
#         '제목': 제목_list,
#         '급여': 급여_list,
#         '등록일': 등록일_list,
#         '마감일': 마감일_list,
#         '근무지역': 근무지역_list,
#         '링크': 링크_list,
#         '근무시간': 근무시간_list,
#         '연락처': 문의_연락처_list,
#         '이메일': 이메일_list,
#         '근무직종': 직무내용_list,
#         '조회수': 조회수_list  # 조회수 열 추가
#     })
#     save_path = get_non_duplicate_filename(save_dir, f"부산경영자총협회_최종_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 페이지 번호 반복 설정
# for page in range(1, 2):  # 1부터 4페이지까지
#     url = f"https://bsefapp.co.kr/board/joboffer/?page={page}"
#     driver.get(url)
#     time.sleep(5)

#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'div.bo_tit a')

#     # 각 링크의 JavaScript 함수를 통해 추출한 코드 사용
#     link_ids = [link.get_attribute('href').split("'")[1] for link in links]
#     link_texts = [link.text.strip() for link in links]
#     num_links = len(link_ids)

#     # 등록일 추출
#     dates = driver.find_elements(By.CSS_SELECTOR, 'td.td_datetime')
#     dates_texts = [date.text for date in dates]

#     # 조회수 추출
#     조회수_elements = driver.find_elements(By.CSS_SELECTOR, 'td.td-hit')
#     조회수_texts = [element.text.strip() for element in 조회수_elements]

#     i = 0
#     while i < num_links:
#         try:
#             # 해당 링크로 이동
#             detail_url = f"https://bsefapp.co.kr/board/joboffer/details/?schCode={link_ids[i]}&page={page}"
#             driver.get(detail_url)
#             time.sleep(4)  # 페이지 로드 시간을 더 길게 설정

#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)

#             # 채용 제목 추출 (div id="bo_v_con" 안의 p 태그)
#             제목 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='bo_v_con']//p/b/span"))).text
#             제목_list.append(제목)

#             # 기업명 추출 및 리스트에 추가
#             기업명 = extract_company_name(제목)
#             기업명_list.append(기업명)

#             # 급여 추출
#             급여_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[5]//td[2]//p")
#             급여 = " ".join([element.text.strip() for element in 급여_elements])
#             급여_list.append(급여)

#             # 등록일 추가
#             등록일_list.append(dates_texts[i])

#             # 마감일 추출
#             마감일_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[7]//td[2]//p")
#             마감일 = " ".join([element.text.strip() for element in 마감일_elements])
#             마감일_list.append(마감일)

#             # 근무지역 추출
#             근무지역_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[3]//td[2]//p")
#             근무지역 = " ".join([element.text.strip() for element in 근무지역_elements])
#             근무지역_list.append(근무지역)

#             # 상세보기 링크 추가
#             링크_list.append(detail_url)

#             # 근무시간 추출
#             근무시간_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[2]//td[2]//p")
#             근무시간 = " ".join([element.text.strip() for element in 근무시간_elements])
#             근무시간_list.append(근무시간)

#             # 이메일 추출
#             이메일_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[8]//td[2]//p")
#             이메일 = " ".join([element.text.strip() for element in 이메일_elements])
#             이메일_list.append(이메일)

#             # 직무내용 추출
#             직무내용_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[1]//td[2]//p")
#             직무내용 = " ".join([element.text for element in 직무내용_elements])
#             직무내용_list.append(직무내용)

#             # 문의 연락처 추출
#             try:
#                 문의_연락처 = driver.find_element(By.XPATH, "//b[contains(text(),'문의')]").text
#             except NoSuchElementException:
#                 문의_연락처 = ""
#             문의_연락처_list.append(문의_연락처)

#             # 조회수 추가
#             조회수 = 조회수_texts[i]
#             조회수_list.append(조회수)

#             # 출처 추가
#             출처_list.append("부산경영자총협회")

#             i += 1  # 다음 링크로 이동

#         except (TimeoutException, Exception) as e:
#             print(f"Error: {e}")

#             # 모든 리스트에 빈 값을 추가하여 길이를 맞춤
#             출처_list.append("부산경영자총협회")
#             기업명_list.append("")
#             제목_list.append("")
#             급여_list.append("")
#             등록일_list.append("")
#             마감일_list.append("")
#             근무지역_list.append("")
#             링크_list.append("")
#             근무시간_list.append("")
#             문의_연락처_list.append("")
#             이메일_list.append("")
#             직무내용_list.append("")
#             조회수_list.append("")

#             i += 1  # 다음 링크로 이동하여 계속 크롤링 진행
#             continue  # 루프의 다음 반복으로 넘어감

#         # 목록 페이지로 돌아가기
#         driver.get(url)
#         time.sleep(3)

# # 최종 저장
# make_df('final')

# # 드라이버 종료
# driver.quit()





# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트
# 기업명_list = []
# 제목_list = []
# 직무내용_list = []
# 근무시간_list = []
# 링크_list = []
# 이메일_list = []

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def get_non_duplicate_filename(base_dir, base_filename):
#     """
#     주어진 디렉토리와 파일 이름을 기반으로 중복되지 않는 파일 이름을 생성합니다.
#     """
#     filename, extension = os.path.splitext(base_filename)
#     counter = 1
#     new_filename = base_filename
#     while os.path.exists(os.path.join(base_dir, new_filename)):
#         new_filename = f"{filename}_{counter}{extension}"
#         counter += 1
#     return os.path.join(base_dir, new_filename)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '제목': 제목_list,
#         '직무내용': 직무내용_list,
#         '근무시간': 근무시간_list,
#         '링크': 링크_list,
#         '이메일': 이메일_list,
#     })
#     # 중복되지 않는 파일 이름을 생성하여 저장
#     save_path = get_non_duplicate_filename(save_dir, f"부산경영자총협회_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 페이지 번호 반복 설정
# for page in range(1, 5):  # 1부터 4페이지까지
#     url = f"https://bsefapp.co.kr/board/joboffer/?page={page}"
#     driver.get(url)
#     time.sleep(5)

#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'div.bo_tit a')

#     # 각 링크의 JavaScript 함수를 통해 추출한 코드 사용
#     link_ids = [link.get_attribute('href').split("'")[1] for link in links]
#     link_texts = [link.text.strip() for link in links]
#     num_links = len(link_ids)

#     # 등록일 추출
#     dates = driver.find_elements(By.CSS_SELECTOR, 'td.td_datetime')
#     dates_texts = [date.text for date in dates]

#     i = 0
#     while i < num_links:
#         try:
#             # 해당 링크로 이동
#             detail_url = f"https://bsefapp.co.kr/board/joboffer/details/?schCode={link_ids[i]}&page={page}"
#             driver.get(detail_url)
#             time.sleep(4)  # 페이지 로드 시간을 더 길게 설정

#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)

#             # 제목 추출 (div id="bo_v_con" 안의 p 태그)
#             제목 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='bo_v_con']//p/b/span"))).text
#             제목_list.append(제목)

#             # 기업명 추출 (제목에서 [채용중] 텍스트1 - 텍스트2 에서 텍스트1 추출)
#             기업명 = 제목.split('-')[0].replace('[채용중]', '').strip()
#             기업명_list.append(기업명)

#             # 직무내용 추출 (div id="bo_v_con" 안의 table에서 직무내용 텍스트 추출)
#             직무내용_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[1]//td[2]//p")
#             직무내용 = " ".join([element.text for element in 직무내용_elements])
#             직무내용_list.append(직무내용)

#             # 근무시간 추출 (div id="bo_v_con" 안의 table에서 근무시간 텍스트 추출)
#             근무시간_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[2]//td[2]//p")
#             근무시간 = " ".join([element.text.strip() for element in 근무시간_elements])
#             근무시간_list.append(근무시간)

#             # 링크 추가
#             링크_list.append(detail_url)

#             # 이메일 추출 (이전 이력서_제출서 열에 해당)
#             이력서_제출서_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[8]//td[2]//p")
#             이메일 = " ".join([element.text.strip() for element in 이력서_제출서_elements])
#             이메일_list.append(이메일)

#             i += 1  # 다음 링크로 이동

#         except (TimeoutException, Exception) as e:
#             print(f"Error: {e}")

#             # 모든 리스트에 빈 값을 추가하여 길이를 맞춤
#             기업명_list.append("")
#             제목_list.append("")
#             직무내용_list.append("")
#             근무시간_list.append("")
#             링크_list.append("")
#             이메일_list.append("")

#             i += 1  # 다음 링크로 이동하여 계속 크롤링 진행
#             continue  # 루프의 다음 반복으로 넘어감

#         # 목록 페이지로 돌아가기
#         driver.get(url)
#         time.sleep(3)

# # 최종 저장
# make_df('final')

# # 드라이버 종료
# driver.quit()

# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트
# 채용제목_list = []
# 직무내용_list = []
# 근무시간_list = []
# 근무지역_list = []
# 모집인원_list = []
# 급여_list = []
# 연령_list = []
# 등록일_list = []
# 마감일_list = []
# 이력서_제출서_list = []
# 구인공고_링크_list = []
# 상세보기_링크_list = []
# 문의_연락처_list = []

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def get_non_duplicate_filename(base_dir, base_filename):
#     """
#     주어진 디렉토리와 파일 이름을 기반으로 중복되지 않는 파일 이름을 생성합니다.
#     """
#     filename, extension = os.path.splitext(base_filename)
#     counter = 1
#     new_filename = base_filename
#     while os.path.exists(os.path.join(base_dir, new_filename)):
#         new_filename = f"{filename}_{counter}{extension}"
#         counter += 1
#     return os.path.join(base_dir, new_filename)

# def make_df(num):
#     df = pd.DataFrame({
#         '채용제목': 채용제목_list,
#         '직무내용': 직무내용_list,
#         '근무시간': 근무시간_list,
#         '근무지역': 근무지역_list,
#         '모집인원': 모집인원_list,
#         '급여': 급여_list,
#         '연령': 연령_list,
#         '등록일': 등록일_list,
#         '마감일': 마감일_list,
#         '이력서_제출서': 이력서_제출서_list,
#         '구인공고_링크': 구인공고_링크_list,
#         '상세보기_링크': 상세보기_링크_list,
#         '문의_연락처': 문의_연락처_list
#     })
#     # 중복되지 않는 파일 이름을 생성하여 저장
#     save_path = get_non_duplicate_filename(save_dir, f"부산경영자총협회_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 페이지 번호 반복 설정
# for page in range(1, 5):  # 1부터 4페이지까지
#     url = f"https://bsefapp.co.kr/board/joboffer/?page={page}"
#     driver.get(url)
#     time.sleep(5)

#     # 공고 리스트 추출
#     links = driver.find_elements(By.CSS_SELECTOR, 'div.bo_tit a')

#     # 각 링크의 JavaScript 함수를 통해 추출한 코드 사용
#     link_ids = [link.get_attribute('href').split("'")[1] for link in links]
#     link_texts = [link.text.strip() for link in links]
#     num_links = len(link_ids)

#     # 등록일 추출
#     dates = driver.find_elements(By.CSS_SELECTOR, 'td.td_datetime')
#     dates_texts = [date.text for date in dates]

#     i = 0
#     while i < num_links:
#         try:
#             # 해당 링크로 이동
#             detail_url = f"https://bsefapp.co.kr/board/joboffer/details/?schCode={link_ids[i]}&page={page}"
#             driver.get(detail_url)
#             time.sleep(4)  # 페이지 로드 시간을 더 길게 설정

#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)

#             # 채용 제목 추출 (div id="bo_v_con" 안의 p 태그)
#             채용제목 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='bo_v_con']//p/b/span"))).text
#             채용제목_list.append(채용제목)

#             # 직무내용 추출 (div id="bo_v_con" 안의 table에서 직무내용 텍스트 추출)
#             직무내용_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[1]//td[2]//p")
#             직무내용 = " ".join([element.text for element in 직무내용_elements])
#             직무내용_list.append(직무내용)

#             # 근무시간 추출 (div id="bo_v_con" 안의 table에서 근무시간 텍스트 추출)
#             근무시간_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[2]//td[2]//p")
#             근무시간 = " ".join([element.text.strip() for element in 근무시간_elements])
#             근무시간_list.append(근무시간)

#             # 근무지역 추출 (div id="bo_v_con" 안의 table에서 근무지역 텍스트 추출)
#             근무지역_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[3]//td[2]//p")
#             근무지역 = " ".join([element.text.strip() for element in 근무지역_elements])
#             근무지역_list.append(근무지역)

#             # 모집인원 추출 (div id="bo_v_con" 안의 table에서 모집인원 텍스트 추출)
#             모집인원_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[4]//td[2]//p")
#             모집인원 = " ".join([element.text.strip() for element in 모집인원_elements])
#             모집인원_list.append(모집인원)

#             # 급여 추출 (div id="bo_v_con" 안의 table에서 급여 텍스트 추출)
#             급여_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[5]//td[2]//p")
#             급여 = " ".join([element.text.strip() for element in 급여_elements])
#             급여_list.append(급여)

#             # 연령 추출 (div id="bo_v_con" 안의 table에서 연령 텍스트 추출)
#             연령_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[6]//td[2]//p")
#             연령 = " ".join([element.text.strip() for element in 연령_elements])
#             연령_list.append(연령)

#             # 마감일 추출 (div id="bo_v_con" 안의 table에서 마감일 텍스트 추출)
#             마감일_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[7]//td[2]//p")
#             마감일 = " ".join([element.text.strip() for element in 마감일_elements])
#             마감일_list.append(마감일)

#             # 이력서 제출서 추출 (div id="bo_v_con" 안의 table에서 이력서 제출서 텍스트 추출)
#             이력서_제출서_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[8]//td[2]//p")
#             이력서_제출서 = " ".join([element.text.strip() for element in 이력서_제출서_elements])
#             이력서_제출서_list.append(이력서_제출서)

#             # 구인공고 링크 추출 (div id="bo_v_con" 안의 table에서 구인공고 링크 텍스트 추출)
#             구인공고_링크_elements = driver.find_elements(By.XPATH, "//div[@id='bo_v_con']//p/following-sibling::table//tr[9]//td[2]//a")
#             구인공고_링크 = " ".join([element.get_attribute('href').strip() for element in 구인공고_링크_elements])
#             구인공고_링크_list.append(구인공고_링크 if 구인공고_링크 else "")

#             # 상세보기 링크 추가
#             상세보기_링크_list.append(detail_url)

#             # 문의 연락처 추출
#             try:
#                 문의_연락처 = driver.find_element(By.XPATH, "//b[contains(text(),'문의')]").text
#             except NoSuchElementException:
#                 문의_연락처 = ""
#             문의_연락처_list.append(문의_연락처)

#             # 등록일 추가
#             등록일_list.append(dates_texts[i])

#             i += 1  # 다음 링크로 이동

#         except (TimeoutException, Exception) as e:
#             print(f"Error: {e}")

#             # 모든 리스트에 빈 값을 추가하여 길이를 맞춤
#             채용제목_list.append("")
#             직무내용_list.append("")
#             근무시간_list.append("")
#             근무지역_list.append("")
#             모집인원_list.append("")
#             급여_list.append("")
#             연령_list.append("")
#             마감일_list.append("")
#             이력서_제출서_list.append("")
#             구인공고_링크_list.append("")
#             상세보기_링크_list.append("")
#             문의_연락처_list.append("")
#             등록일_list.append("")

#             i += 1  # 다음 링크로 이동하여 계속 크롤링 진행
#             continue  # 루프의 다음 반복으로 넘어감

#         # 목록 페이지로 돌아가기
#         driver.get(url)
#         time.sleep(3)

# # 최종 저장
# make_df('final')

# # 드라이버 종료
# driver.quit()
