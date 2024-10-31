import pandas as pd

# 파일 경로
file_path = './data/데이터분석_통합_파일.csv'

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 모든 열을 'merged_column'으로 합치기
df['merged_column'] = df[['company', 'title', 'subtitle', 'work_category', 'details', 'certification']].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

# 'id' 뒤에 'merged_column' 배치 및 기존 열 삭제
columns = list(df.columns)
id_index = columns.index('id')
new_columns = columns[:id_index+1] + ['merged_column']
df = df[new_columns]

# 결과를 CSV 파일로 저장하기
output_file_path = './data/merged_data.csv'
df.to_csv(output_file_path, index=False, encoding='utf-8-sig')




