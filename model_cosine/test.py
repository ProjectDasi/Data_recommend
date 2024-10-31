import pandas as pd

# 파일 경로 설정 (사용자의 파일 경로로 수정)
file_path = './model_cosine/data/cleaned_job_data_no_nan_fixed.csv'

# CSV 파일 로드
data = pd.read_csv(file_path)

# 'combined_cleaned' 열의 텍스트 길이 계산
data['text_length'] = data['combined_cleaned'].apply(len)

# 최대 텍스트 길이를 가진 행의 ID 찾기
max_length_row = data.loc[data['text_length'].idxmax()]
max_length_id = max_length_row['id']

print(f"최대 텍스트 길이를 가진 ID: {max_length_id}, 텍스트 길이: {max_length_row['text_length']}")