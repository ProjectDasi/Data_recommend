import pandas as pd

# 엑셀 파일 로드
work_info = pd.read_excel('./crawling_data_merged/job_transform_column_final_2(0821).xlsx')  # 회사 정보 파일의 경로를 올바르게 대체하세요
region_data = pd.read_csv('./preprocessing/region.csv')

# 새로운 열을 생성하여 지역 ID를 저장
work_info['region_id'] = None

# 회사 정보 데이터프레임의 각 행을 반복
for index, row in work_info.iterrows():
    # 매치가 발견되었는지를 확인하는 플래그
    match_found = False
    
    # 단계 1: 'region_name'을 'subregion'과 비교
    if pd.notna(row['region_name']):
        for i, reg_row in region_data.iterrows():
            if reg_row['subregion'] in row['region_name']:
                work_info.at[index, 'region_id'] = reg_row['id']
                match_found = True
                break

    # 단계 2: 'region_name'이 없을 경우, 'company'을 'subregion'과 비교
    if not match_found and pd.isna(row['region_name']):
        if pd.notna(row['company']):  # 'company'이 NaN이 아닌지 확인
            for i, reg_row in region_data.iterrows():
                if reg_row['subregion'] in row['company']:
                    work_info.at[index, 'region_id'] = reg_row['id']
                    match_found = True
                    break

    # 단계 3: 매치가 없을 경우, 'details'을 'subregion'과 비교
    if not match_found:
        if pd.notna(row['details']):  # 'details'이 NaN이 아닌지 확인
            for i, reg_row in region_data.iterrows():
                if reg_row['subregion'] in row['details']:
                    work_info.at[index, 'region_id'] = reg_row['id']
                    match_found = True
                    break

# 새 열이 추가된 회사 정보를 JSON 형식으로 저장
output_file_path = './data/job_merged_file_surplus_region(0821).json'
work_info.to_json(output_file_path, orient='records', lines=True, force_ascii=False)

print(f"새로운 열이 추가된 회사 정보가 {output_file_path}에 저장되었습니다.")


