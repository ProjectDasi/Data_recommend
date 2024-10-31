import pandas as pd

# 데이터 파일 로드
file_path = './data/cleaned_merged_data2.csv'
df = pd.read_csv(file_path)

# 라벨링 기준 키워드 확장 및 '요양' 키워드 추가
def determine_labels(text):
    if pd.isna(text):
        return None, None
    
    labels = {
        '현실형': ['전기', '기계', '공학', '손재주', '조작', '실물적', '기술', '도구', '농부', '군인', '경찰', '소방관', '운동선수', '정비사'],
        '탐구형': ['탐구', '분석', '비판', '창조', '현상', '자연현상', '학술', '지적', '분석적', '물리학자', '생물학자', '화학자', '심리학자', '지질학자', '시장조사'],
        '예술형': ['창의', '유연', '예술', '아름다움', '상상력', '독창', '음악', '미술', '문학', '디자이너', '작가', '무용가', '배우', '소설가'],
        '사회형': ['교류', '협력', '공감', '치료', '타인', '이타', '봉사', '사회복지사', '간호사', '교사', '상담가', '임상치료', '종교지도자', '요양'],
        '진취형': ['목표', '성취', '기획', '리더십', '설득', '추진', '영업', '관리', '정치가', '판사', '변호사', '기업경영', '보험', '판매'],
        '관습형': ['조직', '체계', '규칙', '안정', '시스템', '서류', '사무', '회계사', '경제분석가', '세무사', '경리', '은행사무원', '법무사']
    }
    
    # 텍스트 소문자 변환
    text = text.lower()
    
    # 각 라벨별 점수 초기화
    scores = {label: 0 for label in labels}
    
    # 각 키워드가 텍스트에 포함되어 있는지 확인하여 점수 계산
    for label, keywords in labels.items():
        for keyword in keywords:
            if keyword in text:
                scores[label] += 1
    
    # 점수를 기준으로 내림차순 정렬
    sorted_labels = sorted(scores, key=scores.get, reverse=True)
    
    # 가장 높은 점수의 라벨과 두 번째로 높은 점수의 라벨 반환
    determined_label = sorted_labels[0]
    second_label = sorted_labels[1] if scores[sorted_labels[1]] > 0 else None
    
    return determined_label, second_label

# 데이터프레임에 라벨링 적용
df['label'], df['label2'] = zip(*df['combined'].apply(determine_labels))

# CSV 파일로 저장 (한글 인코딩 가능하도록 utf-8-sig 사용)
output_path = './data/labeled_data_with_label2.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

# CSV 파일 경로 출력
print(f"CSV 파일이 저장되었습니다: {output_path}")



