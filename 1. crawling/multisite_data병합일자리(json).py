import os
import pandas as pd

# 파일 경로 설정
file_paths = [
    "./1.crawling/crawling_data_merged/벼룩시장_최종1.csv",
    "./1.crawling/crawling_data_merged/부산경영자총협회_최종final.csv",
    "./1.crawling/crawling_data_merged/워크넷_최종_1.csv",
    "./1.crawling/crawling_data_merged/장노년일자리지원센터_최종1.csv"
]

# 파일 읽기
dfs = [pd.read_csv(file) for file in file_paths]

# 데이터프레임 병합 (조인 형태로)
merged_df = pd.concat(dfs, axis=0, join='outer', ignore_index=True)

# 빈 셀을 null 값으로 채우기
merged_df = merged_df.where(pd.notnull(merged_df), None)

# id 열 추가 (병합 후 인덱스 기반으로 추가)
merged_df.insert(0, 'id', range(1, len(merged_df) + 1))

# 지정된 열 순서
specified_order = [
    'id', '출처', '기업명', '제목', '급여', '등록일', '마감일', '근무지역',
    '경력', '학력', '근무형태', '근무직종', '링크', '연락처','details'
]

# 나머지 열 정렬
remaining_columns = [col for col in merged_df.columns if col not in specified_order]
remaining_columns_sorted = sorted(remaining_columns)

# 최종 열 순서 적용
final_columns = specified_order + remaining_columns_sorted
merged_df = merged_df[final_columns]

# JSON 파일로 저장
output_json_path = "./data/일자리데이터병합.json"
merged_df.to_json(output_json_path, orient='records', lines=True, force_ascii=False)

print(f"JSON 파일이 저장되었습니다: {output_json_path}")
