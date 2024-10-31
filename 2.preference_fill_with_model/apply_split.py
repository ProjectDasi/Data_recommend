import json
import pandas as pd

# 파일에서 JSON 데이터 읽기
input_file_path = './2.preference_fill_with_model/data/education_merged_file_with_predictions(1022).json'
output_learning_program_path = './2.preference_fill_with_model/data/education_merged_file_apply_exception(1022).json'
output_apply_methods_path = './2.preference_fill_with_model/data/education_apply_methods(1022).json'

# JSON 파일 열기
with open(input_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 고유 id를 생성하기 위한 초기 값 설정
program_id_counter = 1
apply_method_id_counter = 1

# 결과를 저장할 리스트 초기화
learning_program_list = []
apply_methods_list = []

# apply 필드에서 사용할 ENUM 타입
apply_method_enum = ['방문', '전화', '온라인', '기타','이메일']

# 데이터 처리
for program in data:
    # 프로그램에 고유 id 부여
    program_id = program_id_counter
    program_id_counter += 1
    
    # learning_program 테이블에 프로그램 관련 정보 추가
    learning_program_entry = {}
    for key, value in program.items():
        if key != 'apply':
            # 숫자인 값은 숫자로 유지
            if key in ['preference_id', 'region_id']:
                learning_program_entry[key] = int(value) if value is not None else None
            else:
                # 빈 문자열이나 공백만 있는 경우 None으로 변환
                learning_program_entry[key] = value.strip() if isinstance(value, str) and value.strip() else None
    
    # 고유 id 추가
    learning_program_entry['id'] = program_id
    learning_program_list.append(learning_program_entry)
    
    # apply 필드를 분리하여 apply_methods 테이블에 추가
    apply_methods = [method.strip() for method in program['apply'].split(',')]
    
    for method in apply_methods:
        apply_method_entry = {
            'id': apply_method_id_counter,
            'program_id': program_id,
            'method': method if method in apply_method_enum else '기타'
        }
        apply_methods_list.append(apply_method_entry)
        apply_method_id_counter += 1

# 결과를 JSON 파일로 저장
with open(output_learning_program_path, 'w', encoding='utf-8') as file:
    json.dump(learning_program_list, file, ensure_ascii=False, indent=4)

with open(output_apply_methods_path, 'w', encoding='utf-8') as file:
    json.dump(apply_methods_list, file, ensure_ascii=False, indent=4)

print(f"Learning program data saved to {output_learning_program_path}")
print(f"Apply methods data saved to {output_apply_methods_path}")
