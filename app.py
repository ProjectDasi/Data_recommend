from flask import Flask, request, jsonify
import pandas as pd
import logging
import os
import json
from utils import clean_text, tfidf_vectorize
from utils import tfidf_vectorize, clean_text, create_and_train_tfidf_vectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
from transformers import BertModel, BertTokenizer

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# KC-BERT 모델과 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-large')
model = BertModel.from_pretrained('beomi/kcbert-large')

# GPU 사용 여부 확인
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 벡터화된 데이터 로드 (job, edu, region_name, organization)
job_vectors = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data\kcbert_vectorized_combined_cleaned(1030).csv')
edu_vectors = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned(1022).csv')

# KC-BERT 벡터화 함수
def bert_vectorize(text, max_length=512):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
    inputs = {key: val.to(device) for key, val in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    return cls_embedding.flatten()


# 가장 유사한 단어 찾기 함수
def get_top_n_similar_words(input_vector, top_n=3):
    # BERT의 vocab에서 토큰들을 가져옴
    token_embeddings = model.embeddings.word_embeddings.weight.cpu().detach().numpy()
    
    # 코사인 유사도 계산
    similarities = cosine_similarity(input_vector.reshape(1, -1), token_embeddings)
    
    # 유사도 상위 n개 토큰 인덱스 추출
    top_n_indices = similarities[0].argsort()[-top_n:][::-1]
    
    # 토크나이저를 이용해 인덱스를 단어로 변환
    top_n_words = [tokenizer.decode([idx]).strip() for idx in top_n_indices]
    
    return top_n_words

# # 기존의 벡터화된 CSV 파일 로드
# job_vectors = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data\tfidf_vectorized_combined_cleaned.csv')
# edu_vectors = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\tfidf_vectorized_combined_cleaned.csv')

# # TF-IDF 벡터화기를 생성하고 학습 (기존 job 및 edu 데이터로 학습된 vectorizer)
# job_text_columns = job_vectors.iloc[:, 1:]  # job 데이터의 텍스트 부분만 사용
# edu_text_columns = edu_vectors.iloc[:, 1:]  # edu 데이터의 텍스트 부분만 사용
# job_tfidf_vectorizer = create_and_train_tfidf_vectorizer(job_text_columns.columns)  # job용 벡터화기
# edu_tfidf_vectorizer = create_and_train_tfidf_vectorizer(edu_text_columns.columns)  # edu용 벡터화기

# CSV 파일 경로
csv_file_path = './2.preference_fill_with_model/data/job_merged_file_with_predictions(1030).csv'
json_file_path = './2.preference_fill_with_model/data/education_merged_file_with_predictions(1022).json'

# CSV 파일이 존재하는지 확인하고 로드
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
    logging.info("CSV file loaded successfully.")
else:
    logging.error(f"CSV file not found at path: {csv_file_path}")
    df = pd.DataFrame()  # 데이터 프레임을 빈 상태로 초기화

# JSON 파일이 존재하는지 확인하고 로드
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        education_data = json.load(f)
        education_df = pd.DataFrame(education_data)
        logging.info("JSON file loaded successfully.")
else:
    logging.error(f"JSON file not found at path: {json_file_path}")
    education_df = pd.DataFrame()  # 데이터 프레임을 빈 상태로 초기화

###################### App.route ############################################

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     # 1. 입력 데이터 전처리
#     data = request.get_json()
#     address = clean_text(data.get('address', ''))
#     work_description = clean_text(data.get('workDescription', ''))
#     certification_name = clean_text(data.get('certificationName', ''))
#     training_name = clean_text(data.get('trainingName', ''))
#     major = clean_text(data.get('major', ''))
#     preference_type = clean_text(data.get('preferenceType', ''))

#     # 입력값을 리스트로 저장 (각 항목 별로 벡터화하여 유사도 계산을 위해)
#     input_fields = [work_description, certification_name, training_name, major, preference_type]

#     # 2. Address 벡터화 및 region_name과 코사인 유사도 계산
#     address_vector = bert_vectorize(address).reshape(1, -1)
#     region_vectors_only = region_vectors.iloc[:, 1:].values  # region_name 벡터들 (id 제외)
#     region_similarities = cosine_similarity(address_vector, region_vectors_only)
    
#     # 가장 유사한 region_name 찾기
#     top_region_index = np.argmax(region_similarities[0])
#     top_region_id = region_vectors.iloc[top_region_index]['id']
#     top_region_similarity = region_similarities[0][top_region_index]

#     #### Job 관련 작업 ####
#     # 3. 입력 텍스트 (address 제외)를 하나의 텍스트로 결합
#     combined_text = ' '.join(input_fields)
#     print(f"Combined input text: {combined_text}")

#     # 4. 입력 텍스트를 KC-BERT로 벡터화
#     job_input_vector = bert_vectorize(combined_text).reshape(1, -1)
#     print(f"Job input vector shape: {job_input_vector.shape}")

#     # 5. Job 벡터에서 id를 제외한 부분만 추출
#     job_vectors_only = job_vectors.iloc[:, 1:].values  # 기존 job 벡터들 (id 제외)

#     # 6. 코사인 유사도 계산 (job)
#     job_similarities = cosine_similarity(job_input_vector, job_vectors_only)

#     # 7. 종합 점수 계산 (region_name 유사도와 job 유사도의 가중합)
#     weight_region = 0.3  # region_name 유사도에 대한 가중치
#     weight_job = 0.7  # job 유사도에 대한 가중치



#     # 종합 점수 계산 (가중합)
#     combined_scores = (weight_region * top_region_similarity) + (weight_job * job_similarities[0])

#     # 8. 상위 6개의 유사한 job id 찾기
#     top_6_job_indices = np.argsort(combined_scores)[-6:][::-1]
#     top_6_job_ids = job_vectors.iloc[top_6_job_indices]['id'].tolist()
#     top_6_combined_scores = combined_scores[top_6_job_indices].tolist()

#     #### Edu 관련 작업 ####
#     # 9. Organization 벡터화 및 코사인 유사도 계산
#     organization_vector = bert_vectorize(combined_text).reshape(1, -1)
#     organization_vectors_only = organization_vectors.iloc[:, 1:].values  # organization 벡터들 (id 제외)
#     organization_similarities = cosine_similarity(organization_vector, organization_vectors_only)
    
#     # 각 edu 벡터에 대해 organization 유사도 구하기
#     organization_similarities_for_edu = organization_similarities[0][edu_vectors.index]  # edu id에 맞는 organization 유사도

#     # 10. Edu 텍스트를 KC-BERT로 벡터화
#     edu_input_vector = bert_vectorize(combined_text).reshape(1, -1)

#     # 11. Edu 벡터에서 id를 제외한 부분만 추출
#     edu_vectors_only = edu_vectors.iloc[:, 1:].values  # 기존 edu 벡터들 (id 제외)

#     # 12. 코사인 유사도 계산 (edu)
#     edu_similarities = cosine_similarity(edu_input_vector, edu_vectors_only)

#     # 13. 종합 점수 계산 (organization 유사도와 edu 유사도의 가중합)
#     weight_organization = 0.7  # organization 유사도에 대한 가중치
#     weight_edu = 0.3  # edu 유사도에 대한 가중치

#     combined_edu_scores = (weight_organization * organization_similarities_for_edu) + (weight_edu * edu_similarities[0])

#     # 14. 상위 6개의 유사한 edu id 찾기
#     top_6_edu_indices = np.argsort(combined_edu_scores)[-6:][::-1]
#     top_6_edu_ids = edu_vectors.iloc[top_6_edu_indices]['id'].tolist()
#     top_6_combined_edu_scores = combined_edu_scores[top_6_edu_indices].tolist()

#     #### 각 입력값에 대한 유사도 분석 ####
#     # 15. 각 필드별로 벡터화 후 유사도 계산
#     field_vectors = [bert_vectorize(field).reshape(1, -1) for field in input_fields]
#     field_similarities = [cosine_similarity(vec, job_vectors_only)[0].max() for vec in field_vectors]

#     # 16. 상위 3개의 유사도가 높은 필드 값 찾기
#     top_3_field_indices = np.argsort(field_similarities)[-3:][::-1]
#     top_3_field_values = [input_fields[i] for i in top_3_field_indices]

#     # 17. 최종 결과 반환
#     return jsonify({
#         'job_recommendations': [
#             {'id': job_id, 'similarity': score, 'tag': f'{", ".join(top_3_field_values)}'}
#             for job_id, score in zip(top_6_job_ids, top_6_combined_scores)
#         ],
#         'education_recommendations': [
#             {'id': edu_id, 'similarity': score, 'tag': f'{", ".join(top_3_field_values)}'}
#             for edu_id, score in zip(top_6_edu_ids, top_6_combined_edu_scores)
#         ]
#     })

@app.route('/recommend', methods=['POST'])
def recommend():
    # 1. 입력 데이터 전처리
    data = request.get_json()
    user_region_id = data.get('regionId')
    is_disabled = data.get('isDisabled', False)
    favorites_jobs = data.get('favorites', {}).get('jobs', [])
    favorites_edu = data.get('favorites', {}).get('edu', [])

    # job 추천 데이터 로드 및 지역 필터링
    job_data = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data\kcbert_vectorized_combined_cleaned(1030).csv')
    region_ids_to_filter = set([user_region_id] + [job.get('regionId') for job in favorites_jobs])
    filtered_jobs = job_data[job_data['region_id'].isin(region_ids_to_filter)].copy()

    job_recommendations = []

    # isDisabled가 True인 경우 "사무" 키워드가 포함된 항목을 별도로 필터링하여 추천
    if is_disabled:
        # "사무"와 관련된 다양한 키워드를 사용하여 필터링
        office_job_data = pd.read_csv(r'./2.preference_fill_with_model/data/job_merged_file_with_predictions(1030).csv')
        office_jobs = office_job_data[
            (office_job_data['work_category'].str.contains("사무", na=False) |
            office_job_data['title'].str.contains("사무", na=False)) |
            office_job_data['preferred_qualifications'].str.contains("장애", na=False)
        ]

        # 필터링된 항목의 id만 추출
        office_job_ids = set(office_jobs['id'].values)
        
        # job_data에서 office_job_ids에 해당하는 행만 필터링하여 office_job_vectors 생성
        filtered_job_data = job_data[job_data['id'].isin(office_job_ids)]
        office_job_vectors = filtered_job_data.iloc[:, 1:-1].values  # 코사인 유사도 계산을 위한 벡터 데이터 추출
        
        # 코사인 유사도 계산
        for favorite_job in favorites_jobs[:2]:
            combined_text = ' '.join([
                clean_text(favorite_job.get('title', '')),
                clean_text(favorite_job.get('subtitle', '')),
                clean_text(favorite_job.get('workCategory', '')),
                clean_text(favorite_job.get('certification', '')),
                clean_text(favorite_job.get('preferenceType', ''))
            ])
            favorite_vector = bert_vectorize(combined_text).reshape(1, -1)
            similarities = cosine_similarity(favorite_vector, office_job_vectors)
            top_indices = np.argsort(similarities[0])[::-1]
            recommendations = []
            for index in top_indices:
                job_id = filtered_job_data.iloc[index]['id']  # 필터링된 데이터에서 id 가져오기
                similarity = similarities[0][index]
                if job_id not in {job['id'] for job in favorites_jobs}:
                    recommendations.append({'id': job_id, 'similarity': similarity})
                if len(recommendations) == 3:
                    break
            job_recommendations.extend(recommendations)

    # 일반 job 추천
    if not is_disabled and not filtered_jobs.empty:
        filtered_job_vectors = filtered_jobs.iloc[:, 1:-1].values
        input_job_ids_to_exclude = {job['id'] for job in favorites_jobs}
        
        for favorite_job in favorites_jobs[:2]:
            combined_text = ' '.join([
                clean_text(favorite_job.get('title', '')),
                clean_text(favorite_job.get('subtitle', '')),
                clean_text(favorite_job.get('workCategory', '')),
                clean_text(favorite_job.get('certification', '')),
                clean_text(favorite_job.get('preferenceType', ''))
            ])
            favorite_vector = bert_vectorize(combined_text).reshape(1, -1)
            similarities = cosine_similarity(favorite_vector, filtered_job_vectors)
            top_indices = np.argsort(similarities[0])[::-1]
            recommendations = []
            for index in top_indices:
                job_id = filtered_jobs.iloc[index]['id']
                similarity = similarities[0][index]
                if job_id not in input_job_ids_to_exclude:
                    recommendations.append({'id': job_id, 'similarity': similarity})
                if len(recommendations) == 3:
                    break
            job_recommendations.extend(recommendations)

    # edu 추천 데이터 로드
    edu_data = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned(1022).csv')
    edu_recommendations = []

    if not edu_data.empty:
        filtered_edu_vectors = edu_data.iloc[:, 1:-1].values
        input_edu_ids_to_exclude = {edu['id'] for edu in favorites_edu}

        for favorite_edu in favorites_edu:
            combined_text = ' '.join([
                clean_text(favorite_edu.get('title', '')),
                clean_text(favorite_edu.get('organization', '')),
                clean_text(favorite_edu.get('preferenceType', ''))
            ])
            favorite_vector = bert_vectorize(combined_text).reshape(1, -1)
            similarities = cosine_similarity(favorite_vector, filtered_edu_vectors)
            top_indices = np.argsort(similarities[0])[::-1]
            
            recommendations = []
            for index in top_indices:
                edu_id = edu_data.iloc[index]['id']
                similarity = similarities[0][index]
                if edu_id not in input_edu_ids_to_exclude:
                    recommendations.append({'id': edu_id, 'similarity': similarity})
                if len(recommendations) == 3:
                    break
            edu_recommendations.extend(recommendations)

    # 최종 결과 반환
    return jsonify({
        'job_recommendations': job_recommendations,
        'education_recommendations': edu_recommendations
    })


# # 추천 함수
# @app.route('/recommend', methods=['POST'])
# def recommend():
#     # 1. 입력 데이터 전처리
#     data = request.get_json()
#     user_region_id = data.get('regionId')
#     favorites_jobs = data.get('favorites', {}).get('jobs', [])
#     favorites_edu = data.get('favorites', {}).get('edu', [])

#     # job 추천 데이터 로드 및 지역 필터링
#     job_data = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data\kcbert_vectorized_combined_cleaned(1022).csv')
#     region_ids_to_filter = set([user_region_id] + [job.get('regionId') for job in favorites_jobs])
#     filtered_jobs = job_data[job_data['region_id'].isin(region_ids_to_filter)].copy()

#     job_recommendations = []
#     if not filtered_jobs.empty:
#         filtered_job_vectors = filtered_jobs.iloc[:, 1:-1].values
#         input_job_ids_to_exclude = {job['id'] for job in favorites_jobs}
        
#         # Job 추천
#         for favorite_job in favorites_jobs[:2]:
#             combined_text = ' '.join([
#                 clean_text(favorite_job.get('title', '')),
#                 clean_text(favorite_job.get('subtitle', '')),
#                 clean_text(favorite_job.get('workCategory', '')),
#                 clean_text(favorite_job.get('certification', '')),
#                 clean_text(favorite_job.get('preferenceType', ''))
#             ])
#             favorite_vector = bert_vectorize(combined_text).reshape(1, -1)
#             similarities = cosine_similarity(favorite_vector, filtered_job_vectors)
#             top_indices = np.argsort(similarities[0])[::-1]
#             recommendations = []
#             for index in top_indices:
#                 job_id = filtered_jobs.iloc[index]['id']
#                 similarity = similarities[0][index]
#                 if job_id not in input_job_ids_to_exclude:
#                     recommendations.append({'id': job_id, 'similarity': similarity})
#                 if len(recommendations) == 3:
#                     break
#             job_recommendations.extend(recommendations)

#     # edu 추천 데이터 로드
#     edu_data = pd.read_csv(r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned(1022).csv')
#     edu_recommendations = []

#     # Edu 추천 (처음과 마지막 열 제외하여 벡터 값만 추출)
#     if not edu_data.empty:
#         filtered_edu_vectors = edu_data.iloc[:, 1:-1].values  # 'id'와 'region_id' 제외
#         input_edu_ids_to_exclude = {edu['id'] for edu in favorites_edu}

#         # 각 edu 찜하기 항목에 대해 추천
#         for favorite_edu in favorites_edu:
#             combined_text = ' '.join([
#                 clean_text(favorite_edu.get('title', '')),
#                 clean_text(favorite_edu.get('organization', '')),
#                 clean_text(favorite_edu.get('preferenceType', ''))
#             ])
#             favorite_vector = bert_vectorize(combined_text).reshape(1, -1)
#             similarities = cosine_similarity(favorite_vector, filtered_edu_vectors)
#             top_indices = np.argsort(similarities[0])[::-1]
            
#             # 각 찜하기 항목당 최대 3개의 추천을 생성하여 구분된 형태로 저장
#             recommendations = []
#             for index in top_indices:
#                 edu_id = edu_data.iloc[index]['id']
#                 similarity = similarities[0][index]
#                 if edu_id not in input_edu_ids_to_exclude:
#                     recommendations.append({'id': edu_id, 'similarity': similarity})
#                 if len(recommendations) == 3:
#                     break

#             edu_recommendations.extend(recommendations)

#     # 최종 결과 반환
#     return jsonify({
#         'job_recommendations': job_recommendations,
#         'education_recommendations': edu_recommendations
#     })

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     # 1. 입력 데이터 전처리
#     data = request.get_json()
#     address = clean_text(data.get('address', ''))
#     work_description = clean_text(data.get('workDescription', ''))
#     certification_name = clean_text(data.get('certificationName', ''))
#     training_name = clean_text(data.get('trainingName', ''))
#     major = clean_text(data.get('major', ''))
#     preference_type = clean_text(data.get('preferenceType', ''))

#     # 입력값을 리스트로 저장 (각 항목 별로 벡터화하여 유사도 계산을 위해)
#     input_fields = [address, work_description, certification_name, training_name, major, preference_type]

#     # 입력값을 하나의 텍스트로 결합 (기존 방식 유지)
#     combined_text = ' '.join(input_fields)
#     print(f"Combined input text: {combined_text}")

#     #### Job 관련 작업 ####
#     # 2. 입력 텍스트를 KC-BERT로 벡터화
#     job_input_vector = bert_vectorize(combined_text).reshape(1, -1)
#     print(f"Job input vector shape: {job_input_vector.shape}")

#     # 3. Job 벡터에서 id를 제외한 부분만 추출
#     job_vectors_only = job_vectors.iloc[:, 1:].values  # 기존 job 벡터들 (id 제외)

#     # 4. 코사인 유사도 계산 (job)
#     job_similarities = cosine_similarity(job_input_vector, job_vectors_only)

#     # 5. 상위 6개의 유사한 job id 찾기
#     top_6_job_indices = np.argsort(job_similarities[0])[-6:][::-1]  # 상위 6개의 인덱스를 역순으로 정렬
#     top_6_job_ids = job_vectors.iloc[top_6_job_indices]['id'].tolist()  # 해당 인덱스의 id 값
#     top_6_job_similarities = job_similarities[0][top_6_job_indices].tolist()  # 상위 6개의 유사도 값

#     #### Edu 관련 작업 ####
#     # 6. 입력 텍스트를 KC-BERT로 벡터화
#     edu_input_vector = bert_vectorize(combined_text).reshape(1, -1)

#     # 7. Edu 벡터에서 id를 제외한 부분만 추출
#     edu_vectors_only = edu_vectors.iloc[:, 1:].values  # 기존 edu 벡터들 (id 제외)

#     # 8. 코사인 유사도 계산 (edu)
#     edu_similarities = cosine_similarity(edu_input_vector, edu_vectors_only)

#     # 9. 상위 6개의 유사한 edu id 찾기
#     top_6_edu_indices = np.argsort(edu_similarities[0])[-6:][::-1]  # 상위 6개의 인덱스를 역순으로 정렬
#     top_6_edu_ids = edu_vectors.iloc[top_6_edu_indices]['id'].tolist()  # 해당 인덱스의 id 값
#     top_6_edu_similarities = edu_similarities[0][top_6_edu_indices].tolist()  # 상위 6개의 유사도 값

#     #### 각 입력값에 대한 유사도 분석 ####
#     # 10. 각 필드별로 벡터화 후 유사도 계산
#     field_vectors = [bert_vectorize(field).reshape(1, -1) for field in input_fields]
#     field_similarities = [cosine_similarity(vec, job_vectors_only)[0].max() for vec in field_vectors]  # 각 필드의 유사도 계산

#     # 11. 상위 3개의 유사도가 높은 필드 값 찾기
#     top_3_field_indices = np.argsort(field_similarities)[-3:][::-1]  # 유사도가 높은 필드 3개
#     top_3_field_values = [input_fields[i] for i in top_3_field_indices]  # 해당 필드의 값

#     # 12. 최종 결과 반환
#     return jsonify({
#         'job_recommendations': [
#             {'id': job_id, 'similarity': sim, 'tag': f'{", ".join(top_3_field_values)}'}
#             for job_id, sim in zip(top_6_job_ids, top_6_job_similarities)
#         ],
#         'education_recommendations': [
#             {'id': edu_id, 'similarity': sim, 'tag': f'{", ".join(top_3_field_values)}'}
#             for edu_id, sim in zip(top_6_edu_ids, top_6_edu_similarities)
#         ]
#     })



@app.route('/get_job_id', methods=['POST'])
def get_job_id():
    # 요청에서 JSON 데이터를 가져옴
    data = request.get_json()

    # JSON에서 regionId와 preference 리스트를 추출
    region_id = data.get('regionId')
    preferences = data.get('preference')

    # region_id와 preferences 검증
    if region_id is None or not isinstance(region_id, int):
        return jsonify({'error': 'regionId must be an integer.'}), 400
    if not preferences or not isinstance(preferences, list):
        return jsonify({'error': 'Preference must be a list of strings.'}), 400

    # preference 문자열을 ID로 매핑
    preference_map = {
        '현실형': 1,
        '탐구형': 2,
        '예술형': 3,
        '사회형': 4,
        '진취형': 5,
        '관습형': 6
    }

    # preference 리스트를 ID 리스트로 변환
    preference_ids = [preference_map.get(pref) for pref in preferences if pref in preference_map]

    # 유효한 preference_id가 없는 경우 오류 반환
    if not preference_ids:
        return jsonify({'error': 'Invalid preference values provided.'}), 400

    # 로깅: 필터링 전에 요청된 region_id와 preference_id 출력
    logging.info(f"Requested region_id: {region_id}, preference_ids: {preference_ids}")

    # region_id와 preference_id 리스트에 포함된 값들이 일치하는 행을 필터링
    filtered_df = df[(df['region_id'] == region_id) & (df['preference_id'].isin(preference_ids))]

    # 로깅: 필터링 결과 출력
    logging.info(f"Filtered DataFrame: {filtered_df}")

    # 필터링된 결과에서 'id' 열의 값을 최대 15개 추출
    job_ids = filtered_df['id'].tolist()[:15]

    if not job_ids:
        return jsonify({'error': 'No matching jobs found for the given preference_id(s) and region_id.'}), 404

    return jsonify({'job_ids': job_ids})

@app.route('/get_education_id', methods=['POST'])
def get_education_id():
    # 요청에서 JSON 데이터를 가져옴
    data = request.get_json()

    # JSON에서 regionId와 preference 리스트를 추출
    region_id = data.get('regionId')
    preferences = data.get('preference')

    # region_id와 preferences 검증
    if region_id is None or not isinstance(region_id, int):
        return jsonify({'error': 'regionId must be an integer.'}), 400
    if not preferences or not isinstance(preferences, list):
        return jsonify({'error': 'Preference must be a list of strings.'}), 400

    # preference 문자열을 ID로 매핑
    preference_map = {
        '현실형': 1,
        '탐구형': 2,
        '예술형': 3,
        '사회형': 4,
        '진취형': 5,
        '관습형': 6
    }

    # preference 리스트를 ID 리스트로 변환
    preference_ids = [preference_map.get(pref) for pref in preferences if pref in preference_map]

    # 유효한 preference_id가 없는 경우 오류 반환
    if not preference_ids:
        return jsonify({'error': 'Invalid preference values provided.'}), 400

    # 로깅: 필터링 전에 요청된 region_id와 preference_id 출력
    logging.info(f"Requested region_id: {region_id}, preference_ids: {preference_ids}")

    # region_id와 preference_id 리스트에 포함된 값들이 일치하는 행을 필터링
    filtered_education_df = education_df[(education_df['region_id'] == region_id) & 
                                         (education_df['preference_id'].isin(preference_ids))]

    # 로깅: 필터링 결과 출력
    logging.info(f"Filtered Education DataFrame: {filtered_education_df}")

    # 필터링된 결과에서 'id' 열의 값을 최대 15개 추출
    education_ids = filtered_education_df['id'].tolist()[:15]

    if not education_ids:
        return jsonify({'error': 'No matching education programs found for the given preference_id(s) and region_id.'}), 404

    return jsonify({'education_ids': education_ids})

if __name__ == '__main__':
    # 운영 환경에서는 debug=False로 설정해야 합니다.
    app.run(host='0.0.0.0', port=5000, debug=False)

# from flask import Flask, request, jsonify
# import pandas as pd
# import logging
# import os

# app = Flask(__name__)

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)

# # CSV 파일 경로
# csv_file_path = './2.preference_fill_with_model/data/job_merged_file_with_predictions.csv'

# # CSV 파일이 존재하는지 확인하고 로드
# if os.path.exists(csv_file_path):
#     df = pd.read_csv(csv_file_path)
#     logging.info("CSV file loaded successfully.")
# else:
#     logging.error(f"CSV file not found at path: {csv_file_path}")
#     df = pd.DataFrame()  # 데이터 프레임을 빈 상태로 초기화

# @app.route('/get_job_id', methods=['POST'])
# def get_job_id():
#     # 요청에서 JSON 데이터를 가져옴
#     data = request.get_json()

#     # JSON에서 regionId와 preference 리스트를 추출
#     region_id = data.get('regionId')
#     preferences = data.get('preference')

#     # region_id와 preferences 검증
#     if region_id is None or not isinstance(region_id, int):
#         return jsonify({'error': 'regionId must be an integer.'}), 400
#     if not preferences or not isinstance(preferences, list):
#         return jsonify({'error': 'Preference must be a list of strings.'}), 400

#     # preference 문자열을 ID로 매핑
#     preference_map = {
#         '현실형': 1,
#         '탐구형': 2,
#         '예술형': 3,
#         '사회형': 4,
#         '진취형': 5,
#         '관습형': 6
#     }

#     # preference 리스트를 ID 리스트로 변환
#     preference_ids = [preference_map.get(pref) for pref in preferences if pref in preference_map]

#     # 유효한 preference_id가 없는 경우 오류 반환
#     if not preference_ids:
#         return jsonify({'error': 'Invalid preference values provided.'}), 400

#     # 로깅: 필터링 전에 요청된 region_id와 preference_id 출력
#     logging.info(f"Requested region_id: {region_id}, preference_ids: {preference_ids}")

#     # region_id와 preference_id 리스트에 포함된 값들이 일치하는 행을 필터링
#     filtered_df = df[(df['region_id'] == region_id) & (df['preference_id'].isin(preference_ids))]

#     # 로깅: 필터링 결과 출력
#     logging.info(f"Filtered DataFrame: {filtered_df}")

#     # 필터링된 결과에서 'id' 열의 값을 최대 15개 추출
#     job_ids = filtered_df['id'].tolist()[:15]

#     if not job_ids:
#         return jsonify({'error': 'No matching jobs found for the given preference_id(s) and region_id.'}), 404

#     return jsonify({'job_ids': job_ids})

# if __name__ == '__main__':
#     # 운영 환경에서는 debug=False로 설정해야 합니다.
#     app.run(host='0.0.0.0', port=5000, debug=False)



# from flask import Flask, request, jsonify
# import pandas as pd

# app = Flask(__name__)

# # CSV 파일을 미리 로드하여 메모리에 저장
# df = pd.read_csv('./2.preference_fill_with_model/data/job_merged_file_with_predictions.csv')

# @app.route('/get_job_id', methods=['GET'])
# def get_job_id():
#     # GET 요청에서 preference_id와 region_id 파라미터를 받음
#     preference_ids = request.args.getlist('preference_id', type=int)  # preference_id를 리스트 형식으로 받기
#     region_id = request.args.get('region_id', type=int)

#     if not preference_ids or region_id is None:
#         return jsonify({'error': 'preference_id and region_id are required parameters.'}), 400

#     # region_id와 preference_id 리스트에 포함된 값들이 일치하는 행을 필터링
#     filtered_df = df[(df['region_id'] == region_id) & (df['preference_id'].isin(preference_ids))]

#     # 필터링된 결과에서 'id' 열의 값을 최대 15개 추출
#     job_ids = filtered_df['id'].tolist()[:15]  # 최대 15개의 id 값을 반환

#     if not job_ids:
#         return jsonify({'error': 'No matching jobs found for the given preference_id(s) and region_id.'}), 404

#     return jsonify({'job_ids': job_ids})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
