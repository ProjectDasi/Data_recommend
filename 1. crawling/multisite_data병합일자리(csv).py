import os
import pandas as pd

# 파일 경로 설정
file_paths = [
    "./1. crawling/crawling_data_merged/벼룩시장_최종1.csv",
    "./1. crawling/crawling_data_merged/부산경영자총협회_최종_final_2.csv",
    "./1. crawling/crawling_data_merged/고용24_최종_page_2.csv",
    "./1. crawling/crawling_data_merged/장노년일자리지원센터_최종11.csv"
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
    '경력', '학력', '근무형태', '근무직종', '링크', '연락처','우대사항','조회수'
]

# 나머지 열 정렬
remaining_columns = [col for col in merged_df.columns if col not in specified_order]
remaining_columns_sorted = sorted(remaining_columns)

# 최종 열 순서 적용
final_columns = specified_order + remaining_columns_sorted
merged_df = merged_df[final_columns]

# 엑셀 파일로 저장
output_path = "./1. crawling/crawling_data_merged/job_merged_file(1030).xlsx"
merged_df.to_excel(output_path, index=False)

print(f"파일이 저장되었습니다: {output_path}")


# import os
# import pandas as pd

# # 파일 경로 설정
# file_paths = [
#     "./data/벼룩시장.csv",
#     "./data/부산경영자총협회.csv",
#     "./data/워크넷.csv",
#     "./data/장노년일자리지원센터.csv"
# ]

# # 파일 읽기
# dfs = [pd.read_csv(file) for file in file_paths]

# # 데이터프레임 병합 (조인 형태로)
# merged_df = pd.concat(dfs, axis=0, join='outer', ignore_index=True)

# # id 열 추가 (병합 후 인덱스 기반으로 추가)
# merged_df.insert(0, 'id', range(1, len(merged_df) + 1))

# # 지정된 열 순서
# specified_order = [
#     'id', '출처', '기업명', '제목', '급여', '등록일', '마감일', '근무지역',
#     '경력', '학력', '근무형태', '근무직종', '링크', '연락처'
# ]

# # 나머지 열 정렬
# remaining_columns = [col for col in merged_df.columns if col not in specified_order]
# remaining_columns_sorted = sorted(remaining_columns)

# # 최종 열 순서 적용
# final_columns = specified_order + remaining_columns_sorted
# merged_df = merged_df[final_columns]

# # 엑셀 파일로 저장
# output_path = "./data/merged_data_final.xlsx"
# merged_df.to_excel(output_path, index=False)

# print(f"파일이 저장되었습니다: {output_path}")

