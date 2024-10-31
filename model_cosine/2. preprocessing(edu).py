import pandas as pd
import re

# 파일 경로 설정
file_path = './2.preference_fill_with_model/data/education_merged_file_with_predictions(1022).csv'

# 데이터 로드
data = pd.read_csv(file_path)

# 필요한 열만 선택
selected_columns = ['id', 'title', 'organization', 'preference_type', 'region_id']
data_selected = data[selected_columns]

# 열을 합치는 작업 수행 (id와 region_id를 제외한 열들을 결합)
data_selected['combined'] = data_selected[['title', 'organization', 'preference_type']].astype(str).agg(' '.join, axis=1)

# 불필요한 단어와 패턴을 제거하는 함수 정의
def clean_unwanted_patterns(text):
    # 영어 제거 (영어는 소문자 및 대문자로 이루어짐)
    text = re.sub(r'[A-Za-z]+', '', text)
    # 특정 단어 제거
    text = re.sub(r'맑은|고딕|MalgunGothic|SansSerif|Noto', '', text)
    # 숫자 및 특수문자 패턴 제거 (영문과 숫자가 섞인 긴 패턴들 포함)
    text = re.sub(r'[0-9a-zA-Z]{10,}', '', text)
    # 태그 형식의 문자열 제거 (<tag>, <tag attr="value"> 등)
    text = re.sub(r'<.*?>', '', text)
    # 불필요한 공백 및 개행 문자 제거
    text = re.sub(r'\s+', ' ', text).strip()
    # 숫자 제거
    text = re.sub(r'\d+', '', text)
    return text

# 텍스트 전처리 함수 정의
def clean_text(text):
    # 모든 HTML 스타일 태그와 그 내용을 제거
    text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
    # 특정 HTML 태그 (iframe, div, td 등) 및 그 내용을 삭제
    text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # <br> 및 <br/> 태그와 텍스트 'br'도 제거
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
    # 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
    text = re.sub(r'[^\w\s]', '', text)
    # 여러 개의 공백을 하나로 줄이기
    text = re.sub(r'\s+', ' ', text).strip()
    # 이모티콘 및 이모지 제거
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
    
    # 추가로 불필요한 패턴 제거
    text = clean_unwanted_patterns(text)
    
    return text

# 전처리 적용
data_selected['combined_cleaned'] = data_selected['combined'].apply(clean_text)

# 'nan' 문자열을 공백으로 대체
data_selected['combined_cleaned'] = data_selected['combined_cleaned'].replace('nan', '', regex=True)

# 필요한 열만 남기기
data_cleaned_with_id = data_selected[['id', 'combined_cleaned', 'region_id']]

# NaN 값 제거
data_cleaned_no_nan = data_cleaned_with_id.dropna()

# 파일 저장 경로
cleaned_file_no_nan_fixed_path = './model_cosine/data/(edu)cleaned_education_data_no_nan_fixed(1022).csv'
data_cleaned_no_nan.to_csv(cleaned_file_no_nan_fixed_path, index=False, encoding='utf-8-sig')

print(f"파일 저장 완료: {cleaned_file_no_nan_fixed_path}")



# import pandas as pd
# import re

# # 파일 경로 설정
# file_path = './2.preference_fill_with_model/data/education_merged_file_with_predictions(0920).csv'

# # 데이터 로드
# data = pd.read_csv(file_path)

# # 1. 모든 열을 합친 데이터 생성 [id, combined_cleaned]

# # 필요한 열만 선택 (id 열 추가)
# selected_columns = ['id', 'title', 'details', 'preference_type', 'organization']
# data_selected = data[selected_columns]

# # 열을 합치는 작업 수행 (id를 제외한 title, details, preference_type, organization 열들을 결합)
# data_selected['combined'] = data_selected[['title', 'details', 'preference_type', 'organization']].astype(str).agg(' '.join, axis=1)

# # 불필요한 단어와 패턴을 제거하는 함수 정의
# def clean_unwanted_patterns(text):
#     # 영어 제거 (영어는 소문자 및 대문자로 이루어짐)
#     text = re.sub(r'[A-Za-z]+', '', text)
#     # 맑은, 고딕 등 특정 단어 제거
#     text = re.sub(r'맑은|고딕|MalgunGothic|SansSerif|Noto', '', text)
#     # 숫자 및 특수문자 패턴 제거 (영문과 숫자가 섞인 긴 패턴들 포함)
#     text = re.sub(r'[0-9a-zA-Z]{10,}', '', text)
#     # 태그 형식의 문자열 제거 (<tag>, <tag attr="value"> 등)
#     text = re.sub(r'<.*?>', '', text)
#     # 불필요한 공백 및 개행 문자 제거
#     text = re.sub(r'\s+', ' ', text).strip()
#     # 4. 숫자 제거
#     text = re.sub(r'\d+', '', text)
    
#     # 5. 영어 알파벳 제거
#     text = re.sub(r'[A-Za-z]', '', text)
#     return text

# # 텍스트 전처리 함수 정의
# def clean_text(text):
#     # 모든 HTML 스타일 태그와 그 내용을 제거
#     text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
#     # 특정 HTML 태그 (iframe, div, td 등) 및 그 내용을 삭제
#     text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
#     # <br> 및 <br/> 태그와 텍스트 'br'도 제거
#     text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
#     # 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
#     text = re.sub(r'[^\w\s]', '', text)
#     # 여러 개의 공백을 하나로 줄이기
#     text = re.sub(r'\s+', ' ', text).strip()
#     # 이모티콘 및 이모지 제거
#     text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
    
#     # 추가로 불필요한 패턴 제거
#     text = clean_unwanted_patterns(text)
    
#     return text

# # 전처리 적용
# data_selected['combined_cleaned'] = data_selected['combined'].apply(clean_text)

# # 'nan' 문자열을 공백으로 대체
# data_selected['combined_cleaned'] = data_selected['combined_cleaned'].replace('nan', '', regex=True)

# # id와 전처리된 열만 남기기
# data_cleaned_with_id = data_selected[['id', 'combined_cleaned']]

# # NaN 값 제거
# data_cleaned_no_nan = data_cleaned_with_id.dropna()

# # 파일 저장 경로
# cleaned_file_no_nan_fixed_path = './model_cosine/data/(edu)cleaned_education_data_no_nan_fixed.csv'
# data_cleaned_no_nan.to_csv(cleaned_file_no_nan_fixed_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {cleaned_file_no_nan_fixed_path}")


# # 2. organization만 사용 [id, organization]

# # 필요한 열만 선택
# data_organization = data[['id', 'organization']]

# # NaN 값 제거
# data_organization_no_nan = data_organization.dropna()

# # 파일 저장 경로
# organization_file_path = './model_cosine/data/(edu)organization_data.csv'
# data_organization_no_nan.to_csv(organization_file_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {organization_file_path}")



# import pandas as pd
# import re

# # 파일 경로 설정
# file_path = './2.preference_fill_with_model/data/education_merged_file_with_predictions(0920).csv'

# # 데이터 로드
# data = pd.read_csv(file_path)

# # 1. 모든 열을 합친 데이터 생성 [id, combined_cleaned]

# # 필요한 열만 선택 (id 열 추가)
# selected_columns = ['id', 'title', 'details', 'preference_type', 'organization']
# data_selected = data[selected_columns]

# # 열을 합치는 작업 수행 (id를 제외한 열들을 결합)
# data_selected['combined'] = data_selected.apply(lambda row: ' '.join(row[1:].values.astype(str)), axis=1)

# # 텍스트 전처리 함수 정의
# def clean_text(text):
#     # 모든 HTML 스타일 태그와 그 내용을 제거
#     text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
#     # 특정 HTML 태그 (iframe, div, td 등) 및 그 내용을 삭제
#     text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
#     # <br> 및 <br/> 태그와 텍스트 'br'도 제거
#     text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
#     # 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
#     text = re.sub(r'[^\w\s]', '', text)
#     # 여러 개의 공백을 하나로 줄이기
#     text = re.sub(r'\s+', ' ', text).strip()
#     # 이모티콘 및 이모지 제거
#     text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
#     return text

# # 전처리 적용
# data_selected['combined_cleaned'] = data_selected['combined'].apply(clean_text)

# # 'nan' 문자열을 공백으로 대체
# data_selected['combined_cleaned'] = data_selected['combined_cleaned'].replace('nan', '', regex=True)

# # id와 전처리된 열만 남기기
# data_cleaned_with_id = data_selected[['id', 'combined_cleaned']]

# # NaN 값 제거
# data_cleaned_no_nan = data_cleaned_with_id.dropna()

# # 파일 저장 경로
# cleaned_file_no_nan_fixed_path = './model_cosine/data/(edu)cleaned_education_data_no_nan_fixed.csv'
# data_cleaned_no_nan.to_csv(cleaned_file_no_nan_fixed_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {cleaned_file_no_nan_fixed_path}")


# # 2. organization만 사용 [id, organization]

# # 필요한 열만 선택
# data_organization = data[['id', 'organization']]

# # NaN 값 제거
# data_organization_no_nan = data_organization.dropna()

# # 파일 저장 경로
# organization_file_path = './model_cosine/data/(edu)organization_data.csv'
# data_organization_no_nan.to_csv(organization_file_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {organization_file_path}")


