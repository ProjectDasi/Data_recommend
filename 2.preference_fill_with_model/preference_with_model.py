import torch
import torch.nn as nn
import pandas as pd
import re
from transformers import BertTokenizer, BertModel
from tqdm import tqdm

# tqdm을 pandas에 통합
tqdm.pandas()

# 전처리 함수 정의
def clean_text(text):
    text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
    return text

# 1. 모델 로드 및 정의
class JobPreferenceModel(nn.Module):
    def __init__(self):
        super(JobPreferenceModel, self).__init__()
        self.bert = BertModel.from_pretrained('beomi/kcbert-large')
        self.classifier = nn.Linear(self.bert.config.hidden_size, 6)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs[1]
        logits = self.classifier(cls_output)
        return logits

# 모델 인스턴스 생성
model = JobPreferenceModel()

# 가중치만 로드하기
checkpoint = torch.load('./2.preference_fill_with_model/model/best_model_weights_with_softmax_job.pth', weights_only=False)
model.load_state_dict(checkpoint['model_state_dict'])  # 가중치만 로드
model.eval()

# 2. 데이터 로드
df = pd.read_csv('./1. crawling/data/job_merged_file_surplus_region(1030).csv')

# 3. 텍스트 데이터 결합 및 정제
combined_texts = (df['title'].fillna('') + " " + df['subtitle'].fillna('') + " " + df['work_category'].fillna(''))
df['cleaned_combined_text'] = combined_texts.progress_apply(clean_text)

# 4. 토크나이저 로드 및 데이터 전처리
tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-base')

def preprocess_texts(texts):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=128)
    return inputs['input_ids'], inputs['attention_mask']

input_ids, attention_mask = preprocess_texts(df['cleaned_combined_text'].tolist())

# 5. 예측 수행
with torch.no_grad():
    outputs = model(input_ids, attention_mask)
    softmax = nn.Softmax(dim=1)
    probabilities = softmax(outputs)
    predicted_ids = torch.argmax(probabilities, dim=1) + 1

# 6. 결과를 DataFrame에 추가
df['preference_id'] = predicted_ids.numpy()

# 'cleaned_combined_text' 열 삭제
df.drop(columns=['cleaned_combined_text'], inplace=True)

# preference.csv 파일 로드
preference_df = pd.read_csv('./2.preference_fill_with_model/data/preference.csv')

# id와 type을 매핑하는 딕셔너리 생성
preference_mapping = dict(zip(preference_df['id'], preference_df['type']))

# preference_id 값을 preference_type으로 변환하는 함수 정의
def map_preference_id_to_type(preference_id):
    return preference_mapping.get(preference_id, "Unknown")

# 7. preference_id를 preference_type으로 변환하여 새로운 열 'preference_type' 추가
df['preference_type'] = df['preference_id'].apply(map_preference_id_to_type)

# preference_type 열을 region_id 앞에 이동
cols = df.columns.tolist()
preference_type_index = cols.index('preference_type')
region_id_index = cols.index('region_id')

# 'preference_type'을 'region_id' 앞에 배치
cols.insert(region_id_index, cols.pop(preference_type_index))
df = df[cols]

# 8. 결과 CSV 파일로 저장
df.to_csv('./2.preference_fill_with_model/data/job_merged_file_with_predictions(1030).csv', index=False, encoding='utf-8-sig')
df.to_json('./2.preference_fill_with_model/data/job_merged_file_with_predictions(1030).json', orient='records', force_ascii=False)

print("Preference Type 변환 및 저장이 완료되었습니다. 결과는 CSV 및 JSON 파일에 저장되었습니다.")

# import torch
# import torch.nn as nn
# import pandas as pd
# import re
# from transformers import BertTokenizer, BertModel
# from tqdm import tqdm

# # tqdm을 pandas에 통합
# tqdm.pandas()

# # 전처리 함수 정의
# def clean_text(text):
#     text = re.sub(r'style=[^>]*>', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'<(iframe|div|td)[^>]*>.*?</\1>', '', text, flags=re.IGNORECASE | re.DOTALL)
#     text = re.sub(r'<br\s*/?>', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'\bbr\b', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'[^\w\s]', '', text)
#     text = re.sub(r'\s+', ' ', text).strip()
#     text = re.sub(r'[\U00010000-\U0010ffff]', '', text, flags=re.UNICODE)
#     return text

# # 1. 모델 로드 및 정의
# class JobPreferenceModel(nn.Module):
#     def __init__(self):
#         super(JobPreferenceModel, self).__init__()
#         self.bert = BertModel.from_pretrained('beomi/kcbert-base')
#         self.classifier = nn.Linear(self.bert.config.hidden_size, 6)

#     def forward(self, input_ids, attention_mask):
#         outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
#         cls_output = outputs[1]
#         logits = self.classifier(cls_output)
#         return logits

# # 모델 인스턴스 생성
# model = JobPreferenceModel()

# # 가중치만 로드하기
# checkpoint = torch.load('./2.preference_fill_with_model/model/best_model_weights_with_softmax.pth', weights_only=False)
# model.load_state_dict(checkpoint['model_state_dict'])  # 가중치만 로드
# model.eval()

# # 2. 데이터 로드
# df = pd.read_csv('./1.crawling/data/job_merged_file_surplus_region(0903).csv')

# # 3. 텍스트 데이터 결합 및 정제
# combined_texts = (df['title'].fillna('') + " " + df['subtitle'].fillna('') + " " + df['work_category'].fillna(''))
# df['cleaned_combined_text'] = combined_texts.progress_apply(clean_text)

# # 4. 토크나이저 로드 및 데이터 전처리
# tokenizer = BertTokenizer.from_pretrained('beomi/kcbert-base')

# def preprocess_texts(texts):
#     inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=128)
#     return inputs['input_ids'], inputs['attention_mask']

# input_ids, attention_mask = preprocess_texts(df['cleaned_combined_text'].tolist())

# # 5. 예측 수행
# with torch.no_grad():
#     outputs = model(input_ids, attention_mask)
#     softmax = nn.Softmax(dim=1)
#     probabilities = softmax(outputs)
#     predicted_ids = torch.argmax(probabilities, dim=1) + 1

# # 6. 결과를 DataFrame에 추가
# df['preference_id'] = predicted_ids.numpy()

# # 'cleaned_combined_text' 열 삭제
# df.drop(columns=['cleaned_combined_text'], inplace=True)

# # 결과 CSV 파일로 저장
# df.to_csv('./2.preference_fill_with_model/data/job_merged_file_with_predictions(0903).csv', index=False, encoding='utf-8-sig')

# print("Preference ID 예측이 완료되었습니다. 결과는 './data/job_merged_file_with_predictions.csv' 파일에 저장되었습니다.")

