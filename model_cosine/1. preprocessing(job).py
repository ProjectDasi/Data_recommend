import pandas as pd
import re

# 파일 경로 설정
file_path = './2.preference_fill_with_model/data/job_merged_file_with_predictions(1030).csv'

# 데이터 로드
data = pd.read_csv(file_path)

# 필요한 열만 선택
selected_columns = ['id', 'title', 'subtitle', 'work_category', 'certification', 'preference_type', 'region_id']
data_selected = data[selected_columns]

# 열을 합치는 작업 수행 (id와 region_id를 제외한 열들을 결합)
data_selected['combined'] = data_selected.apply(lambda row: ' '.join(row[['title', 'subtitle', 'work_category', 'certification', 'preference_type']].values.astype(str)), axis=1)

# 텍스트 전처리 함수 정의
def clean_text(text):
    # 1. 모든 HTML 스타일 태그와 그 내용을 제거
    text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
    
    # 2. 특정 HTML 태그 (iframe, div, td 등) 및 그 내용을 삭제
    text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # 3. <br> 및 <br/> 태그와 텍스트 'br'도 제거
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
    
    # 4. 숫자 제거
    text = re.sub(r'\d+', '', text)
    
    # 5. 영어 알파벳 제거
    text = re.sub(r'[A-Za-z]', '', text)
    
    # 6. 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
    text = re.sub(r'[^\w\s]', '', text)
    
    # 7. '수정'이라는 단어 제거
    text = re.sub(r'수정', '', text)
    
    # 8. 여러 개의 공백을 하나로 줄이기
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 9. 이모티콘 및 이모지 제거
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
    
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
cleaned_file_no_nan_fixed_path = './model_cosine/data/cleaned_job_data_no_nan_fixed(1030).csv'
data_cleaned_no_nan.to_csv(cleaned_file_no_nan_fixed_path, index=False, encoding='utf-8-sig')

print(f"파일 저장 완료: {cleaned_file_no_nan_fixed_path}")


# import pandas as pd
# import re

# # 파일 경로 설정
# file_path = './2.preference_fill_with_model/data/job_merged_file_with_predictions(1022).csv'

# # 데이터 로드
# data = pd.read_csv(file_path)

# # 1. 모든 열을 합친 데이터 생성 [id, combined_cleaned]

# # 필요한 열만 선택 (id 열 추가)
# selected_columns = ['id', 'title','region_name', 'work_category', 'certification', 'preference_type', 'details']
# data_selected = data[selected_columns]

# # 열을 합치는 작업 수행 (id를 제외한 열들을 결합)
# data_selected['combined'] = data_selected.apply(lambda row: ' '.join(row[1:].values.astype(str)), axis=1)

# # 텍스트 전처리 함수 정의
# def clean_text(text):
#     # 1. 모든 HTML 스타일 태그와 그 내용을 제거
#     text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
    
#     # 2. 특정 HTML 태그 (iframe, div, td 등) 및 그 내용을 삭제
#     text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
#     # 3. <br> 및 <br/> 태그와 텍스트 'br'도 제거
#     text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
    
#     # 4. 숫자 제거
#     text = re.sub(r'\d+', '', text)
    
#     # 5. 영어 알파벳 제거
#     text = re.sub(r'[A-Za-z]', '', text)
    
#     # 6. 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
#     text = re.sub(r'[^\w\s]', '', text)
    
#     # 7. '수정'이라는 단어 제거
#     text = re.sub(r'수정', '', text)
    
#     # 8. 여러 개의 공백을 하나로 줄이기
#     text = re.sub(r'\s+', ' ', text).strip()
    
#     # 9. 이모티콘 및 이모지 제거
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
# cleaned_file_no_nan_fixed_path = './model_cosine/data/cleaned_job_data_no_nan_fixed.csv'
# data_cleaned_no_nan.to_csv(cleaned_file_no_nan_fixed_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {cleaned_file_no_nan_fixed_path}")


# # 2. region_name만 사용 [id, region_name]

# # 필요한 열만 선택
# data_region = data[['id', 'region_name']]

# # NaN 값 제거
# data_region_no_nan = data_region.dropna()

# # 파일 저장 경로
# region_file_path = './model_cosine/data/region_name_data.csv'
# data_region_no_nan.to_csv(region_file_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {region_file_path}")


# # 3. certification만 사용 [id, certification]

# # 필요한 열만 선택
# data_certification = data[['id', 'certification']]

# # NaN 값을 "관계없음"으로 대체
# data_certification_filled = data_certification.fillna('관계없음')

# # 파일 저장 경로
# certification_file_path = './model_cosine/data/certification_data.csv'
# data_certification_filled.to_csv(certification_file_path, index=False, encoding='utf-8-sig')

# print(f"파일 저장 완료: {certification_file_path}")
