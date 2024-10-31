import pandas as pd
import re
import numpy as np

# 파일 경로 설정
job_file_path = './1. crawling/crawling_data_merged/job_merged_file(1030).xlsx'
column_translation_path = './1. crawling/preprocessing/열이름변환.xlsx'
region_data_path = './1. crawling/preprocessing/region.csv'  # 지역 데이터 파일 경로

# 엑셀 파일 로드
job_df = pd.read_excel(job_file_path)
column_translation_df = pd.read_excel(column_translation_path)
region_data = pd.read_csv(region_data_path)

# 열 이름 변환 정보를 딕셔너리로 변환
column_translation_dict = pd.Series(column_translation_df['변환후'].values, index=column_translation_df['변환전']).to_dict()

# 근무유형을 근무형태에 데이터를 합치기 (근무형태에 근무유형을 덧붙임)
job_df['근무형태'] = job_df['근무형태'].fillna('') + ' ' + job_df['근무유형'].fillna('')

# 기존의 '근무유형' 열 삭제
job_df = job_df.drop(columns=['근무유형'])

# 열 이름 영어로 변환
job_df = job_df.rename(columns=column_translation_dict)

# 지역명 리스트
regions = [
    "기장군", "동래구", "사상구", "수영구", "중구", "강서구", "남구", 
    "부산진구", "사하구", "연제구", "해운대구", "금정구", "동구", 
    "북구", "서구", "영도구"
]

# 'title' 열을 처리하기 전에 NaN 값을 빈 문자열로 대체
job_df['title'] = job_df['title'].fillna('')

# title에서 대괄호와 그 안의 내용, 소괄호 안의 지역명을 제거하고, ' - ' 뒤 내용 subtitle로 분리
def clean_title(title, regions):
    # 대괄호와 그 안의 내용 제거
    title = re.sub(r'\[.*?\]', '', title).strip()
    
    # 소괄호 안에 지역명이 포함된 경우 소괄호와 그 안의 내용 제거
    for region in regions:
        title = re.sub(r'\(.*?' + re.escape(region) + r'.*?\)', '', title).strip()
    
    # ' - '를 기준으로 분리
    if ' - ' in title:
        main_title, subtitle = title.split(' - ', 1)
    else:
        main_title = title
        subtitle = None
    
    return main_title, subtitle

# title 열을 처리하고 subtitle 열 추가
job_df[['title', 'subtitle']] = job_df.apply(lambda row: pd.Series(clean_title(row['title'], regions)), axis=1)

# subtitle 열을 title 옆으로 이동
columns = list(job_df.columns)
columns.insert(columns.index('title') + 1, columns.pop(columns.index('subtitle')))
job_df = job_df[columns]

# title과 link 내용 비교하여 중복되는 행 삭제
job_df = job_df.drop_duplicates(subset=['title', 'link'], keep='first')

# 'region_name'에서 부산 외의 특정 지역이 포함된 행 삭제
exclude_regions = ["서울", "인천", "광주", "대전", "울산", "세종", 
                   "경기", "강원", "충청", "전북", "전라", "경상", "제주", "경남"]

# 제외할 지역들이 포함된 행을 삭제
pattern = '|'.join(exclude_regions)
job_df = job_df[~job_df['region_name'].str.contains(pattern, na=False)]

# '마감' 텍스트 제거 함수
def remove_closing_text(date_value):
    if isinstance(date_value, str):
        # '마감' 텍스트 제거
        return re.sub(r'마감$', '', date_value).strip()
    return date_value

# 날짜 형식 변환 함수
def format_date(date_value):
    date_value = remove_closing_text(date_value)
    
    # 다양한 형식의 날짜를 처리하기 위한 패턴
    date_formats = ['%y/%m/%d', '%y.%m.%d', '%Y-%m-%d', '%Y.%m.%d']  # 여기에서 '%Y.%m.%d' 형식 추가
    
    for date_format in date_formats:
        try:
            # 날짜 형식을 2024-08-13 형식으로 통일
            return pd.to_datetime(date_value, format=date_format).strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # 날짜 형식이 맞지 않으면 원래 텍스트 반환
    return date_value

# signup_date와 due_date 열에서 날짜 형식 통일
job_df['signup_date'] = job_df['signup_date'].apply(format_date)
job_df['due_date'] = job_df['due_date'].apply(format_date)

# due_date 열에서 특정 값 변환
job_df['due_date'] = job_df['due_date'].replace(
    ['최대한 빨리', '정보 없음', '', re.compile(r'^[dD]-\d+$')], 
    '채용시까지',
    regex=True
)

job_df['due_date'] = job_df['due_date'].replace(
    [r'^[dD]-(\d+)$', 'D-DAY', ''], 
    '상시채용', 
    regex=True
)

# 'due_date' 열의 값 변환 (상시채용 -> 2999-12-31, 채용시까지 -> 9999-01-01)
job_df['due_date'] = job_df['due_date'].replace({'상시채용': '2999-12-31', '채용시까지': '9999-01-01'})

# 공란 (NaN) 값 변환
job_df['due_date'] = job_df['due_date'].replace('', np.nan)
job_df['due_date'] = job_df['due_date'].fillna('9999-01-01')  # 빈 값이 채용시까지로 표시되도록 통일

# details에서 스페이스바 여러 개를 한 개로 치환
def clean_spaces(text):
    if isinstance(text, str):
        return re.sub(r'\s+', ' ', text)
    return text

# 모든 열에 대해 문자열이 아닌 값에 대한 처리를 추가
job_df = job_df.applymap(lambda x: clean_spaces(x) if isinstance(x, str) else x)

# 중복 제거 후 id 값 초기화
job_df.reset_index(drop=True, inplace=True)
job_df['id'] = job_df.index + 1

# 새로운 열을 생성하여 preference_id 및 region_id를 저장
job_df['preference_id'] = None  # 필요에 따라 로직을 추가하여 할당
job_df['region_id'] = None

# region_id와 preference_id 열을 채우는 로직
for index, row in job_df.iterrows():
    # 매치가 발견되었는지를 확인하는 플래그
    match_found = False
    
    # 단계 1: 'region_name'을 'subregion'과 비교
    if pd.notna(row['region_name']):
        for i, reg_row in region_data.iterrows():
            if reg_row['subregion'] in row['region_name']:
                job_df.at[index, 'region_id'] = reg_row['id']
                match_found = True
                break

    # 단계 2: 'region_name'이 없을 경우, 'company'을 'subregion'과 비교
    if not match_found and pd.isna(row['region_name']):
        if pd.notna(row['company']):  # 'company'이 NaN이 아닌지 확인
            for i, reg_row in region_data.iterrows():
                if reg_row['subregion'] in row['company']:
                    job_df.at[index, 'region_id'] = reg_row['id']
                    match_found = True
                    break

    # 단계 3: 매치가 없을 경우, 'details'을 'subregion'과 비교
    if not match_found:
        if pd.notna(row['details']):  # 'details'이 NaN이 아닌지 확인
            for i, reg_row in region_data.iterrows():
                if reg_row['subregion'] in row['details']:
                    job_df.at[index, 'region_id'] = reg_row['id']
                    match_found = True
                    break
    
    # 매치가 안된 경우 region_id 1 부여
    if not match_found:
        job_df.at[index, 'region_id'] = 1

# 'preference_id' 열을 'region_id' 왼쪽에 한 번만 삽입
columns = list(job_df.columns)
preference_index = columns.index('region_id')
# 'preference_id'가 이미 존재하지 않으면 삽입
if 'preference_id' not in columns:
    columns.insert(preference_index, 'preference_id')
job_df = job_df[columns]

# 'source'가 '장노년일자리지원센터'이고 'region_name'이 비어있는 경우, 'region_id' 값을 사용하여 'region_name'을 채워줌
region_id_to_subregion = {
    1: "전체", 2: "기장군", 3: "동래구", 4: "사상구", 5: "수영구", 6: "중구",
    7: "강서구", 8: "남구", 9: "부산진구", 10: "사하구", 11: "연제구", 12: "해운대구",
    13: "금정구", 14: "동구", 15: "북구", 16: "서구", 17: "영도구"
}

# 'region_name'이 비어 있고 'source'가 '장노년일자리지원센터'인 경우 'region_id'를 활용하여 'region_name' 채우기
for index, row in job_df.iterrows():
    if pd.isna(row['region_name']) and row['source'] == '장노년일자리지원센터':
        region_id = row['region_id']
        subregion = region_id_to_subregion.get(region_id, '전체')  # 기본값을 '전체'로 설정
        job_df.at[index, 'region_name'] = '부산 ' + subregion

# 최종 데이터를 CSV 파일로 저장
output_file_path_csv = './1. crawling/data/job_merged_file_surplus_region(1030).csv'
job_df.to_csv(output_file_path_csv, index=False, encoding='utf-8-sig')

# 최종 데이터를 JSON 파일로 저장
output_file_path_json = './1. crawling/data/job_merged_file_surplus_region(1030).json'
job_df.to_json(output_file_path_json, orient='records', force_ascii=False, indent=4)

print(f"최종 데이터가 {output_file_path_csv, output_file_path_json}에 저장되었습니다.")


# import pandas as pd
# import re
# import numpy as np

# # 파일 경로 설정
# job_file_path = './1.crawling/crawling_data_merged/job_merged_file(0920).xlsx'
# column_translation_path = './1.crawling/preprocessing/열이름변환.xlsx'
# region_data_path = './1.crawling/preprocessing/region.csv'  # 지역 데이터 파일 경로

# # 엑셀 파일 로드
# job_df = pd.read_excel(job_file_path)
# column_translation_df = pd.read_excel(column_translation_path)
# region_data = pd.read_csv(region_data_path)

# # 열 이름 변환 정보를 딕셔너리로 변환
# column_translation_dict = pd.Series(column_translation_df['변환후'].values, index=column_translation_df['변환전']).to_dict()

# # 근무유형을 근무형태에 데이터를 합치기 (근무형태에 근무유형을 덧붙임)
# job_df['근무형태'] = job_df['근무형태'].fillna('') + ' ' + job_df['근무유형'].fillna('')

# # 기존의 '근무유형' 열 삭제
# job_df = job_df.drop(columns=['근무유형'])

# # 열 이름 영어로 변환
# job_df = job_df.rename(columns=column_translation_dict)

# # 지역명 리스트
# regions = [
#     "기장군", "동래구", "사상구", "수영구", "중구", "강서구", "남구", 
#     "부산진구", "사하구", "연제구", "해운대구", "금정구", "동구", 
#     "북구", "서구", "영도구"
# ]

# # title에서 대괄호와 그 안의 내용, 소괄호 안의 지역명을 제거하고, ' - ' 뒤 내용 subtitle로 분리
# def clean_title(title, regions):
#     # 대괄호와 그 안의 내용 제거
#     title = re.sub(r'\[.*?\]', '', title).strip()
    
#     # 소괄호 안에 지역명이 포함된 경우 소괄호와 그 안의 내용 제거
#     for region in regions:
#         title = re.sub(r'\(.*?' + re.escape(region) + r'.*?\)', '', title).strip()
    
#     # ' - '를 기준으로 분리
#     if ' - ' in title:
#         main_title, subtitle = title.split(' - ', 1)
#     else:
#         main_title = title
#         subtitle = None
    
#     return main_title, subtitle

# # title 열을 처리하고 subtitle 열 추가
# job_df[['title', 'subtitle']] = job_df.apply(lambda row: pd.Series(clean_title(row['title'], regions)), axis=1)

# # subtitle 열을 title 옆으로 이동
# columns = list(job_df.columns)
# columns.insert(columns.index('title') + 1, columns.pop(columns.index('subtitle')))
# job_df = job_df[columns]

# # title과 link 내용 비교하여 중복되는 행 삭제
# job_df = job_df.drop_duplicates(subset=['title', 'link'], keep='first')

# # 'region_name'에서 부산 외의 특정 지역이 포함된 행 삭제
# exclude_regions = ["서울", "인천", "광주", "대전", "울산", "세종", 
#                    "경기", "강원", "충청", "전북", "전라", "경상", "제주", "경남"]

# # 제외할 지역들이 포함된 행을 삭제
# pattern = '|'.join(exclude_regions)
# job_df = job_df[~job_df['region_name'].str.contains(pattern, na=False)]

# # '마감' 텍스트 제거 함수
# def remove_closing_text(date_value):
#     if isinstance(date_value, str):
#         # '마감' 텍스트 제거
#         return re.sub(r'마감$', '', date_value).strip()
#     return date_value

# # 날짜 형식 변환 함수
# def format_date(date_value):
#     date_value = remove_closing_text(date_value)
    
#     # 다양한 형식의 날짜를 처리하기 위한 패턴
#     date_formats = ['%y/%m/%d', '%y.%m.%d', '%Y-%m-%d', '%Y.%m.%d']  # 여기에서 '%Y.%m.%d' 형식 추가
    
#     for date_format in date_formats:
#         try:
#             # 날짜 형식을 2024-08-13 형식으로 통일
#             return pd.to_datetime(date_value, format=date_format).strftime('%Y-%m-%d')
#         except ValueError:
#             continue
    
#     # 날짜 형식이 맞지 않으면 원래 텍스트 반환
#     return date_value

# # signup_date와 due_date 열에서 날짜 형식 통일
# job_df['signup_date'] = job_df['signup_date'].apply(format_date)
# job_df['due_date'] = job_df['due_date'].apply(format_date)

# # due_date 열에서 특정 값 변환
# job_df['due_date'] = job_df['due_date'].replace(['최대한 빨리', '정보 없음', ''], '채용시까지')

# # 'due_date' 열의 값 변환 (상시채용 -> 2999-12-31, 채용시까지 -> 9999-01-01)
# job_df['due_date'] = job_df['due_date'].replace({'상시채용': '2999-12-31', '채용시까지': '9999-01-01'})

# # 공란 (NaN) 값 변환
# job_df['due_date'] = job_df['due_date'].replace('', np.nan)
# job_df['due_date'] = job_df['due_date'].fillna('9999-01-01')  # 빈 값이 채용시까지로 표시되도록 통일

# # details에서 스페이스바 여러 개를 한 개로 치환
# def clean_spaces(text):
#     if isinstance(text, str):
#         return re.sub(r'\s+', ' ', text)
#     return text

# # 모든 열에 대해 공백을 제거하는 함수 적용
# job_df = job_df.applymap(lambda x: clean_spaces(x) if isinstance(x, str) else x)

# # 중복 제거 후 id 값 초기화
# job_df.reset_index(drop=True, inplace=True)
# job_df['id'] = job_df.index + 1

# # -----------------------------------------------------------------------
# # 새로운 preference_id 및 region_id 열 추가 로직 시작
# # -----------------------------------------------------------------------

# # 새로운 열을 생성하여 preference_id 및 region_id를 저장
# job_df['preference_id'] = None  # 필요에 따라 로직을 추가하여 할당
# job_df['region_id'] = None

# # region_id와 preference_id 열을 채우는 로직
# for index, row in job_df.iterrows():
#     # 매치가 발견되었는지를 확인하는 플래그
#     match_found = False
    
#     # 단계 1: 'region_name'을 'subregion'과 비교
#     if pd.notna(row['region_name']):
#         for i, reg_row in region_data.iterrows():
#             if reg_row['subregion'] in row['region_name']:
#                 job_df.at[index, 'region_id'] = reg_row['id']
#                 match_found = True
#                 break

#     # 단계 2: 'region_name'이 없을 경우, 'company'을 'subregion'과 비교
#     if not match_found and pd.isna(row['region_name']):
#         if pd.notna(row['company']):  # 'company'이 NaN이 아닌지 확인
#             for i, reg_row in region_data.iterrows():
#                 if reg_row['subregion'] in row['company']:
#                     job_df.at[index, 'region_id'] = reg_row['id']
#                     match_found = True
#                     break

#     # 단계 3: 매치가 없을 경우, 'details'을 'subregion'과 비교
#     if not match_found:
#         if pd.notna(row['details']):  # 'details'이 NaN이 아닌지 확인
#             for i, reg_row in region_data.iterrows():
#                 if reg_row['subregion'] in row['details']:
#                     job_df.at[index, 'region_id'] = reg_row['id']
#                     match_found = True
#                     break
    
#     # 매치가 안된 경우 region_id 1 부여
#     if not match_found:
#         job_df.at[index, 'region_id'] = 1

# # 'preference_id' 열을 'region_id' 왼쪽에 한 번만 삽입
# columns = list(job_df.columns)
# preference_index = columns.index('region_id')
# # 'preference_id'가 이미 존재하지 않으면 삽입
# if 'preference_id' not in columns:
#     columns.insert(preference_index, 'preference_id')
# job_df = job_df[columns]

# # 'source'가 '장노년일자리지원센터'이고 'region_name'이 비어있는 경우, 'region_id' 값을 사용하여 'region_name'을 채워줌
# region_id_to_subregion = {
#     1: "전체", 2: "기장군", 3: "동래구", 4: "사상구", 5: "수영구", 6: "중구",
#     7: "강서구", 8: "남구", 9: "부산진구", 10: "사하구", 11: "연제구", 12: "해운대구",
#     13: "금정구", 14: "동구", 15: "북구", 16: "서구", 17: "영도구"
# }

# # 'region_name'이 비어 있고 'source'가 '장노년일자리지원센터'인 경우 'region_id'를 활용하여 'region_name' 채우기
# for index, row in job_df.iterrows():
#     if pd.isna(row['region_name']) and row['source'] == '장노년일자리지원센터':
#         region_id = row['region_id']
#         subregion = region_id_to_subregion.get(region_id, '전체')  # 기본값을 '전체'로 설정
#         job_df.at[index, 'region_name'] = '부산 ' + subregion

# # 최종 데이터를 CSV 파일로 저장
# output_file_path_csv = './1.crawling/data/job_merged_file_surplus_region(0920).csv'
# job_df.to_csv(output_file_path_csv, index=False, encoding='utf-8-sig')

# # 최종 데이터를 JSON 파일로 저장
# output_file_path_json = './1.crawling/data/job_merged_file_surplus_region(0920).json'
# job_df.to_json(output_file_path_json, orient='records', force_ascii=False, indent=4)

# print(f"최종 데이터가 {output_file_path_csv,output_file_path_json}에 저장되었습니다.")


# import pandas as pd
# import re
# import numpy as np

# # 파일 경로 설정
# job_file_path = './crawling_data_merged/job_merged_file2.xlsx'
# column_translation_path = './preprocessing/열이름변환.xlsx'

# # 엑셀 파일 로드
# job_df = pd.read_excel(job_file_path)
# column_translation_df = pd.read_excel(column_translation_path)

# # 열 이름 변환 정보를 딕셔너리로 변환
# column_translation_dict = pd.Series(column_translation_df['변환후'].values, index=column_translation_df['변환전']).to_dict()

# # 근무유형을 근무형태에 데이터를 합치기 (근무형태에 근무유형을 덧붙임)
# job_df['근무형태'] = job_df['근무형태'].fillna('') + ' ' + job_df['근무유형'].fillna('')

# # 기존의 '근무유형' 열 삭제
# job_df = job_df.drop(columns=['근무유형'])

# # 열 이름 영어로 변환
# job_df = job_df.rename(columns=column_translation_dict)

# # 지역명 리스트
# regions = [
#     "기장군", "동래구", "사상구", "수영구", "중구", "강서구", "남구", 
#     "부산진구", "사하구", "연제구", "해운대구", "금정구", "동구", 
#     "북구", "서구", "영도구"
# ]

# # title에서 대괄호와 그 안의 내용, 소괄호 안의 지역명을 제거하고, ' - ' 뒤 내용 subtitle로 분리
# def clean_title(title, regions):
#     # 대괄호와 그 안의 내용 제거
#     title = re.sub(r'\[.*?\]', '', title).strip()
    
#     # 소괄호 안에 지역명이 포함된 경우 소괄호와 그 안의 내용 제거
#     for region in regions:
#         title = re.sub(r'\(.*?' + re.escape(region) + r'.*?\)', '', title).strip()
    
#     # ' - '를 기준으로 분리
#     if ' - ' in title:
#         main_title, subtitle = title.split(' - ', 1)
#     else:
#         main_title = title
#         subtitle = None
    
#     return main_title, subtitle

# # title 열을 처리하고 subtitle 열 추가
# job_df[['title', 'subtitle']] = job_df.apply(lambda row: pd.Series(clean_title(row['title'], regions)), axis=1)

# # subtitle 열을 title 옆으로 이동
# columns = list(job_df.columns)
# columns.insert(columns.index('title') + 1, columns.pop(columns.index('subtitle')))
# job_df = job_df[columns]

# # title과 link 내용 비교하여 중복되는 행 삭제
# job_df = job_df.drop_duplicates(subset=['title', 'link'], keep='first')

# # 'region_name'에서 부산 외의 특정 지역이 포함된 행 삭제
# exclude_regions = ["서울", "인천", "광주", "대전", "울산", "세종", 
#                    "경기", "강원", "충청", "전북", "전라", "경상", "제주", "경남"]

# # 제외할 지역들이 포함된 행을 삭제
# pattern = '|'.join(exclude_regions)
# job_df = job_df[~job_df['region_name'].str.contains(pattern, na=False)]

# # '마감' 텍스트 제거 함수
# def remove_closing_text(date_value):
#     if isinstance(date_value, str):
#         # '마감' 텍스트 제거
#         return re.sub(r'마감$', '', date_value).strip()
#     return date_value

# # 날짜 형식 변환 함수
# def format_date(date_value):
#     date_value = remove_closing_text(date_value)
    
#     # 다양한 형식의 날짜를 처리하기 위한 패턴
#     date_formats = ['%y/%m/%d', '%y.%m.%d', '%Y-%m-%d', '%Y.%m.%d']  # 여기에서 '%Y.%m.%d' 형식 추가
    
#     for date_format in date_formats:
#         try:
#             # 날짜 형식을 2024-08-13 형식으로 통일
#             return pd.to_datetime(date_value, format=date_format).strftime('%Y-%m-%d')
#         except ValueError:
#             continue
    
#     # 날짜 형식이 맞지 않으면 원래 텍스트 반환
#     return date_value

# # signup_date와 due_date 열에서 날짜 형식 통일
# job_df['signup_date'] = job_df['signup_date'].apply(format_date)
# job_df['due_date'] = job_df['due_date'].apply(format_date)

# # due_date 열에서 특정 값 변환
# job_df['due_date'] = job_df['due_date'].replace(['최대한 빨리', '정보 없음', ''], '채용시까지')

# # 'due_date' 열의 값 변환 (상시채용 -> 2999-12-31, 채용시까지 -> 9999-01-01)
# job_df['due_date'] = job_df['due_date'].replace({'상시채용': '2999-12-31', '채용시까지': '9999-01-01'})

# # 공란 (NaN) 값 변환
# job_df['due_date'] = job_df['due_date'].replace('', np.nan)
# job_df['due_date'] = job_df['due_date'].fillna('9999-01-01')  # 빈 값이 채용시까지로 표시되도록 통일

# # details에서 스페이스바 여러 개를 한 개로 치환
# def clean_spaces(text):
#     if isinstance(text, str):
#         return re.sub(r'\s+', ' ', text)
#     return text

# # 모든 열에 대해 공백을 제거하는 함수 적용
# job_df = job_df.applymap(lambda x: clean_spaces(x) if isinstance(x, str) else x)

# # 중복 제거 후 id 값 초기화
# job_df.reset_index(drop=True, inplace=True)
# job_df['id'] = job_df.index + 1


# # 결과를 엑셀 파일로 저장
# output_file_path = './crawling_data_merged/job_transform_column_final_2(0826).xlsx'
# job_df.to_excel(output_file_path, index=False)

# print(f"새로운 데이터가 {output_file_path}에 저장되었습니다.")


# import pandas as pd
# import re

# # 파일 경로 설정
# job_file_path = './crawling_data_merged/job_merged_file.xlsx'
# column_translation_path = './preprocessing/열이름변환.xlsx'

# # 엑셀 파일 로드
# job_df = pd.read_excel(job_file_path)
# column_translation_df = pd.read_excel(column_translation_path)

# # 열 이름 변환 정보를 딕셔너리로 변환
# column_translation_dict = pd.Series(column_translation_df['변환후'].values, index=column_translation_df['변환전']).to_dict()

# # 근무유형을 근무형태에 데이터를 합치기 (근무형태에 근무유형을 덧붙임)
# job_df['근무형태'] = job_df['근무형태'].fillna('') + ' ' + job_df['근무유형'].fillna('')

# # 기존의 '근무유형' 열 삭제
# job_df = job_df.drop(columns=['근무유형'])

# # 열 이름 영어로 변환
# job_df = job_df.rename(columns=column_translation_dict)

# # 지역명 리스트
# regions = [
#     "기장군", "동래구", "사상구", "수영구", "중구", "강서구", "남구", 
#     "부산진구", "사하구", "연제구", "해운대구", "금정구", "동구", 
#     "북구", "서구", "영도구"
# ]

# # title에서 대괄호와 그 안의 내용, 소괄호 안의 지역명을 제거하고, ' - ' 뒤 내용 subtitle로 분리
# def clean_title(title, regions):
#     # 대괄호와 그 안의 내용 제거
#     title = re.sub(r'\[.*?\]', '', title).strip()
    
#     # 소괄호 안에 지역명이 포함된 경우 소괄호와 그 안의 내용 제거
#     for region in regions:
#         title = re.sub(r'\(.*?' + re.escape(region) + r'.*?\)', '', title).strip()
    
#     # ' - '를 기준으로 분리
#     if ' - ' in title:
#         main_title, subtitle = title.split(' - ', 1)
#     else:
#         main_title = title
#         subtitle = None
    
#     return main_title, subtitle

# # title 열을 처리하고 subtitle 열 추가
# job_df[['title', 'subtitle']] = job_df.apply(lambda row: pd.Series(clean_title(row['title'], regions)), axis=1)

# # subtitle 열을 title 옆으로 이동
# columns = list(job_df.columns)
# columns.insert(columns.index('title') + 1, columns.pop(columns.index('subtitle')))
# job_df = job_df[columns]

# # title과 link 내용 비교하여 중복되는 행 삭제
# job_df = job_df.drop_duplicates(subset=['title', 'link'], keep=False)

# # '마감' 텍스트 제거 함수
# def remove_closing_text(date_value):
#     if isinstance(date_value, str):
#         # '마감' 텍스트 제거
#         return re.sub(r'마감$', '', date_value).strip()
#     return date_value

# # 날짜 형식 변환 함수
# def format_date(date_value):
#     date_value = remove_closing_text(date_value)
    
#     # 다양한 형식의 날짜를 처리하기 위한 패턴
#     date_formats = ['%y/%m/%d', '%y.%m.%d', '%Y-%m-%d']
    
#     for date_format in date_formats:
#         try:
#             # 날짜 형식을 2024-08-13 형식으로 통일
#             return pd.to_datetime(date_value, format=date_format).strftime('%Y-%m-%d')
#         except ValueError:
#             continue
    
#     # 날짜 형식이 맞지 않으면 원래 텍스트 반환
#     return date_value

# # signup_date와 due_date 열에서 날짜 형식 통일
# job_df['signup_date'] = job_df['signup_date'].apply(format_date)
# job_df['due_date'] = job_df['due_date'].apply(format_date)

# # details에서 스페이스바 여러 개를 한 개로 치환
# def clean_spaces(text):
#     if isinstance(text, str):
#         return re.sub(r'\s+', ' ', text)
#     return text

# job_df['details'] = job_df['details'].apply(clean_spaces)

# # 결과를 CSV 파일로 저장
# output_file_path = './crawling_data_merged/job_transform_column_final.csv'
# job_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

# print(f"새로운 데이터가 {output_file_path}에 저장되었습니다.")




# import pandas as pd

# # 파일 경로 설정
# job_file_path = './crawling_data_merged/job_merged_file.xlsx'
# column_translation_path = './preprocessing/열이름변환.xlsx'

# # 엑셀 파일 로드
# job_df = pd.read_excel(job_file_path)
# column_translation_df = pd.read_excel(column_translation_path)

# # 열 이름 변환 정보를 딕셔너리로 변환
# column_translation_dict = pd.Series(column_translation_df['변환후'].values, index=column_translation_df['변환전']).to_dict()

# # 근무유형을 근무형태에 데이터를 합치기 (근무형태에 근무유형을 덧붙임)
# job_df['근무형태'] = job_df['근무형태'].fillna('') + ' ' + job_df['근무유형'].fillna('')

# # 기존의 '근무유형' 열 삭제
# job_df = job_df.drop(columns=['근무유형'])

# # 열 이름 영어로 변환
# job_df = job_df.rename(columns=column_translation_dict)

# # title에서 대괄호 제거, ' - ' 뒤 내용 subtitle로 분리, 소괄호와 그 안의 내용 제거
# def clean_title(title):
#     # 대괄호 제거
#     title = re.sub(r'\[.*?\]', '', title).strip()
    
#     # 소괄호와 그 안의 내용 제거
#     title = re.sub(r'\(.*?\)', '', title).strip()
    
#     # ' - '를 기준으로 분리
#     if ' - ' in title:
#         main_title, subtitle = title.split(' - ', 1)
#     else:
#         main_title = title
#         subtitle = None
    
#     return main_title, subtitle

# # title 열을 처리하고 subtitle 열 추가
# job_df[['title', 'subtitle']] = job_df.apply(lambda row: pd.Series(clean_title(row['title'])), axis=1)


# # 결과 저장
# output_file_path = './crawling_data_merged/job_transform_column.xlsx'
# job_df.to_excel(output_file_path, index=False)

# output_file_path