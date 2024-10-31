import re
import pandas as pd
import torch
from transformers import BertModel, BertTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
# utils.py
import re
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# TF-IDF 벡터화 함수
# TF-IDF 벡터화를 위한 함수 (단일 텍스트 또는 리스트 모두 처리)
def tfidf_vectorize(text, vectorizer):
    # Ensure text is a string and not a list
    if isinstance(text, list):
        text = ' '.join(text)
    return vectorizer.transform([text]).toarray().flatten()

# 코사인 유사도를 계산하여 상위 N개 반환
def get_top_similarities(input_vector, vectors, top_n=6):
    similarities = cosine_similarity([input_vector], vectors)
    top_indices = similarities[0].argsort()[::-1][:top_n]  # 유사도가 높은 순으로 정렬
    return top_indices, similarities[0][top_indices]

# 텍스트 전처리 함수 (clean_text)
def clean_text(text):
    # None 값을 빈 문자열로 처리
    if text is None:
        return ''
    
    # 특수 문자 제거 (한글, 숫자, 공백만 유지)
    text = re.sub(r'[^\w\s]', '', text)
    
    # 공백 정리
    return text.strip()

# 데이터 로드 함수
def load_vectors(job_file_path, edu_file_path):
    job_vectors = pd.read_csv(job_file_path)
    edu_vectors = pd.read_csv(edu_file_path)
    return job_vectors, edu_vectors

# TF-IDF 벡터화기 생성 및 학습 함수
def create_and_train_tfidf_vectorizer(text_columns):
    vectorizer = TfidfVectorizer()
    vectorizer.fit(text_columns)  # 벡터 학습
    return vectorizer

# # KC-BERT 모델과 토크나이저 로드
# tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-base')
# model = BertModel.from_pretrained('beomi/kcbert-base')
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model.to(device)

# # 기본적인 텍스트 전처리 함수
# def clean_text(text):
#     text = re.sub(r'<[^>]+>', '', text)  # HTML 태그 제거
#     text = re.sub(r'[^\w\s]', '', text)  # 특수 문자 제거
#     text = re.sub(r'\d+', '', text)  # 숫자 제거
#     text = re.sub(r'[A-Za-z]+', '', text)  # 영어 제거
#     text = re.sub(r'\s+', ' ', text).strip()  # 여러 공백을 하나로
#     return text

# # 텍스트 데이터를 BERT 입력 형식으로 변환 및 벡터화
# def bert_vectorize(text):
#     inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=300)
#     inputs = {key: val.to(device) for key, val in inputs.items()}
    
#     with torch.no_grad():
#         outputs = model(**inputs)
#     return outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()

# # 코사인 유사도를 계산하여 상위 N개 반환
# def get_top_similarities(input_vector, vectors, top_n=6):
#     similarities = cosine_similarity([input_vector], vectors)
#     top_indices = np.argsort(similarities[0])[::-1][:top_n]  # 유사도가 높은 순으로 정렬
#     return top_indices, similarities[0][top_indices]

# ########################################################
# # 단어 일치도 계산 함수

# def calculate_word_overlap(text1, text2):
#     words1 = set(text1.split())  # 첫 번째 텍스트의 단어를 세트로 변환
#     words2 = set(text2.split())  # 두 번째 텍스트의 단어를 세트로 변환
#     return len(words1 & words2)  # 두 텍스트에서 겹치는 단어의 수 반환

# # 파일 내에서 단어 일치도 계산 후 상위 N개의 결과 반환
# def get_top_n_text_similarity(input_text, csv_file, key_column='id', text_column='combined_cleaned', weight_dict=None, n=3):
#     # CSV 파일 로드
#     df = pd.read_csv(csv_file)
    
#     # weight_dict는 특정 키워드(지역명, 자격증명)에 대해 가중치를 더해줌
#     if weight_dict is None:
#         weight_dict = {}
    
#     # 결과를 담을 리스트
#     results = []
    
#     # 각 행에 대해 입력 텍스트와의 일치도 계산
#     for i, row in df.iterrows():
#         row_text = row[text_column]  # 현재 행의 텍스트 데이터 가져오기
#         score = calculate_word_overlap(input_text, row_text)  # 입력 텍스트와의 단어 일치도 계산
        
#         # 가중치가 부여된 항목을 찾고, 그 단어가 포함된 경우 가중치를 더함
#         for keyword, weight in weight_dict.items():
#             if keyword in row_text:
#                 score += weight  # 가중치 추가
        
#         results.append((row[key_column], score))  # 결과 리스트에 (id, 점수) 추가
    
#     # 점수가 높은 순으로 정렬하여 상위 N개 반환
#     results.sort(key=lambda x: x[1], reverse=True)
#     top_n = results[:n]  # 상위 n개 추출
    
#     return [item[0] for item in top_n], [item[1] for item in top_n]  # 상위 n개의 id와 점수 반환


# ########################################################

# # KC-BERT 모델 및 토크나이저 로드
# tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-base')
# model = BertModel.from_pretrained('beomi/kcbert-base')

# # GPU 사용 여부 확인
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model.to(device)

# # 텍스트 전처리 함수 정의
# def clean_text(text):
#     # 1. 모든 HTML 태그 제거
#     text = re.sub(r'<.*?>', '', text)

#     # 2. 특수 문자 제거 (한글, 숫자, 공백, 기본적인 문장 부호는 유지)
#     text = re.sub(r'[^\w\sㄱ-ㅎㅏ-ㅣ가-힣.,?!]', '', text)

#     # 3. 이모지 및 이모티콘 제거
#     text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)

#     # 4. 한자 제거
#     text = re.sub(r'[\u4e00-\u9fff]', '', text)

#     # 5. 영어 텍스트 제거
#     text = re.sub(r'[A-Za-z]', '', text)

#     # 6. 중복된 공백 제거
#     text = re.sub(r'\s+', ' ', text).strip()

#     # 7. 불필요한 반복 문자 제거 (ex: "ㅋㅋㅋㅋ" -> "ㅋㅋ", "ㅎㅎㅎㅎ" -> "ㅎㅎ")
#     text = re.sub(r'(.)\1{2,}', r'\1\1', text)

#     return text

# # KC-BERT를 사용하여 벡터화하는 함수
# def bert_vectorize(text, max_length=300):
#     inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
#     inputs = {key: val.to(device) for key, val in inputs.items()}
#     with torch.no_grad():
#         outputs = model(**inputs)
#     cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
#     return cls_embedding.flatten()

# # 코사인 유사도를 계산하여 상위 N개의 항목을 반환하는 함수
# def get_top_n_cosine_similarity(user_vector, csv_path, n=3):
#     # CSV 파일 로드
#     df = pd.read_csv(csv_path)
#     vectors = df.iloc[:, 1:].values  # id 열을 제외한 벡터 열들 사용
#     cosine_sim = cosine_similarity([user_vector], vectors)[0]
#     top_n_idx = np.argsort(cosine_sim)[-n:][::-1]  # 상위 N개 인덱스 반환
#     return df.iloc[top_n_idx]['id'].tolist(), cosine_sim[top_n_idx].tolist()
