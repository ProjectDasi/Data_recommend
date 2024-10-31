import pandas as pd
from datetime import datetime

# 절대 경로로 파일 경로 지정
file_path = "./1.1 crawling_education/data/부산평생교육정보망_final_3.csv"
df = pd.read_csv(file_path)

# 열 이름을 영어로 변경
df.rename(columns={
    '강좌명': 'title',
    '학습기관': 'organization',
    '학습기간': 'progress_period',
    '접수기간': 'application_period',
    '강사명': 'instructor',
    '수강료': 'tuition',
    '교육방법': 'teaching_method',
    '교육대상': 'target',
    '교육주기': 'cycle',
    '교육정원': 'capacity',
    '교육장소': 'place',
    '교육문의전화': 'phone',
    '접수방법': 'apply',
    '직업능력개발_훈련비지원': 'support',
    '교육공고_링크': 'link',
    '조회수': 'views'
}, inplace=True)

# 'application_period'와 'progress_period'을 '~'로 나누어 새로운 두 개의 열로 분리
df[['application_start', 'application_end']] = df['application_period'].str.split('~', expand=True)
df[['progress_start', 'progress_end']] = df['progress_period'].str.split('~', expand=True)

# 문자열 형식의 날짜를 datetime 형식으로 변환
df['application_start'] = pd.to_datetime(df['application_start'].str.strip(), format='%Y.%m.%d', errors='coerce')
df['application_end'] = pd.to_datetime(df['application_end'].str.strip(), format='%Y.%m.%d', errors='coerce')
df['progress_start'] = pd.to_datetime(df['progress_start'].str.strip(), format='%Y.%m.%d', errors='coerce')
df['progress_end'] = pd.to_datetime(df['progress_end'].str.strip(), format='%Y.%m.%d', errors='coerce')

# 기존 'application_period'와 'progress_period' 열 삭제
df = df.drop(columns=['application_period', 'progress_period'])

# 'apply' 열에서 '접수' 단어 삭제
df['apply'] = df['apply'].str.replace('접수', '')

# 'apply' 열의 빈 값을 '온라인'으로 대체 (NaN 처리 포함)
df['apply'] = df['apply'].fillna('온라인')  # NaN 값을 '온라인'으로 대체
df['apply'] = df['apply'].replace('^\s*$', '온라인', regex=True)  # 공백 문자열을 '온라인'으로 대체

df['teaching_method'] = df['teaching_method'].fillna('관련링크 참조')
df['teaching_method'] = df['teaching_method'].replace('^\s*$', '관련링크 참조', regex=True)

# 빈 열 추가
df['source'] = '부산평생교육정보망'
# df['empty_column_1'] = ''
# df['empty_column_2'] = ''

# 현재 날짜를 기준으로 상황 열 추가
current_date = datetime.now()

def determine_situation(row):
    if pd.isna(row['application_start']) or pd.isna(row['application_end']):
        return '알 수 없음'
    if current_date < row['application_start']:
        return '접수예정'
    elif row['application_start'] <= current_date <= row['application_end']:
        return '접수중'
    else:
        return '접수마감'

df['situation'] = df.apply(determine_situation, axis=1)

# 'situation' 열에서 값이 '접수마감'인 행 삭제
# df = df[df['situation'] != '접수마감']

# 'tuition' 열에서 숫자가 포함된 행을 '유료'로 변경
df['tuition'] = df['tuition'].apply(lambda x: '유료' if any(char.isdigit() for char in str(x)) else '무료')

# 'link' 열에서 'bsbukgu'가 포함된 URL 수정
df['link'] = df['link'].apply(lambda x: x.replace('index.bsbukgu&', 'index.bsbukgu?') if 'bsbukgu' in x else x)

# 원하는 열 순서로 데이터프레임을 재정렬
columns_order = [
    'source',
    'title', 
    'organization', 
    'application_start',  # 신청기간_시작
    'application_end',    # 신청기간_끝
    'progress_start',     # 진행기간_시작
    'progress_end',       # 진행기간_끝
    'apply', 
    'link', 
    'instructor',
    # 'empty_column_1',     # 빈 열
    'phone',
    # 'empty_column_2',     # 빈 열
    'tuition',
    'teaching_method',
    'capacity',
    'place',
    'situation',
    'support',
    'views'
]

df = df[columns_order]

# 결과 확인
print(df.head())

# 변경된 DataFrame을 CSV 파일로 저장
df.to_csv('./1.1 crawling_education/data/부산평생교육정보망_ppp.csv', index=False, encoding='utf-8-sig')

print("데이터 수정 완료!")
