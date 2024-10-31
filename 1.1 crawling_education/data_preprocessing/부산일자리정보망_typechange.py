import pandas as pd
from datetime import datetime

# 절대 경로로 파일 경로 지정
file_path = "./1.1 crawling_education/data/부산일자리정보망_final_2.csv"
df = pd.read_csv(file_path)

# 열 이름을 영어로 변경
df.rename(columns={
    '강좌명': 'title',
    '기관명': 'organization',
    '대상': 'target',
    '신청기간': 'application_period',
    '진행기간': 'progress_period',
    '신청방법': 'apply',
    '링크': 'link',
    '담당자': 'manager',
    '담당부서': 'charge',
    '전화번호': 'phone',
    '이메일': 'email',
    '상세보기 링크': 'view_details_link',
    '세부사항': 'details',
    '조회수' : 'views'
}, inplace=True)

# 'application_period'와 'progress_period'을 '~'로 나누어 새로운 두 개의 열로 분리
df[['application_start', 'application_end']] = df['application_period'].str.split('~', expand=True)
df[['progress_start', 'progress_end']] = df['progress_period'].str.split('~', expand=True)

# 문자열 형식의 날짜를 datetime 형식으로 변환
df['application_start'] = pd.to_datetime(df['application_start'].str.strip(), format='%Y-%m-%d %H시')
df['application_end'] = pd.to_datetime(df['application_end'].str.strip(), format='%Y-%m-%d %H시')
df['progress_start'] = pd.to_datetime(df['progress_start'].str.strip(), format='%Y-%m-%d')
df['progress_end'] = pd.to_datetime(df['progress_end'].str.strip(), format='%Y-%m-%d')

# 기존 'application_period'와 'progress_period' 열 삭제
df = df.drop(columns=['application_period', 'progress_period'])

df['source'] = '부산일자리정보망'

# 'apply' 열의 빈 값을 '기타'로 대체 (NaN 처리 포함)
df['apply'] = df['apply'].fillna('기타')  # NaN 값을 '기타'로 대체
df['apply'] = df['apply'].replace('^\s*$', '기타', regex=True)  # 공백 문자열을 '기타'로 대체

# 'title' 열에서 '청년' 또는 '신입'이 포함된 행 삭제
# df = df[~df['title'].str.contains('청년|신입', na=False)]
# df = df[~df['details'].str.contains('신입|신규입사자', na=False)]

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

# 'situation' 열에서 값이 '접수마감', '알수없음'인 행 삭제
# df = df[df['situation'] != '접수마감']
# df = df[df['situation'] != '알 수 없음']

# 원하는 열 순서로 데이터프레임을 재정렬
columns_order = [
    'source',
    'title', 
    'organization', 
    'application_start',  # 신청기간_시작
    'application_end',    # 신청기간_끝
    'progress_start',     # 진행기간_시작
    'progress_end',       # 진행기간_끝
    'situation',          # 접수 상태
    'apply', 
    'link', 
    'manager', 
    'charge', 
    'phone', 
    'email', 
    'view_details_link',
    'details',
    'views'
]

df = df[columns_order]

# 결과 확인
print(df.head())

# 변경된 DataFrame을 CSV 파일로 저장
df.to_csv('./1.1 crawling_education/data/부산일자리정보망_ppp.csv', index=False, encoding='utf-8-sig')

print("데이터 수정 완료!")

# # DataFrame을 JSON 파일로 저장
# output_json_path = 'C:/Users/SAMSUNG/Desktop/다시_크롤링0819/data/changed_file.json'
# df.to_json(output_json_path, orient='records', force_ascii=False, lines=True)

# print("데이터 수정 및 JSON 파일 저장 완료!")
