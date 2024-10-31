import pandas as pd

# CSV 파일 불러오기
file_path = './labeling_for_train/data/데이터분석_통합_파일.csv'
df = pd.read_csv(file_path)

# NaN 값을 빈 문자열로 대체 (문자열 열에만 적용)
str_columns = df.select_dtypes(include=['object']).columns
df[str_columns] = df[str_columns].fillna('')

# 'title', 'subtitle', 'work_category', 'certification' 열을 통합하여 'combined' 열 생성, 빈 부분은 제외하고 결합
df['combined'] = df[['title', 'subtitle', 'work_category', 'certification','details','certification']].agg(lambda x: ' / '.join(filter(None, x)), axis=1)

# 'id' 열과 새로 만든 'combined' 열만 남기고, 나머지 열 삭제
df_combined = df[['id', 'combined']].copy()

# 'label'과 'label2' 빈 열 추가
df_combined.loc[:, 'label'] = ''
df_combined.loc[:, 'label2'] = ''

# 통합된 데이터프레임을 CSV 파일로 저장 (한글 인코딩 지원을 위해 UTF-8 사용)
output_file_path = './labeling_for_train/testdata/전처리테스트용.csv'
df_combined.to_csv(output_file_path, index=False, encoding='utf-8-sig')

# 저장된 파일 경로 출력
print(output_file_path)