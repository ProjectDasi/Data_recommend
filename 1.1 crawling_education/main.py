import subprocess

# 절대 경로로 각 스크립트의 경로를 설정
crawling_script_1 = "./1.1 crawling_education/data_crawling/0914부산평생교육정보망.py"
crawling_script_2 = "./1.1 crawling_education/data_crawling/부산일자리정보망.py"
preprocessing_script_1 = "./1.1 crawling_education/data_preprocessing/부산평생교육정보망_typechange.py"
preprocessing_script_2 = "./1.1 crawling_education/data_preprocessing/부산일자리정보망_typechange.py"
merge_script = "./1.1 crawling_education/data_merge/교육크롤링data병합.py"

try:
    # 부산평생교육정보망 크롤링 코드 실행
    print("부산평생교육정보망 크롤링 시작...")
    subprocess.run(["python", crawling_script_1], check=True)
    print("부산평생교육정보망 크롤링  완료!")

    # 부산일자리정보망 크롤링 코드 실행
    print("부산일자리정보망 크롤링 시작...")
    subprocess.run(["python", crawling_script_2], check=True)
    print("부산일자리정보망 크롤링 완료!")

    # 부산평생교육정보망 전처리 코드 실행
    print("부산평생교육정보망 데이터 전처리 시작...")
    subprocess.run(["python", preprocessing_script_1], check=True)
    print("부산평생교육정보망 데이터 전처리 완료!")

    # 부산일자리정보망 전처리 코드 실행
    print("부산일자리정보망 데이터 전처리 시작...")
    subprocess.run(["python", preprocessing_script_2], check=True)
    print("부산일자리정보망 데이터 전처리 완료!")

    # 데이터 합치기 코드 실행
    print("데이터 병합 시작...")
    subprocess.run(["python", merge_script], check=True)
    print("데이터 병합 완료!")

except subprocess.CalledProcessError as e:
    print(f"오류 발생: {e}")
