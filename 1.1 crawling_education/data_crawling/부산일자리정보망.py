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
강좌명_list = []
기관명_list = []
대상_list = []
신청기간_list = []
진행기간_list = []
신청방법_list = []
링크_list = []
담당자_list = []
담당부서_list = []
전화번호_list = []
이메일_list = []
상세보기_링크_list = []
세부사항_list = []
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
        len(기관명_list),
        len(대상_list),
        len(신청기간_list),
        len(진행기간_list),
        len(신청방법_list),
        len(링크_list),
        len(담당자_list),
        len(담당부서_list),
        len(전화번호_list),
        len(이메일_list),
        len(상세보기_링크_list),
        len(세부사항_list),
        len(조회수_list)  # 조회수 리스트 추가
    )

    # 리스트의 길이를 max_length에 맞추기
    def pad_list(lst):
        return lst + [''] * (max_length - len(lst))
    
    df = pd.DataFrame({
        '강좌명': pad_list(강좌명_list),
        '기관명': pad_list(기관명_list),
        '대상': pad_list(대상_list),
        '신청기간': pad_list(신청기간_list),
        '진행기간': pad_list(진행기간_list),
        '신청방법': pad_list(신청방법_list),
        '링크': pad_list(링크_list),
        '담당자': pad_list(담당자_list),
        '담당부서': pad_list(담당부서_list),
        '전화번호': pad_list(전화번호_list),
        '이메일': pad_list(이메일_list),
        '상세보기 링크': pad_list(상세보기_링크_list),
        '세부사항': pad_list(세부사항_list),
        '조회수': pad_list(조회수_list)  # 조회수 열 추가
    })
    save_path = get_non_duplicate_filename(save_dir, f"부산일자리정보망_{num}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')

# 초기 페이지 설정
url = "https://www.busanjob.net/03_part/part01.asp?search_mode=Y&search_save=N&keyword=&kind1_type=P&kind1_type_k=P&kind2_type=JP04&kind2_type=JP05&kind2_type_k=JP04%2CJP05"
driver.get(url)
time.sleep(5)

try:
    wait = WebDriverWait(driver, 10)

    # 페이지 번호 반복 설정
    for page in range(1, 2):  # 페이지 수에 따라 조정 (20)
        try:
            if page > 1:
                try:
                    page_button = driver.find_element(By.XPATH, f"//a[@title='{page}']")
                    page_button.click()
                except NoSuchElementException:
                    next_button = driver.find_element(By.XPATH, "//div[@class='pb_box']/img[contains(@src, 'pagebt_next.png')]")
                    next_button.click()

                time.sleep(5)

            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:MoveMoreView')]")
            
            for link in links:
                try:
                    href = link.get_attribute('href')
                    idx_value = href.split('MoveMoreView(')[1].split(')')[0]

                    detail_url = f"https://www.busanjob.net/03_part/part01_view.asp?idx={idx_value}&page={page}&params=search_mode%3DY%26search_save%3DN%26keyword%3D%26kind1_type%3DP%26kind1_type_k%3DP%26kind2_type%3DJP04%26kind2_type%3DJP05%26kind2_type_k%3DJP04%252CJP05"
                    
                    driver.get(detail_url)
                    time.sleep(5)

                    try:
                        강좌명 = wait.until(EC.presence_of_element_located((By.XPATH, ".//h2[@class='txt_center']"))).text
                    except TimeoutException:
                        강좌명 = ""
                    강좌명_list.append(강좌명)

                    try:
                        기관명 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '기관명')]/following-sibling::div"))).text
                    except TimeoutException:
                        기관명 = ""
                    기관명_list.append(기관명)

                    try:
                        대상 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '대상')]/following-sibling::div"))).text
                    except TimeoutException:
                        대상 = ""
                    대상_list.append(대상)

                    try:
                        신청기간 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '신청기간')]/following-sibling::div"))).text
                    except TimeoutException:
                        신청기간 = ""
                    신청기간_list.append(신청기간)

                    try:
                        진행기간 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '진행기간')]/following-sibling::div"))).text
                    except TimeoutException:
                        진행기간 = ""
                    진행기간_list.append(진행기간)

                    try:
                        신청방법 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '신청방법')]/following-sibling::div"))).text
                    except TimeoutException:
                        신청방법 = ""
                    신청방법_list.append(신청방법)

                    try:
                        링크 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '링크')]/following-sibling::div/a"))).get_attribute('href')
                    except TimeoutException:
                        링크 = ""
                    링크_list.append(링크)

                    try:
                        담당자 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '담당자')]/following-sibling::div"))).text
                    except TimeoutException:
                        담당자 = ""
                    담당자_list.append(담당자)

                    try:
                        담당부서 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '담당부서')]/following-sibling::div"))).text
                    except TimeoutException:
                        담당부서 = ""
                    담당부서_list.append(담당부서)

                    try:
                        전화번호 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '전화번호')]/following-sibling::div"))).text
                    except TimeoutException:
                        전화번호 = ""
                    전화번호_list.append(전화번호)

                    try:
                        이메일 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '이메일')]/following-sibling::div"))).text
                    except TimeoutException:
                        이메일 = ""
                    이메일_list.append(이메일)

                    try:
                        세부사항 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='view_detail']"))).get_attribute('outerHTML')
                    except TimeoutException:
                        세부사항 = ""
                    세부사항_list.append(세부사항)

                    상세보기_링크_list.append(detail_url)
                    조회수_list.append(0)  # 조회수 기본값을 0으로 설정

                except NoSuchElementException:
                    print(f"Some elements could not be found on {driver.current_url}. Skipping...")

                driver.back()
                time.sleep(2)

        except NoSuchElementException:
            print(f"Page {page} not found or could not be loaded.")
            continue

except (TimeoutException, Exception) as e:
    print(f"Error: {e}")

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
# 강좌명_list = []
# 기관명_list = []
# 대상_list = []
# 신청기간_list = []
# 진행기간_list = []
# 신청방법_list = []
# 링크_list = []
# 담당자_list = []
# 담당부서_list = []
# 전화번호_list = []
# 이메일_list = []
# 상세보기_링크_list = []
# 세부사항_list = []

# # 저장 경로 설정
# save_dir = "./1.1 crawling_education/data"
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

# def make_df(num):
#     max_length = max(
#         len(강좌명_list),
#         len(기관명_list),
#         len(대상_list),
#         len(신청기간_list),
#         len(진행기간_list),
#         len(신청방법_list),
#         len(링크_list),
#         len(담당자_list),
#         len(담당부서_list),
#         len(전화번호_list),
#         len(이메일_list),
#         len(상세보기_링크_list),
#         len(세부사항_list)
#     )

#     # 리스트의 길이를 max_length에 맞추기
#     def pad_list(lst):
#         return lst + [''] * (max_length - len(lst))
    
#     df = pd.DataFrame({
#         '강좌명': pad_list(강좌명_list),
#         '기관명': pad_list(기관명_list),
#         '대상': pad_list(대상_list),
#         '신청기간': pad_list(신청기간_list),
#         '진행기간': pad_list(진행기간_list),
#         '신청방법': pad_list(신청방법_list),
#         '링크': pad_list(링크_list),
#         '담당자': pad_list(담당자_list),
#         '담당부서': pad_list(담당부서_list),
#         '전화번호': pad_list(전화번호_list),
#         '이메일': pad_list(이메일_list),
#         '상세보기 링크': pad_list(상세보기_링크_list),
#         '세부사항': pad_list(세부사항_list)
#     })
#     save_path = get_non_duplicate_filename(save_dir, f"부산일자리정보망_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 초기 페이지 설정
# url = "https://www.busanjob.net/03_part/part01.asp?search_mode=Y&search_save=N&keyword=&kind1_type=P&kind1_type_k=P&kind2_type=JP04&kind2_type=JP05&kind2_type_k=JP04%2CJP05"
# driver.get(url)
# time.sleep(5)

# try:
#     wait = WebDriverWait(driver, 10)

#     # 페이지 번호 반복 설정
#     for page in range(1, 20):  # 페이지 수에 따라 조정 (20)
#         try:
#             if page > 1:
#                 try:
#                     # 페이지 이동
#                     page_button = driver.find_element(By.XPATH, f"//a[@title='{page}']")
#                     page_button.click()
#                 except NoSuchElementException:
#                     # 페이지 번호 버튼이 없으면 '다음' 버튼 클릭
#                     next_button = driver.find_element(By.XPATH, "//div[@class='pb_box']/img[contains(@src, 'pagebt_next.png')]")
#                     next_button.click()

#                 time.sleep(5)  # 페이지 로드 대기

#             # 목록에서 상세보기 링크 추출
#             links = driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:MoveMoreView')]")
            
#             for link in links:
#                 try:
#                     # href 속성에서 ID 추출
#                     href = link.get_attribute('href')
#                     idx_value = href.split('MoveMoreView(')[1].split(')')[0]

#                     # 상세보기 URL 생성
#                     detail_url = f"https://www.busanjob.net/03_part/part01_view.asp?idx={idx_value}&page={page}&params=search_mode%3DY%26search_save%3DN%26keyword%3D%26kind1_type%3DP%26kind1_type_k%3DP%26kind2_type%3DJP04%26kind2_type%3DJP05%26kind2_type_k%3DJP04%252CJP05"
                    
#                     # 상세보기 페이지로 이동
#                     driver.get(detail_url)
#                     time.sleep(5)  # 페이지 로드 대기

#                     # 데이터 추출
#                     try:
#                         강좌명 = wait.until(EC.presence_of_element_located((By.XPATH, ".//h2[@class='txt_center']"))).text
#                     except TimeoutException:
#                         강좌명 = ""
#                     강좌명_list.append(강좌명)

#                     try:
#                         기관명 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '기관명')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         기관명 = ""
#                     기관명_list.append(기관명)

#                     try:
#                         대상 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '대상')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         대상 = ""
#                     대상_list.append(대상)

#                     try:
#                         신청기간 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '신청기간')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         신청기간 = ""
#                     신청기간_list.append(신청기간)

#                     try:
#                         진행기간 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '진행기간')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         진행기간 = ""
#                     진행기간_list.append(진행기간)

#                     try:
#                         신청방법 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '신청방법')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         신청방법 = ""
#                     신청방법_list.append(신청방법)

#                     try:
#                         링크 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '링크')]/following-sibling::div/a"))).get_attribute('href')
#                     except TimeoutException:
#                         링크 = ""
#                     링크_list.append(링크)

#                     try:
#                         담당자 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '담당자')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         담당자 = ""
#                     담당자_list.append(담당자)

#                     try:
#                         담당부서 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '담당부서')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         담당부서 = ""
#                     담당부서_list.append(담당부서)

#                     try:
#                         전화번호 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '전화번호')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         전화번호 = ""
#                     전화번호_list.append(전화번호)

#                     try:
#                         이메일 = wait.until(EC.presence_of_element_located((By.XPATH, ".//li/div[contains(text(), '이메일')]/following-sibling::div"))).text
#                     except TimeoutException:
#                         이메일 = ""
#                     이메일_list.append(이메일)

#                     try:
#                         # 세부사항을 HTML 태그와 함께 추출
#                         세부사항 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='view_detail']"))).get_attribute('outerHTML')
#                     except TimeoutException:
#                         세부사항 = ""
#                     세부사항_list.append(세부사항)

#                     # 상세보기 링크 추가
#                     상세보기_링크_list.append(detail_url)

#                 except NoSuchElementException:
#                     print(f"Some elements could not be found on {driver.current_url}. Skipping...")

#                 # 다시 목록 페이지로 돌아가기
#                 driver.back()
#                 time.sleep(2)  # 목록 페이지로 돌아가면 약간 대기

#         except NoSuchElementException:
#             print(f"Page {page} not found or could not be loaded.")
#             continue

# except (TimeoutException, Exception) as e:
#     print(f"Error: {e}")

# # 최종 저장
# make_df('final')

# # 드라이버 종료
# driver.quit()
