import pandas as pd
from bs4 import BeautifulSoup
import re

# 파일 경로 지정
file1_path = "./1.1 crawling_education/data/부산일자리정보망_ppp.csv"
file2_path = "./1.1 crawling_education/data/부산평생교육정보망_ppp.csv"

# CSV 파일 불러오기
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# 공통 열 이름 설정
columns = [
    'source', 'title',  'organization', 'application_start', 'application_end',
    'progress_start', 'progress_end', 'situation', 'apply', 'link', 'phone', 'manager', 'charge',
    'email', 'view_details_link', 'details', 'instructor', 'tuition', 'teaching_method', 'capacity',
    'place',  'support','views'
]

# 열이 없는 경우 공백으로 추가
for df in [df1, df2]:
    for col in columns:
        if col not in df.columns:
            df[col] = ""

# 두 데이터프레임 병합
merged_df = pd.concat([df1[columns], df2[columns]], ignore_index=True)

# region.csv 파일 불러오기
region_file_path = './1.1 crawling_education/data_merge/region.csv'
region_df = pd.read_csv(region_file_path)

# region 데이터프레임을 딕셔너리로 변환 (subregion -> id 매핑)
region_dict = dict(zip(region_df['subregion'], region_df['id']))

# organization 열에서 subregion을 찾아서 region_id로 변환
def get_region_id(organization):
    for subregion in region_dict.keys():
        if subregion in organization:
            return region_dict[subregion]
    return region_dict['전체']  # 해당되는 subregion이 없을 경우 '전체'로 설정

# region_id 열 추가
merged_df['region_id'] = merged_df['organization'].apply(get_region_id)

# preference_id 열을 빈칸으로 추가
merged_df['preference_id'] = ""  # 또는 None

# id 열 추가 (1부터 시작)
merged_df['id'] = pd.Series(range(1, len(merged_df) + 1))

# id 열을 맨 앞에 배치
columns_order = ['id'] + [col for col in merged_df.columns if col != 'id']

# region_id 열을 오른쪽 끝으로 이동
columns_order = [col for col in columns_order if col != 'region_id'] + ['region_id']
merged_df = merged_df[columns_order]

# 병합된 데이터 확인
print(merged_df[['id', 'organization', 'preference_id', 'region_id']].head())

# 인라인 스타일 및 불필요한 태그를 제거하는 함수 정의
from bs4 import BeautifulSoup
import pandas as pd
import re

def clean_large_html_data(html_content):
    if pd.isna(html_content):  # NaN 값 처리
        return ""

    # 1. HTML 주석 제거 (<!-- -->)
    html_content = re.sub(r'<!--[\s\S]*?-->', '', html_content, flags=re.DOTALL)  # HTML 주석 제거

    # BeautifulSoup을 이용하여 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 2. 잘못된 속성 값 제거 (예: "noto=\"\"", "맑은=\"\"" 등)
    for tag in soup.find_all(True):
        # 모든 잘못된 속성 제거 (정규식으로 잘못된 속성을 제거)
        for attr in list(tag.attrs):
            if re.search(r'\"[a-zA-Z가-힣]*=\"\"', str(tag.attrs[attr])):
                del tag.attrs[attr]

    # 3. 인라인 스타일 제거
    for tag in soup.find_all(True):  # 모든 태그에서
        if 'style' in tag.attrs:  # 'style' 속성이 있으면 제거
            del tag.attrs['style']

    # 4. 빈 태그 제거 (내용이 없는 태그)
    for tag in soup.find_all(['div', 'span']):  # 빈 p, div, span 태그 제거
        if not tag.get_text(strip=True):
            tag.decompose()  # 태그 삭제

    # 5. 중복된 태그 간소화 (예: <b><span></span></b>)
    for tag in soup.find_all(['b', 'span']):  # 중첩된 태그 간소화
        if tag.find(['b', 'span']):
            tag.unwrap()

    # 6. img 태그 삭제 (원치 않는 이미지 제거)
    for img_tag in soup.find_all('img'):
        img_tag.decompose()  # img 태그 제거

    # 변경된 HTML을 문자열로 반환
    return str(soup)

# def clean_large_html_data(html_content):
#     if pd.isna(html_content):  # NaN 값 처리
#         return ""

#     # 영어, 숫자, 특수문자 제거
#     html_content = re.sub(r'[A-Za-z0-9]', '', html_content)  # 영어와 숫자 제거
#     html_content = re.sub(r'[^\w\s]', '', html_content)  # 특수문자 제거 (단어와 공백을 제외한 모든 문자)
    
#     if len(html_content) > 5000:  # 글자 수가 5000자를 넘는 경우에만 처리
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # 1. &nbsp;와 <br> 태그를 제외한 모든 태그 제거
#         for tag in soup.find_all(True):
#             if tag.name not in ['nbsp', 'br']:  # &nbsp;와 br만 남기고 나머지 태그 제거
#                 tag.unwrap()

#         # 변경된 HTML을 문자열로 반환
#         return str(soup)
    
#     return html_content  # 5000자 이하일 경우 원본 유지

#####완전 기존##############
# def clean_large_html_data(html_content):
#     if pd.isna(html_content):  # NaN 값 처리
#         return ""
    
#     if len(html_content) > 1000:  # 글자 수가 5000자를 넘는 경우에만 처리
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # 1. 인라인 스타일 제거
#         for tag in soup.find_all(True):
#             if 'style' in tag.attrs:
#                 del tag.attrs['style']

#         # 2. 빈 태그 제거
#         for tag in soup.find_all(['p', 'div', 'span']):
#             if not tag.get_text(strip=True):  # 내용이 없는 경우
#                 tag.decompose()  # 태그 삭제

#         # 3. 잘못된 속성 제거 (불필요한 속성들 처리)
#         for tag in soup.find_all(True):  # 모든 태그 탐색
#             attrs_to_remove = [attr for attr in tag.attrs if re.search(r'["\'\=\(\)]', str(tag.attrs[attr]))]
#             for attr in attrs_to_remove:
#                 del tag.attrs[attr]

#         # 4. 중첩된 불필요한 태그 제거 (예: <span><div> -> <div>)
#         for span in soup.find_all('span'):
#             if span.find('div'):
#                 span.unwrap()
        
#         # 변경된 HTML을 문자열로 반환
#         return str(soup)
    
#     return html_content  # 5000자 이하일 경우 원본 유지

# def clean_large_html_data(html_content):
#     if pd.isna(html_content):  # NaN 값 처리
#         return ""

#     # 무의미한 긴 패턴 필터링 (예: 500자 이상의 긴 문자열을 무의미한 값으로 간주)
#     if len(html_content) > 1500:
#         # 반복적인 문자 패턴 제거
#         invalid_pattern = re.compile(r'([A-Za-z0-9]{3,})\1{3,}')  # 동일한 패턴이 3회 이상 반복
#         if invalid_pattern.search(html_content):
#             return ""

#     # HTML 처리: 글자 수가 5000자를 넘는 경우에만 처리
#     if len(html_content) > 1500:
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # 1. 인라인 스타일 제거
#         for tag in soup.find_all(True):
#             if 'style' in tag.attrs:
#                 del tag.attrs['style']

#         # 2. 빈 태그 제거
#         for tag in soup.find_all(['p', 'div', 'span']):
#             if not tag.get_text(strip=True):  # 내용이 없는 경우
#                 tag.decompose()  # 태그 삭제

#         # 3. 잘못된 속성 제거 (불필요한 속성들 처리)
#         for tag in soup.find_all(True):  # 모든 태그 탐색
#             attrs_to_remove = [attr for attr in tag.attrs if re.search(r'["\'\=\(\)]', str(tag.attrs[attr]))]
#             for attr in attrs_to_remove:
#                 del tag.attrs[attr]

#         # 4. 중첩된 불필요한 태그 제거 (예: <span><div> -> <div>)
#         for span in soup.find_all('span'):
#             if span.find('div'):
#                 span.unwrap()

#         # 변경된 HTML을 문자열로 반환
#         return str(soup)
    
#     # 특수 문자나 무의미한 패턴 제거 (5000자 이하일 경우에도 적용)
#     html_content = re.sub(r'[^\w\s]', '', html_content)  # 특수문자 제거
#     html_content = re.sub(r'\s+', ' ', html_content).strip()  # 공백 정리
    
#     return html_content  # 5000자 이하일 경우 원본 유지

# details 열에서 5000자를 넘는 경우 HTML 데이터를 정리
merged_df['details'] = merged_df['details'].apply(clean_large_html_data)

# 병합된 데이터 CSV로 저장
merged_df.to_csv("./1.1 crawling_education/data/education_merged_data(1022).csv", index=False, encoding='utf-8-sig')

print("데이터 병합 및 저장 완료!")



# import pandas as pd

# # 파일 경로 지정
# file1_path = "./1.1 crawling_education/data/부산일자리정보망_pp.csv"
# file2_path = "./1.1 crawling_education/data/부산평생교육정보망_pp.csv"

# # CSV 파일 불러오기
# df1 = pd.read_csv(file1_path)
# df2 = pd.read_csv(file2_path)

# # 공통 열 이름 설정
# columns = [
#     'source', 'title',  'organization', 'application_start', 'application_end',
#     'progress_start', 'progress_end', 'situation', 'apply', 'link', 'phone', 'manager', 'charge',
#     'email', 'view_details_link', 'details', 'instructor', 'tuition', 'teaching_method', 'capacity',
#     'place',  'support'
# ]

# # 열이 없는 경우 공백으로 추가
# for df in [df1, df2]:
#     for col in columns:
#         if col not in df.columns:
#             df[col] = ""

# # 두 데이터프레임 병합
# merged_df = pd.concat([df1[columns], df2[columns]], ignore_index=True)

# # region.csv 파일 불러오기
# region_file_path = './1.1 crawling_education/data_merge/region.csv'
# region_df = pd.read_csv(region_file_path)

# # region 데이터프레임을 딕셔너리로 변환 (subregion -> id 매핑)
# region_dict = dict(zip(region_df['subregion'], region_df['id']))

# # organization 열에서 subregion을 찾아서 region_id로 변환
# def get_region_id(organization):
#     for subregion in region_dict.keys():
#         if subregion in organization:
#             return region_dict[subregion]
#     return region_dict['전체']  # 해당되는 subregion이 없을 경우 '전체'로 설정

# # region_id 열 추가
# merged_df['region_id'] = merged_df['organization'].apply(get_region_id)

# # preference_id 열을 빈칸으로 추가
# merged_df['preference_id'] = ""  # 또는 None

# # region_id 열을 오른쪽 끝으로 이동
# columns_order = [col for col in merged_df.columns if col != 'region_id'] + ['region_id']
# merged_df = merged_df[columns_order]

# # 병합된 데이터 확인
# print(merged_df[['organization', 'preference_id', 'region_id']].head())

# # 병합된 데이터 CSV로 저장
# merged_df.to_csv("./1.1 crawling_education/data/education_merged_data(0910).csv", index=False, encoding='utf-8-sig')

# print("데이터 병합 및 저장 완료!")

# import pandas as pd

# # 파일 경로 지정
# file1_path = "./1.1 crawling_education/data/부산일자리정보망_pp.csv"
# file2_path = "./1.1 crawling_education/data/부산평생교육정보망_pp.csv"

# # CSV 파일 불러오기
# df1 = pd.read_csv(file1_path)
# df2 = pd.read_csv(file2_path)

# # 공통 열 이름 설정
# columns = [
#     'source', 'title',  'organization', 'application_start', 'application_end',
#     'progress_start', 'progress_end', 'situation', 'apply', 'link', 'phone', 'manager', 'charge',
#     'email', 'view_details_link', 'details', 'instructor', 'tuition', 'teaching_method', 'capacity',
#     'place',  'support'
# ]

# # 열이 없는 경우 공백으로 추가
# for df in [df1, df2]:
#     for col in columns:
#         if col not in df.columns:
#             df[col] = ""

# # 두 데이터프레임 병합
# merged_df = pd.concat([df1[columns], df2[columns]], ignore_index=True)

# # 병합된 데이터 확인
# print(merged_df.head())

# # 병합된 데이터 CSV로 저장
# merged_df.to_csv("./1.1 crawling_education/data/education_merged_data(0909).csv", index=False, encoding='utf-8-sig')

# print("데이터 병합 및 저장 완료!")
