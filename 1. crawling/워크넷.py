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
    return [], [], [], [], [], [], [], [], [], [], [], [], [], [],[]

출처_list, 기업명_list, 채용공고명_list, 급여_list, 등록일_list, 마감일_list, 근무지역_list, 경력_list, 학력_list, 근무형태_list, 근무직종_list, 연락처_list, 세부내용_list, 자격면허_list, 링크_list = initialize_lists()

# 페이지 수 설정
current_page = 1
pages = 39

# 저장 경로 설정
save_dir = "./1.crawling/crawling_data_merged"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def make_df(num):
    df = pd.DataFrame({
        '출처': 출처_list,  
        '기업명': 기업명_list,
        '제목': 채용공고명_list,  
        '급여': 급여_list,  
        '등록일': 등록일_list,
        '마감일': 마감일_list,
        '근무지역': 근무지역_list,  
        '경력': 경력_list,
        '학력': 학력_list,
        '근무형태': 근무형태_list,
        '근무직종': 근무직종_list,  
        '연락처': 연락처_list,  
        '세부내용': 세부내용_list,  
        '자격면허': 자격면허_list,
        '링크': 링크_list  
    })
    save_path = os.path.join(save_dir, f"워크넷_최종{num}.csv")
    df.to_csv(save_path, index=False, encoding='utf-8-sig')

# 크롤링 실행
data_counter = 0  # 수집된 데이터 개수 카운터
save_counter = 1  # 저장 파일 번호 카운터

while current_page <= pages:
    url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=2&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
    driver.get(url)
    time.sleep(3)
    
    # 공고 리스트 추출
    rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
    num_links = len(rows)
    
    i = 0
    while i < num_links:
        try:
            # 링크 추출
            link = WebDriverWait(rows[i], 10).until(
                EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]"))
            )
            link_url = link.get_attribute('href')

            # 등록일 추출
            try:
                등록일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(text(), '등록')]").text.split()[0]
            except NoSuchElementException:
                등록일 = "정보 없음"

            # 마감일 추출
            try:
                element = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//span[starts-with(@id, 'spanCloseDt') or @id='dDayInfo']")
                마감일 = element.text.strip()
            except NoSuchElementException:
                마감일 = "정보 없음"

            # 상세 페이지로 이동
            driver.get(link_url)
            time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
            # 페이지가 유효하지 않다면 건너뛰기
            try:
                마감메시지 = driver.find_element(By.XPATH, "//div[contains(text(), '해당 채용은 마감되었습니다')]")
                print(f"채용 마감됨: {link_url}")
                driver.back()  # 페이지 뒤로가기
                time.sleep(2)
                i += 1  # 다음 링크로 이동
                rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")  # 리스트 재설정
                continue  # 마감된 공고이므로 다음 공고로 건너뜀
            except NoSuchElementException:
                pass  # 마감 메시지가 없으면 다음으로 진행

            # 기업명 추출
            try:
                기업명 = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))
                ).text
            except NoSuchElementException:
                기업명 = "정보 없음"
            
            # 채용공고명 추출
            try:
                채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
            except NoSuchElementException:
                채용공고명 = "정보 없음"
            
            # 임금 추출
            try:
                급여 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
            except NoSuchElementException:
                급여 = "정보 없음"
            
            # 지역 추출
            try:
                근무지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
            except NoSuchElementException:
                근무지역 = "정보 없음"
            
            # 경력, 학력, 근무형태 추출
            try:
                경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
            except NoSuchElementException:
                경력 = "정보 없음"

            try:
                학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
            except NoSuchElementException:
                학력 = "정보 없음"

            try:
                근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text
            except NoSuchElementException:
                근무형태 = "정보 없음"
            
            # 업종(근무직종) 추출
            try:
                근무직종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
            except NoSuchElementException:
                근무직종 = "정보 없음"

            # 연락처 추출 (연락처가 없는 경우 빈 문자열로 저장)
            try:
                연락처 = driver.find_element(By.XPATH, "//div[@class='careers-table charge center']//td[2]").text.strip()
            except NoSuchElementException:
                연락처 = ""  # 연락처가 없을 경우 빈 문자열 저장

            # 모집요강 추출 및 <br> 태그 유지
            try:
                모집요강_html = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerHTML")
                soup = BeautifulSoup(모집요강_html, 'html.parser')

                # <td> 태그 내의 텍스트만 추출하고 <br> 태그는 유지
                모집요강_td = soup.find('td')
                if 모집요강_td:
                    for tag in 모집요강_td.find_all(True):  # 모든 태그를 찾음
                        if tag.name == "br":
                            continue  # <br> 태그는 유지
                        tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

                    세부내용 = str(모집요강_td)  # <td> 내용만 문자열로 변환
                else:
                    세부내용 = "정보 없음"  # <td>가 없을 경우 기본값 설정
            except NoSuchElementException:
                세부내용 = "정보 없음"
            
            # 자격면허 추출
            try:
                자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
            except NoSuchElementException:
                자격면허 = "정보 없음"
            
            # 리스트에 데이터 추가
            출처_list.append('워크넷')  # 출처 값 추가
            기업명_list.append(기업명)
            채용공고명_list.append(채용공고명)
            급여_list.append(급여)
            등록일_list.append(등록일)
            마감일_list.append(마감일)
            근무지역_list.append(근무지역)
            경력_list.append(경력)
            학력_list.append(학력)
            근무형태_list.append(근무형태)
            근무직종_list.append(근무직종)
            연락처_list.append(연락처)  # 연락처 데이터 추가
            세부내용_list.append(세부내용)
            자격면허_list.append(자격면허)
            링크_list.append(link_url)  # 링크 추가

            data_counter += 1  # 데이터 개수 증가
            
            i += 1  # 다음 링크로 이동

            # 페이지 이동 후 다시 rows 업데이트
            driver.back()
            time.sleep(2)
            rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Element not found or timeout. Skipping: {link_url}")
            i += 1  # 다음 링크로 이동
            continue
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
            rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
            continue
        except Exception as e:
            print(f"Error: {e}")
            i += 1  # 오류가 발생해도 다음 링크로 이동
            continue
    
    # 10 페이지마다 저장
    if current_page % 20 == 0:
        make_df(f"_page_{save_counter}")
        save_counter += 1  # 저장 파일 번호 증가

    current_page += 1  # 다음 페이지로 이동

# 남은 데이터 최종 저장
make_df(f"_{save_counter}")

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

# # 데이터 저장용 리스트
# 기업명_list = []
# 채용공고명_list = []  # 제목
# 급여_list = []  # 임금
# 등록일_list = []
# 마감일_list = []
# 근무지역_list = []  # 지역
# 경력_list = []
# 학력_list = []
# 근무형태_list = []
# 근무직종_list = []  # 업종
# 링크_list = []  # 링크
# 세부내용_list = []  # 모집요강
# 자격면허_list = []  # 자격면허

# # 페이지 수 설정
# current_page = 1
# pages = 20

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '제목': 채용공고명_list,  # 채용공고명 -> 제목
#         '급여': 급여_list,  # 임금 -> 급여
#         '등록일': 등록일_list,
#         '마감일': 마감일_list,
#         '근무지역': 근무지역_list,  # 지역 -> 근무지역
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '근무형태': 근무형태_list,
#         '근무직종': 근무직종_list,  # 업종 -> 근무직종
#         '링크': 링크_list,
#         '세부내용': 세부내용_list,  # 모집요강 -> 세부내용
#         '자격면허': 자격면허_list
#     })
#     save_path = os.path.join(save_dir, f"워크넷2_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 크롤링 실행
# data_counter = 0  # 수집된 데이터 개수 카운터
# save_counter = 1  # 저장 파일 번호 카운터

# while current_page <= pages:
#     url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=2&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
#     driver.get(url)
#     time.sleep(3)
    
#     # 공고 리스트 추출
#     rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#     num_links = len(rows)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크 추출
#             link = WebDriverWait(rows[i], 10).until(
#                 EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]"))
#             )
#             link_url = link.get_attribute('href')

#             # 등록일 추출
#             등록일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(text(), '등록')]").text.split()[0]

#             # 마감일 추출
#             try:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//span[starts-with(@id, 'spanCloseDt')]").text.strip()
#             except NoSuchElementException:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(@class, 'dday')]").text.strip()

#             # 링크 데이터 추가
#             링크_list.append(link_url)
#             등록일_list.append(등록일)
#             마감일_list.append(마감일)
            
#             # 상세 페이지로 이동
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기업명 추출
#             기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))).text
            
#             # 채용공고명 추출
#             채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
            
#             # 임금 추출
#             급여 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
            
#             # 지역 추출
#             근무지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
            
#             # 경력, 학력, 근무형태 추출
#             경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
#             학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
#             근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text
            
#             # 업종(근무직종) 추출
#             근무직종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
            
#             # 모집요강 추출 및 <br> 태그 유지
#             모집요강_html = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerHTML")
#             soup = BeautifulSoup(모집요강_html, 'html.parser')

#             # <td> 태그 내의 텍스트만 추출하고 <br> 태그는 유지
#             모집요강_td = soup.find('td')
#             if 모집요강_td:
#                 for tag in 모집요강_td.find_all(True):  # 모든 태그를 찾음
#                     if tag.name == "br":
#                         continue  # <br> 태그는 유지
#                     tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

#                 세부내용 = str(모집요강_td)  # <td> 내용만 문자열로 변환
#             else:
#                 세부내용 = "정보 없음"  # <td>가 없을 경우 기본값 설정
            
#             # 자격면허 추출
#             자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
            
#             # 리스트에 데이터 추가
#             기업명_list.append(기업명)
#             채용공고명_list.append(채용공고명)
#             급여_list.append(급여)

#             근무지역_list.append(근무지역)
#             경력_list.append(경력)
#             학력_list.append(학력)
#             근무형태_list.append(근무형태)
#             근무직종_list.append(근무직종)

#             세부내용_list.append(세부내용)
#             자격면허_list.append(자격면허)

#             data_counter += 1  # 데이터 개수 증가
            
#             # 데이터가 5개 모일 때마다 저장
#             if data_counter % 5 == 0:
#                 make_df(f"_{save_counter}")
#                 save_counter += 1  # 저장 파일 번호 증가
            
#             i += 1  # 다음 링크로 이동

#             # 페이지 이동 후 다시 rows 업데이트
#             driver.back()
#             time.sleep(2)
#             rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
#             rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
    
#     current_page += 1  # 다음 페이지로 이동

# # 최종 저장
# make_df(f"워크넷_final_{save_counter}")

# # 드라이버 종료
# driver.quit()



# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, UnexpectedAlertPresentException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd
# from bs4 import BeautifulSoup

# # 크롬 드라이버 설정
# driver_options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=driver_options)

# # 데이터 저장용 리스트
# 기업명_list = []
# 업종_list = []
# 기업규모_list = []
# 설립년도_list = []
# 연매출액_list = []
# 홈페이지_list = []
# 근로자수_list = []

# 채용공고명_list = []
# 경력_list = []
# 학력_list = []
# 지역_list = []
# 임금_list = []
# 고용형태_list = []
# 근무형태_list = []
# 모집요강_list = []
# 자격면허_list = []  # 자격면허 리스트 추가
# 링크_list = []  # 링크 리스트 추가
# 등록일_list = []  # 등록일 리스트 추가
# 마감일_list = []  # 마감일 리스트 추가
# 연락처_list = []  # 연락처 리스트 추가

# # 페이지 수 설정
# current_page = 1
# pages = 20

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '업종': 업종_list,
#         '기업규모': 기업규모_list,
#         '설립년도': 설립년도_list,
#         '연매출액': 연매출액_list,
#         '홈페이지': 홈페이지_list,
#         '근로자수': 근로자수_list,
#         '채용공고명': 채용공고명_list,
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '지역': 지역_list,
#         '임금': 임금_list,
#         '고용형태': 고용형태_list,
#         '근무형태': 근무형태_list,
#         '모집요강': 모집요강_list,
#         '자격면허': 자격면허_list,  # 자격면허 추가
#         '링크': 링크_list,  # 링크 열 추가
#         '등록일': 등록일_list,  # 등록일 열 추가
#         '마감일': 마감일_list,  # 마감일 열 추가
#         '연락처': 연락처_list  # 연락처 열 추가
#     })
#     save_path = os.path.join(save_dir, f"워크넷1_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')
#     print(f"Data saved to {save_path}")

# # 크롤링 실행
# data_counter = 0  # 수집된 데이터 개수 카운터
# save_counter = 1  # 저장 파일 번호 카운터

# while current_page <= pages:
#     url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=2&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
#     print(f"Fetching page {current_page}: {url}")
#     driver.get(url)
#     time.sleep(3)
    
#     # 공고 리스트 추출
#     rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#     num_links = len(rows)
#     print(f"Found {num_links} job postings on page {current_page}")
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크 추출
#             link = WebDriverWait(rows[i], 10).until(
#                 EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]"))
#             )
#             link_url = link.get_attribute('href')
#             print(f"Processing job posting {i+1}/{num_links}: {link_url}")

#             # 등록일 추출
#             등록일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(text(), '등록')]").text.split()[0]
#             print(f"등록일: {등록일}")

#             # 마감일 추출
#             try:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//span[starts-with(@id, 'spanCloseDt')]").text.strip()
#             except NoSuchElementException:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(@class, 'dday')]").text.strip()
#             print(f"마감일: {마감일}")

#             # 링크 데이터 추가
#             링크_list.append(link_url)
#             등록일_list.append(등록일)
#             마감일_list.append(마감일)
            
#             # 상세 페이지로 이동
#             try:
#                 driver.get(link_url)
#                 time.sleep(3)  # 페이지 로드 시간을 더 길게 설정

#                 # 알림 창이 있는지 확인하고 처리
#                 try:
#                     alert = driver.switch_to.alert
#                     alert_text = alert.text
#                     if "접수마감시간이 지난 채용공고입니다." in alert_text:
#                         alert.accept()  # 알림 닫기
#                         print(f"Skipped closed job posting: {link_url}")
#                         i += 1
#                         continue  # 다음 공고로 넘어가기
#                 except:
#                     pass
                
#                 # Explicit wait for the element to be visible
#                 wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
                
#                 # 기업명, 업종, 기업규모 등 기본 정보 추출
#                 기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))).text
#                 업종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
#                 기업규모 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='기업규모']]/div").text
#                 설립년도 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='설립년도']]/div").text
#                 연매출액 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='연매출액']]/div").text
#                 홈페이지 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='홈페이지']]/div").text
#                 근로자수 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='근로자수']]/div").text

#                 print(f"기업명: {기업명}, 업종: {업종}, 기업규모: {기업규모}, 설립년도: {설립년도}, 연매출액: {연매출액}, 홈페이지: {홈페이지}, 근로자수: {근로자수}")
                
#                 # 채용공고명, 경력, 학력 등 공고 정보 추출
#                 채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
#                 경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
#                 학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
#                 지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
#                 임금 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
#                 고용형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='고용형태']]/span").text
#                 근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text

#                 print(f"채용공고명: {채용공고명}, 경력: {경력}, 학력: {학력}, 지역: {지역}, 임금: {임금}, 고용형태: {고용형태}, 근무형태: {근무형태}")
                
#                 # 모집요강 추출 및 <br> 태그 유지
#                 모집요강_html = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerHTML")
#                 soup = BeautifulSoup(모집요강_html, 'html.parser')

#                 # <td> 태그 내의 텍스트만 추출하고 <br> 태그는 유지
#                 모집요강_td = soup.find('td')
#                 if 모집요강_td:
#                     for tag in 모집요강_td.find_all(True):  # 모든 태그를 찾음
#                         if tag.name == "br":
#                             continue  # <br> 태그는 유지
#                         tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

#                     모집요강 = str(모집요강_td)  # <td> 내용만 문자열로 변환
#                 else:
#                     모집요강 = "정보 없음"  # <td>가 없을 경우 기본값 설정

#                 print(f"모집요강: {모집요강}")
                
#                 # 자격면허 추출 (세 번째 div[@class='careers-table center'] 안의 두 번째 td)
#                 자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
#                 print(f"자격면허: {자격면허}")

#                 # 연락처 추출 (전화번호 열에서 가져오기)
#                 연락처 = driver.find_element(By.XPATH, "(//div[@class='careers-table charge center']//tbody//tr//td[2])").text
#                 print(f"연락처: {연락처}")
                
#                 # 리스트에 데이터 추가
#                 기업명_list.append(기업명)
#                 업종_list.append(업종)
#                 기업규모_list.append(기업규모)
#                 설립년도_list.append(설립년도)
#                 연매출액_list.append(연매출액)
#                 홈페이지_list.append(홈페이지 if 홈페이지 else "없음")
#                 근로자수_list.append(근로자수)
#                 채용공고명_list.append(채용공고명)
#                 경력_list.append(경력)
#                 학력_list.append(학력)
#                 지역_list.append(지역)
#                 임금_list.append(임금)
#                 고용형태_list.append(고용형태)
#                 근무형태_list.append(근무형태)
#                 모집요강_list.append(모집요강)
#                 자격면허_list.append(자격면허)  # 자격면허 데이터 추가
#                 연락처_list.append(연락처)  # 연락처 데이터 추가

#                 data_counter += 1  # 데이터 개수 증가
                
#                 # 데이터가 5개 모일 때마다 저장
#                 if data_counter % 5 == 0:
#                     print(f"Saving data to CSV after collecting {data_counter} entries.")
#                     make_df(f"_{save_counter}")
#                     save_counter += 1  # 저장 파일 번호 증가
                
#                 i += 1  # 다음 링크로 이동

#                 # 페이지 이동 후 다시 rows 업데이트
#                 driver.back()
#                 time.sleep(2)
#                 rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
            
#             except UnexpectedAlertPresentException:
#                 alert = driver.switch_to.alert
#                 alert.accept()
#                 print(f"Skipped closed job posting: {link_url}")
#                 i += 1  # 다음 링크로 이동
#                 continue
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
#             rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
    
#     current_page += 1  # 다음 페이지로 이동
#     print(f"Moving to page {current_page}")

# # 최종 저장
# make_df(f"워크넷_final_{save_counter}")

# # 드라이버 종료
# print("Closing the web driver.")
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

# # 데이터 저장용 리스트
# 기업명_list = []
# 업종_list = []
# 기업규모_list = []
# 설립년도_list = []
# 연매출액_list = []
# 홈페이지_list = []
# 근로자수_list = []

# 채용공고명_list = []
# 경력_list = []
# 학력_list = []
# 지역_list = []
# 임금_list = []
# 고용형태_list = []
# 근무형태_list = []
# 모집요강_list = []
# 자격면허_list = []  # 자격면허 리스트 추가
# 링크_list = []  # 링크 리스트 추가
# 등록일_list = []  # 등록일 리스트 추가
# 마감일_list = []  # 마감일 리스트 추가

# # 페이지 수 설정
# current_page = 1
# pages = 20

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '업종': 업종_list,
#         '기업규모': 기업규모_list,
#         '설립년도': 설립년도_list,
#         '연매출액': 연매출액_list,
#         '홈페이지': 홈페이지_list,
#         '근로자수': 근로자수_list,
#         '채용공고명': 채용공고명_list,
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '지역': 지역_list,
#         '임금': 임금_list,
#         '고용형태': 고용형태_list,
#         '근무형태': 근무형태_list,
#         '모집요강': 모집요강_list,
#         '자격면허': 자격면허_list,  # 자격면허 추가
#         '링크': 링크_list,  # 링크 열 추가
#         '등록일': 등록일_list,  # 등록일 열 추가
#         '마감일': 마감일_list  # 마감일 열 추가
#     })
#     save_path = os.path.join(save_dir, f"워크넷1_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 크롤링 실행
# data_counter = 0  # 수집된 데이터 개수 카운터
# save_counter = 1  # 저장 파일 번호 카운터

# while current_page <= pages:
#     url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=2&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
#     driver.get(url)
#     time.sleep(3)
    
#     # 공고 리스트 추출
#     rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#     num_links = len(rows)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크 추출
#             link = WebDriverWait(rows[i], 10).until(
#                 EC.presence_of_element_located((By.XPATH, ".//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]"))
#             )
#             link_url = link.get_attribute('href')

#             # 등록일 추출
#             등록일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(text(), '등록')]").text.split()[0]

#             # 마감일 추출
#             try:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//span[starts-with(@id, 'spanCloseDt')]").text.strip()
#             except NoSuchElementException:
#                 마감일 = rows[i].find_element(By.XPATH, ".//div[@class='cp-info']//p[contains(@class, 'dday')]").text.strip()

#             # 링크 데이터 추가
#             링크_list.append(link_url)
#             등록일_list.append(등록일)
#             마감일_list.append(마감일)
            
#             # 상세 페이지로 이동
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기업명, 업종, 기업규모 등 기본 정보 추출
#             기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))).text
#             업종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
#             기업규모 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='기업규모']]/div").text
#             설립년도 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='설립년도']]/div").text
#             연매출액 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='연매출액']]/div").text
#             홈페이지 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='홈페이지']]/div").text
#             근로자수 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='근로자수']]/div").text
            
#             # 채용공고명, 경력, 학력 등 공고 정보 추출
#             채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
#             경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
#             학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
#             지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
#             임금 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
#             고용형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='고용형태']]/span").text
#             근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text
            
#             # 모집요강 추출 및 <br> 태그 유지
#             모집요강_html = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerHTML")
#             soup = BeautifulSoup(모집요강_html, 'html.parser')

#             # <td> 태그 내의 텍스트만 추출하고 <br> 태그는 유지
#             모집요강_td = soup.find('td')
#             if 모집요강_td:
#                 for tag in 모집요강_td.find_all(True):  # 모든 태그를 찾음
#                     if tag.name == "br":
#                         continue  # <br> 태그는 유지
#                     tag.unwrap()  # 나머지 태그는 제거하고 내용만 남김

#                 모집요강 = str(모집요강_td)  # <td> 내용만 문자열로 변환
#             else:
#                 모집요강 = "정보 없음"  # <td>가 없을 경우 기본값 설정
            
#             # 자격면허 추출 (세 번째 div[@class='careers-table center'] 안의 두 번째 td)
#             자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
            
#             # 리스트에 데이터 추가
#             기업명_list.append(기업명)
#             업종_list.append(업종)
#             기업규모_list.append(기업규모)
#             설립년도_list.append(설립년도)
#             연매출액_list.append(연매출액)
#             홈페이지_list.append(홈페이지 if 홈페이지 else "없음")
#             근로자수_list.append(근로자수)
#             채용공고명_list.append(채용공고명)
#             경력_list.append(경력)
#             학력_list.append(학력)
#             지역_list.append(지역)
#             임금_list.append(임금)
#             고용형태_list.append(고용형태)
#             근무형태_list.append(근무형태)
#             모집요강_list.append(모집요강)
#             자격면허_list.append(자격면허)  # 자격면허 데이터 추가

#             data_counter += 1  # 데이터 개수 증가
            
#             # 데이터가 5개 모일 때마다 저장
#             if data_counter % 5 == 0:
#                 make_df(f"_{save_counter}")
#                 save_counter += 1  # 저장 파일 번호 증가
            
#             i += 1  # 다음 링크로 이동

#             # 페이지 이동 후 다시 rows 업데이트
#             driver.back()
#             time.sleep(2)
#             rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
#             rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'list')]")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
    
#     current_page += 1  # 다음 페이지로 이동

# # 최종 저장
# make_df(f"워크넷_final_{save_counter}")

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
# 기업명_list = []
# 업종_list = []
# 기업규모_list = []
# 설립년도_list = []
# 연매출액_list = []
# 홈페이지_list = []
# 근로자수_list = []

# 채용공고명_list = []
# 경력_list = []
# 학력_list = []
# 지역_list = []
# 임금_list = []
# 고용형태_list = []
# 근무형태_list = []
# 모집요강_list = []
# 자격면허_list = []  # 자격면허 리스트 추가

# # 페이지 수 설정
# current_page = 1
# pages = 20

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '업종': 업종_list,
#         '기업규모': 기업규모_list,
#         '설립년도': 설립년도_list,
#         '연매출액': 연매출액_list,
#         '홈페이지': 홈페이지_list,
#         '근로자수': 근로자수_list,
#         '채용공고명': 채용공고명_list,
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '지역': 지역_list,
#         '임금': 임금_list,
#         '고용형태': 고용형태_list,
#         '근무형태': 근무형태_list,
#         '모집요강': 모집요강_list,
#         '자격면허': 자격면허_list  # 자격면허 추가
#     })
#     save_path = os.path.join(save_dir, f"워크넷_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 크롤링 실행
# data_counter = 0  # 수집된 데이터 개수 카운터
# save_counter = 1  # 저장 파일 번호 카운터

# while current_page <= pages:
#     url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=2&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
#     driver.get(url)
#     time.sleep(3)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.XPATH, "//div[@class='cp-info-in']//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]")
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.XPATH, "//div[@class='cp-info-in']//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]")
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기업명, 업종, 기업규모 등 기본 정보 추출
#             기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))).text
#             업종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
#             기업규모 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='기업규모']]/div").text
#             설립년도 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='설립년도']]/div").text
#             연매출액 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='연매출액']]/div").text
#             홈페이지 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='홈페이지']]/div").text
#             근로자수 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='근로자수']]/div").text
            
#             # 채용공고명, 경력, 학력 등 공고 정보 추출
#             채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
#             경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
#             학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
#             지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
#             임금 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
#             고용형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='고용형태']]/span").text
#             근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text
            
#             # 모집요강 추출
#             모집요강 = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerText")
            
#             # 자격면허 추출 (세 번째 div[@class='careers-table center'] 안의 두 번째 td)
#             자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
            
#             # 리스트에 데이터 추가
#             기업명_list.append(기업명)
#             업종_list.append(업종)
#             기업규모_list.append(기업규모)
#             설립년도_list.append(설립년도)
#             연매출액_list.append(연매출액)
#             홈페이지_list.append(홈페이지 if 홈페이지 else "없음")
#             근로자수_list.append(근로자수)
#             채용공고명_list.append(채용공고명)
#             경력_list.append(경력)
#             학력_list.append(학력)
#             지역_list.append(지역)
#             임금_list.append(임금)
#             고용형태_list.append(고용형태)
#             근무형태_list.append(근무형태)
#             모집요강_list.append(모집요강)
#             자격면허_list.append(자격면허)  # 자격면허 데이터 추가

#             data_counter += 1  # 데이터 개수 증가
            
#             # 데이터가 5개 모일 때마다 저장
#             if data_counter % 5 == 0:
#                 make_df(f"_{save_counter}")
#                 save_counter += 1  # 저장 파일 번호 증가
            
#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(2)
    
#     current_page += 1  # 다음 페이지로 이동

# # 최종 저장
# make_df(f"워크넷_final_{save_counter}")

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
# 기업명_list = []
# 업종_list = []
# 기업규모_list = []
# 설립년도_list = []
# 연매출액_list = []
# 홈페이지_list = []
# 근로자수_list = []

# 채용공고명_list = []
# 경력_list = []
# 학력_list = []
# 지역_list = []
# 임금_list = []
# 고용형태_list = []
# 근무형태_list = []
# 모집요강_list = []
# 자격면허_list = []  # 자격면허 리스트 추가
# 등록일_list = []  # 등록일 리스트 추가
# 마감일_list = []  # 마감일 리스트 추가
# 링크_list = []  # 상세보기 링크 리스트 추가

# # 페이지 수 설정
# current_page = 1
# pages = 30

# # 저장 경로 설정
# save_dir = "data"
# if not os.path.exists(save_dir):
#     os.makedirs(save_dir)

# def make_df(num):
#     df = pd.DataFrame({
#         '기업명': 기업명_list,
#         '업종': 업종_list,
#         '기업규모': 기업규모_list,
#         '설립년도': 설립년도_list,
#         '연매출액': 연매출액_list,
#         '홈페이지': 홈페이지_list,
#         '근로자수': 근로자수_list,
#         '채용공고명': 채용공고명_list,
#         '경력': 경력_list,
#         '학력': 학력_list,
#         '지역': 지역_list,
#         '임금': 임금_list,
#         '고용형태': 고용형태_list,
#         '근무형태': 근무형태_list,
#         '모집요강': 모집요강_list,
#         '자격면허': 자격면허_list,  # 자격면허 추가
#         '등록일': 등록일_list,  # 등록일 추가
#         '마감일': 마감일_list,  # 마감일 추가
#         '상세보기 링크': 링크_list  # 상세보기 링크 추가
#     })
#     save_path = os.path.join(save_dir, f"워크넷1_{num}.csv")
#     df.to_csv(save_path, index=False, encoding='utf-8-sig')

# # 크롤링 실행
# data_counter = 0  # 수집된 데이터 개수 카운터
# save_counter = 1  # 저장 파일 번호 카운터

# while current_page <= pages:
#     url = f"https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&templateInfo=&shsyWorkSecd=&rot2WorkYn=&payGbn=&resultCnt=10&keywordJobCont=N&cert=&cloDateStdt=&moreCon=&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&maxPay=&keywordStaAreaNm=N&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=&region=26000&infaYn=&resultCntInfo=10&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo={current_page}&indArea=&careerTypes=&searchOn=Y&tlmgYn=&subEmpHopeYn=&academicGbn=&templateDepthNoInfo=&foriegn=&mealOfferClcd=&station=&moerButtonYn=N&holidayGbn=&srcKeyword=&enterPriseGbn=all&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&isEmptyHeader=&depth2SelCode=&_csrf=4d328f77-8efa-4d76-acac-ae15e7535868&keywordBusiNm=N&preferentialGbn=&rot3WorkYn=&pfMatterPreferential=B&regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={current_page}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL"
#     driver.get(url)
#     time.sleep(3)
    
#     # 공고 리스트 추출
#     links = driver.find_elements(By.XPATH, "//div[@class='cp-info-in']//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]")
#     num_links = len(links)
    
#     i = 0
#     while i < num_links:
#         try:
#             # 링크를 다시 찾아서 StaleElementReferenceException 방지
#             links = driver.find_elements(By.XPATH, "//div[@class='cp-info-in']//a[contains(@href, '/empInfo/empInfoSrch/detail/empDetailAuthView.do')]")
            
#             if i >= len(links):
#                 print(f"Skipping index {i} as it exceeds the length of available links.")
#                 break
            
#             link = links[i]
#             link_url = link.get_attribute('href')
#             driver.get(link_url)
#             time.sleep(3)  # 페이지 로드 시간을 더 길게 설정
            
#             # Explicit wait for the element to be visible
#             wait = WebDriverWait(driver, 15)  # 대기 시간을 늘림
            
#             # 기업명, 업종, 기업규모 등 기본 정보 추출
#             기업명 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='info']//li[strong[text()='기업명']]/div"))).text
#             업종 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='업종']]/div").text
#             기업규모 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='기업규모']]/div").text
#             설립년도 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='설립년도']]/div").text
#             연매출액 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='연매출액']]/div").text
#             홈페이지 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='홈페이지']]/div").text
#             근로자수 = driver.find_element(By.XPATH, "//div[@class='info']//li[strong[text()='근로자수']]/div").text
            
#             # 채용공고명, 경력, 학력 등 공고 정보 추출
#             채용공고명 = driver.find_element(By.XPATH, "//div[@class='tit-area']/p[@class='tit']").text
#             경력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='경력']]/span").text
#             학력 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='학력']]/span").text
#             지역 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='지역']]/span").text
#             임금 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='임금']]/span").text
#             고용형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='고용형태']]/span").text
#             근무형태 = driver.find_element(By.XPATH, "//div[@class='cont']//li[strong[text()='근무형태']]/span").text
            
#             # 모집요강 추출
#             모집요강 = driver.find_element(By.XPATH, "//div[@class='careers-table']").get_attribute("innerText")
            
#             # 자격면허 추출 (세 번째 div[@class='careers-table center'] 안의 두 번째 td)
#             자격면허 = driver.find_element(By.XPATH, "(//div[@class='careers-table center'])[3]//td[2]").text
            
#             # 등록일 및 마감일 추출
#             등록일 = driver.find_element(By.XPATH, "//div[@class='cp-info']/p[2]").text.split()[0]  # 등록일 추출
#             마감일 = driver.find_element(By.XPATH, "//p[@id='dDayInfo0']").text  # 마감일 추출

#             # 링크 추가
#             링크_list.append(link_url)
            
#             # 리스트에 데이터 추가
#             기업명_list.append(기업명)
#             업종_list.append(업종)
#             기업규모_list.append(기업규모)
#             설립년도_list.append(설립년도)
#             연매출액_list.append(연매출액)
#             홈페이지_list.append(홈페이지 if 홈페이지 else "없음")
#             근로자수_list.append(근로자수)
#             채용공고명_list.append(채용공고명)
#             경력_list.append(경력)
#             학력_list.append(학력)
#             지역_list.append(지역)
#             임금_list.append(임금)
#             고용형태_list.append(고용형태)
#             근무형태_list.append(근무형태)
#             모집요강_list.append(모집요강)
#             자격면허_list.append(자격면허)  # 자격면허 데이터 추가
#             등록일_list.append(등록일)  # 등록일 데이터 추가
#             마감일_list.append(마감일)  # 마감일 데이터 추가
#             링크_list.append(link_url)  # 링크 데이터 추가

#             data_counter += 1  # 데이터 개수 증가
            
#             # 데이터가 5개 모일 때마다 저장
#             if data_counter % 5 == 0:
#                 make_df(f"part_{save_counter}")
#                 save_counter += 1  # 저장 파일 번호 증가
            
#             i += 1  # 다음 링크로 이동
        
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Element not found or timeout. Skipping: {link_url}")
#             i += 1  # 다음 링크로 이동
#             continue
#         except StaleElementReferenceException:
#             print(f"StaleElementReferenceException 발생. 다시 시도 중: {link_url}")
#             continue
#         except Exception as e:
#             print(f"Error: {e}")
#             i += 1  # 오류가 발생해도 다음 링크로 이동
#             continue
        
#         driver.back()
#         time.sleep(2)
    
#     current_page += 1  # 다음 페이지로 이동

# # 최종 저장
# make_df(f"워크넷_final_{save_counter}")

# # 드라이버 종료
# driver.quit()
