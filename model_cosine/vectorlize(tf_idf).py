import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# 데이터 로드 경로들
job_file_paths = {
    'combined_cleaned': './model_cosine/data/cleaned_job_data_no_nan_fixed.csv',
    'region_name': './model_cosine/data/region_name_data.csv',
    'certification': './model_cosine/data/certification_data.csv'
}

edu_file_paths = {
    'combined_cleaned': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)cleaned_education_data_no_nan_fixed.csv',
    'organization': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)organization_data.csv',
}

# TF-IDF 벡터화를 위한 함수
def tfidf_vectorize(texts, vectorizer):
    tfidf_matrix = vectorizer.transform(texts)
    return tfidf_matrix.toarray()

# 일자리와 교육 데이터를 결합하여 벡터화기 학습하는 함수
def create_combined_tfidf_vectorizer(job_paths, edu_paths):
    # 일자리 데이터 로드
    job_data_combined = pd.read_csv(job_paths['combined_cleaned'])['combined_cleaned'].fillna('')
    job_data_region = pd.read_csv(job_paths['region_name'])['region_name'].fillna('')
    job_data_cert = pd.read_csv(job_paths['certification'])['certification'].fillna('')
    
    # 교육 데이터 로드
    edu_data_combined = pd.read_csv(edu_paths['combined_cleaned'])['combined_cleaned'].fillna('')
    edu_data_org = pd.read_csv(edu_paths['organization'])['organization'].fillna('')

    # 두 데이터셋을 결합하여 학습 데이터로 사용 (단, 고유 ID는 결합하지 않음)
    combined_data = pd.concat([job_data_combined, job_data_region, job_data_cert, edu_data_combined, edu_data_org])
    
    # 벡터화기 생성 및 학습
    vectorizer = TfidfVectorizer(max_features=768)
    vectorizer.fit(combined_data)

    return vectorizer

# 각 파일에 대해 벡터화 작업을 수행하는 함수 (고유 ID 유지)
def process_and_save(file_path, text_column, output_file, vectorizer):
    # 데이터 로드
    data = pd.read_csv(file_path)

    # 텍스트 데이터를 리스트로 가져오기
    texts = data[text_column].fillna('')  # NaN 값을 빈 문자열로 처리
    
    # TF-IDF 벡터화 수행
    vectors = tfidf_vectorize(texts, vectorizer)

    # 벡터화된 결과를 데이터프레임으로 변환 (id 포함)
    vectorized_columns = ['id'] + [f'tfidf_{i}' for i in range(vectors.shape[1])]
    vectorized_data = pd.DataFrame(vectors, columns=vectorized_columns[1:])
    vectorized_data.insert(0, 'id', data['id'])  # 'id' 열 추가

    # 벡터화된 데이터를 CSV로 저장
    vectorized_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"벡터화된 데이터가 다음 위치에 저장되었습니다: {output_file}")

# 벡터화기 학습 (일자리와 교육 데이터를 결합하여 벡터화기 학습)
tfidf_vectorizer = create_combined_tfidf_vectorizer(job_file_paths, edu_file_paths)

# 1. 일자리 데이터 벡터화 및 저장 (고유 ID 유지)
process_and_save(job_file_paths['combined_cleaned'], 'combined_cleaned', './model_cosine/data/vector_data/tfidf_vectorized_combined_cleaned.csv', tfidf_vectorizer)
process_and_save(job_file_paths['region_name'], 'region_name', './model_cosine/data/vector_data/tfidf_vectorized_region_name.csv', tfidf_vectorizer)
process_and_save(job_file_paths['certification'], 'certification', './model_cosine/data/vector_data/tfidf_vectorized_certification.csv', tfidf_vectorizer)

# 2. 교육 데이터 벡터화 및 저장 (고유 ID 유지)
process_and_save(edu_file_paths['combined_cleaned'], 'combined_cleaned', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\tfidf_vectorized_combined_cleaned.csv', tfidf_vectorizer)
process_and_save(edu_file_paths['organization'], 'organization', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\tfidf_vectorized_organization.csv', tfidf_vectorizer)