import pandas as pd
from pinecone import Pinecone, ServerlessSpec, Index
from transformers import AutoTokenizer, AutoModel
import torch

import os
from pinecone import Pinecone, ServerlessSpec

import os
from pinecone import Pinecone, ServerlessSpec, Index

# Pinecone 인스턴스 생성
pc = Pinecone(
    api_key='5a827264-af2e-4477-b624-53a8f0362baf',  # API 키 입력
)

# 인덱스가 존재하지 않는 경우 생성
if 'dasiproject' not in pc.list_indexes().names():
    pc.create_index(
        name='dasiproject',
        dimension=768,  # BERT 기반 모델의 벡터 차원
        metric='cosine',  # 유사도 계산 방식
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# Index 클래스를 사용해 인덱스에 접근 (호스트 URL 필요)
host_url = 'https://dasiproject-v2qgj6h.svc.aped-4627-b74a.pinecone.io'  # 본인의 Host URL 사용
index = Index('dasiproject', host=host_url)

print("Pinecone 인덱스에 성공적으로 연결되었습니다.")



# BERT 모델 및 토크나이저 초기화
tokenizer = AutoTokenizer.from_pretrained("beomi/kcbert-base")
model = AutoModel.from_pretrained("beomi/kcbert-base")

# 벡터 차원 설정
dimension = 768  # BERT 모델의 벡터 차원

# CSV 파일 경로 설정
file_paths = [
    r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\certification_data.csv',
    r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\cleaned_job_data_no_nan_fixed.csv',
    r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\region_name_data.csv'
]

# 데이터 벡터화 함수
def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0, :].numpy()  # [CLS] 토큰의 벡터만 사용
    return embeddings[0]  # 벡터 반환

# 파일마다 데이터를 읽고 Pinecone에 업로드
def process_file(file_path, text_column):
    # CSV 파일 읽기
    df = pd.read_csv(file_path)
    
    # Pinecone에 업로드할 데이터를 준비 (ID와 벡터)
    vectors = []
    for idx, row in df.iterrows():
        text = row[text_column]  # 벡터화할 텍스트가 있는 열
        vector = embed_text(text)  # 텍스트를 벡터화
        vectors.append((str(idx), vector))  # ID는 인덱스 번호 사용

    # 벡터들을 Pinecone에 업로드
    index.upsert(vectors=vectors)
    print(f"{file_path} 데이터가 성공적으로 업로드되었습니다.")

# 각 파일의 텍스트 컬럼 이름에 맞게 호출
process_file(file_paths[0], 'certification')  # 첫 번째 파일
process_file(file_paths[1], 'combined_cleaned')  # 두 번째 파일
process_file(file_paths[2], 'region_name')  # 세 번째 파일

print("모든 데이터가 Pinecone에 업로드되었습니다.")

