import pandas as pd
import torch
from transformers import BertModel, BertTokenizer

# 데이터 로드 경로들
file_paths = {
    'combined_cleaned': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)cleaned_education_data_no_nan_fixed(1022).csv',
}

# KC-BERT Large 모델과 토크나이저 로드
tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-large')
model = BertModel.from_pretrained('beomi/kcbert-large')

# GPU 사용 여부 확인
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)  # 모델을 GPU로 이동

# 텍스트 데이터를 BERT 입력 형식으로 변환 및 벡터화 함수
def bert_vectorize(text, max_length=512):  # max_length는 최대 512로 설정
    # 입력 텍스트를 토크나이저로 변환 (패딩과 자르기 포함)
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
    inputs = {key: val.to(device) for key, val in inputs.items()}  # 데이터를 GPU로 이동
    
    # 모델을 통해 벡터화
    with torch.no_grad():  # 연산에서 그래디언트를 계산하지 않음
        outputs = model(**inputs)
    
    # [CLS] 토큰 벡터 추출
    cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()  # GPU에서 CPU로 다시 이동 후 넘파이 변환
    return cls_embedding.flatten()

# 각 파일에 대한 벡터화 작업을 수행하는 함수
def process_and_save(file_path, text_column, output_file):
    # 데이터 로드
    data = pd.read_csv(file_path)
    
    # 벡터화된 결과를 담을 리스트
    vectors = []

    # 데이터 벡터화 진행
    for i, row in data.iterrows():
        try:
            vector = bert_vectorize(row[text_column])
            vectors.append([row['id'], *vector.tolist(), row['region_id']])  # id, 벡터, region_id를 함께 추가
        except Exception as e:
            print(f"Error processing text: {row[text_column]}, Error: {e}")
            vectors.append([row['id']] + [0] * 1024 + [row['region_id']])  # 오류 발생 시 0으로 채운 벡터 추가

    # 벡터화된 결과를 데이터프레임으로 변환 (id 및 region_id 포함)
    vectorized_columns = ['id'] + [f'vector_{i}' for i in range(1024)] + ['region_id']
    vectorized_data = pd.DataFrame(vectors, columns=vectorized_columns)

    # 벡터화된 데이터를 CSV로 저장
    vectorized_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"벡터화된 데이터가 다음 위치에 저장되었습니다: {output_file}")

# 1. combined_cleaned 벡터화
process_and_save(file_paths['combined_cleaned'], 'combined_cleaned', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned(1022).csv')


# import pandas as pd
# import torch
# from transformers import BertModel, BertTokenizer

# # 데이터 로드 경로들
# file_paths = {
#     'combined_cleaned': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)cleaned_education_data_no_nan_fixed.csv',
#     'organization': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)organization_data.csv',
# }

# # KC-BERT Large 모델과 토크나이저 로드
# tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-large')
# model = BertModel.from_pretrained('beomi/kcbert-large')

# # GPU 사용 여부 확인
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model.to(device)  # 모델을 GPU로 이동

# # 텍스트 데이터를 BERT 입력 형식으로 변환 및 벡터화 함수
# def bert_vectorize(text, max_length=512):  # max_length는 최대 512로 설정
#     # 입력 텍스트를 토크나이저로 변환 (패딩과 자르기 포함)
#     inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
#     inputs = {key: val.to(device) for key, val in inputs.items()}  # 데이터를 GPU로 이동
    
#     # 모델을 통해 벡터화
#     with torch.no_grad():  # 연산에서 그래디언트를 계산하지 않음
#         outputs = model(**inputs)
    
#     # [CLS] 토큰 벡터 추출
#     cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()  # GPU에서 CPU로 다시 이동 후 넘파이 변환
#     return cls_embedding.flatten()

# # 각 파일에 대한 벡터화 작업을 수행하는 함수
# def process_and_save(file_path, text_column, output_file):
#     # 데이터 로드
#     data = pd.read_csv(file_path)
    
#     # 벡터화된 결과를 담을 리스트
#     vectors = []

#     # 데이터 벡터화 진행
#     for i, row in data.iterrows():
#         try:
#             vector = bert_vectorize(row[text_column])
#             vectors.append([row['id']] + vector.tolist())  # id와 벡터를 함께 추가
#         except Exception as e:
#             print(f"Error processing text: {row[text_column]}, Error: {e}")
#             vectors.append([row['id']] + [0] * 1024)  # id와 함께 임시로 0으로 채운 벡터 추가 (오류 방지용)

#     # 벡터화된 결과를 데이터프레임으로 변환 (id 포함)
#     vectorized_columns = ['id'] + [f'vector_{i}' for i in range(1024)]
#     vectorized_data = pd.DataFrame(vectors, columns=vectorized_columns)

#     # 벡터화된 데이터를 CSV로 저장
#     vectorized_data.to_csv(output_file, index=False, encoding='utf-8-sig')
#     print(f"벡터화된 데이터가 다음 위치에 저장되었습니다: {output_file}")

# # 1. combined_cleaned 벡터화
# process_and_save(file_paths['combined_cleaned'], 'combined_cleaned', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned.csv')

# # 2. organization 벡터화
# process_and_save(file_paths['organization'], 'organization', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_organization.csv')



# import pandas as pd
# import torch
# from transformers import BertModel, BertTokenizer

# # 데이터 로드 경로들
# file_paths = {
#     'combined_cleaned': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)cleaned_education_data_no_nan_fixed.csv',
#     'organization': r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\(edu)organization_data.csv',
# }

# # KC-BERT 모델과 토크나이저 로드
# tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-base')
# model = BertModel.from_pretrained('beomi/kcbert-base')

# # GPU 사용 여부 확인
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model.to(device)

# # 텍스트 데이터를 BERT 입력 형식으로 변환 및 벡터화 함수
# def bert_vectorize(text, max_length=300):
#     # 입력 텍스트를 토크나이저로 변환 (패딩과 자르기 포함)
#     inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=max_length)
#     inputs = {key: val.to(device) for key, val in inputs.items()}
    
#     # 모델을 통해 벡터화
#     with torch.no_grad():
#         outputs = model(**inputs)
    
#     # [CLS] 토큰 벡터 추출
#     cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
#     return cls_embedding.flatten()

# # 각 파일에 대한 벡터화 작업을 수행하는 함수
# def process_and_save(file_path, text_column, output_file):
#     # 데이터 로드
#     data = pd.read_csv(file_path)
    
#     # 벡터화된 결과를 담을 리스트
#     vectors = []

#     # 데이터 벡터화 진행
#     for i, row in data.iterrows():
#         try:
#             vector = bert_vectorize(row[text_column])
#             vectors.append([row['id']] + vector.tolist())  # id와 벡터를 함께 추가
#         except Exception as e:
#             print(f"Error processing text: {row[text_column]}, Error: {e}")
#             vectors.append([row['id']] + [0] * 768)  # id와 함께 임시로 0으로 채운 벡터 추가 (오류 방지용)

#     # 벡터화된 결과를 데이터프레임으로 변환 (id 포함)
#     vectorized_columns = ['id'] + [f'vector_{i}' for i in range(768)]
#     vectorized_data = pd.DataFrame(vectors, columns=vectorized_columns)

#     # 벡터화된 데이터를 CSV로 저장
#     vectorized_data.to_csv(output_file, index=False, encoding='utf-8-sig')
#     print(f"벡터화된 데이터가 다음 위치에 저장되었습니다: {output_file}")

# # 1. combined_cleaned 벡터화
# process_and_save(file_paths['combined_cleaned'], 'combined_cleaned', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_combined_cleaned.csv')

# # 2. organization 벡터화
# process_and_save(file_paths['organization'], 'organization', r'C:\Users\lenovo\Desktop\dasi\model_cosine\data\vector_data(edu)\kcbert_vectorized_organization.csv')


