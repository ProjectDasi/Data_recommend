import pandas as pd
import os

# 병합할 CSV 파일 리스트
csv_files = ["./data/job_merged_file_surplus_region.csv", 
             "./data/job_merged_file_surplus_region(0821).csv"]

# 빈 데이터프레임 생성
merged_df = pd.DataFrame()

# 각 CSV 파일을 읽어서 병합
for file in csv_files:
    df = pd.read_csv(file, encoding='utf-8-sig')  # CSV 파일 읽기
    merged_df = pd.concat([merged_df, df], ignore_index=True)  # 데이터프레임 병합

# 병합된 결과를 새로운 CSV 파일로 저장
output_file = "./crawling_data_merged/데이터분석_통합_파일.csv"
merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"병합된 파일이 {output_file}로 저장되었습니다.")