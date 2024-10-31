import pandas as pd
import json

# Excel 파일 경로 설정
file_path = 'C:/Users/lenovo/Desktop/dasi/지원금페이지/지원금.xlsx'

# 엑셀 파일 읽기
excel_data = pd.ExcelFile(file_path)
sheet_data = excel_data.parse('Sheet1')  # 'Sheet1'을 필요한 시트 이름으로 변경 가능

# JSON 변환
json_data = sheet_data.to_dict(orient='records')

# JSON 파일로 저장 경로 설정
json_file_path = 'C:/Users/lenovo/Desktop/dasi/지원금페이지/output1.json'

# JSON 파일로 저장 (이스케이프된 백슬래시 없이 저장)
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
