import pandas as pd
import re

# CSV 파일 로드
file_path = './data/통합된_데이터_수정.csv'
data = pd.read_csv(file_path)

def clean_text(text):
    # 모든 HTML 스타일 태그와 그 내용을 제거
    text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
    # 특정 HTML 태그 (iframe, div, td, br 등) 및 그 내용을 삭제
    text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # <br> 및 <br/> 태그와 텍스트 'br'도 제거
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
    # 일반 텍스트로 존재하는 'br' 제거
    text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
    # 특수 문자 제거 (모든 비문자 및 숫자 문자 제거)
    text = re.sub(r'[^\w\s]', '', text)
    # 여러 개의 공백을 하나로 줄이기
    text = re.sub(r'\s+', ' ', text).strip()
    # 이모티콘 및 이모지 제거
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
    return text

# 'combined' 열의 NaN 값을 빈 문자열로 대체하고 문자열로 변환
data['combined'] = data['combined'].fillna('').astype(str)

# 전처리 함수 적용 후 'combined' 열 업데이트
data['combined'] = data['combined'].apply(clean_text)

# 512자 이상 되는 행 필터링
long_rows = data[data['combined'].str.len() > 512]

# 전처리된 데이터를 새로운 CSV 파일로 저장
output_file_path = './data/cleaned_merged_data2.csv'
data.to_csv(output_file_path, index=False, encoding='utf-8-sig')

# 512자 이상인 행의 개수 출력
print(f"Number of rows with more than 512 characters: {len(long_rows)}")



