# 1. '1.crawling' 디렉토리에서 워크넷.py, 벼룩시장.py, 부산경영자총협회.py, 장노년일자리지원센터.py 실행 
# 2. multisite_data병합일자리(csv).py을 실행시켜서 각 사이트 별 데이터를 통합
# 3. preprocessing 디렉토리의 preprocessing&merged(일자리).py를 실행시켜 통합된 데이터 전처리 실행 
# 4. '2.preference_fill_with_model'의 preference_with_model.py를 실행시켜 최종 데이터 파일 생성
# 5. 최종 데이터 파일을 kc-bert를 활용하여 벡터값 파일 따로 저장 