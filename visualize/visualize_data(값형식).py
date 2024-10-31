# 필요한 라이브러리 설치
# pip install konlpy wordcloud matplotlib

from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json
import pandas as pd

# 엑셀 파일 읽기 (사용자 환경에 맞게 경로 수정)
df = pd.read_csv('./2.preference_fill_with_model/data/job_merged_file_with_predictions(0920).csv')

# 'source' 열에서 '국민 일자리 벼룩시장'인 행을 제외
df_filtered = df[df['source'] != '국민 일자리 벼룩시장']

# 'title' 열에서 텍스트 추출
titles = df_filtered['title'].dropna().tolist()

# Okt 객체 생성 (형태소 분석기)
okt = Okt()

# 불필요한 단어들 (불용어 추가)
stopwords = [
    # 의미가 적은 단어들
    '또', '등', '앞', '생', '를', '여기', '다른', '예', '은', '위해', '다음', '대한', '아주', '그', '도움', '약', '때문', '여러', '더', '이', '의', '및', '것', '내', '나', '수', '게', '말',
    # 시간, 상태, 정도
    '마감', '현재', '시작', '신규', '예정', '최근', '즉시', '매일', '모두', '일부', '신입', '경력', '상시', '최소', '최대', '연속', '주', '일', '월', '분', '시간', '협의', '상담', '긴급', '필수', '선택', '우대', '기본', '조건', '모집', '선발', '자격', '요건', '인원', '서류', '지원', '방식', '중', '신속', '예정',
    # 지역 이름
    '부산','부산광역시', '서울', '경기', '경상', '충청', '전라', '강원', '기장군', '동래구', '사상구', '수영구', '중구', '강서구', '남구', '부산진구', '사하구', '연제구', '해운대구', '금정구', '동구', '북구', '서구', '영도구',
    # 회사나 근로 조건
    '회사', '근로자', '사무실', '채용', '기간', '급여', '연봉', '근무', '월급', '시급', '임금', '복리후생', '주급', '일급', '계약', '정규직', '임시직', '계약직', '알바', '시간제', '파트타임', '풀타임', '상주', '출근', '퇴근', '잔업', '야근', '교대', '점심', '저녁', '휴식', '휴가', '공휴일',
    # 서비스/지원 관련
    '대행', '지급', '제공', '지원', '문의', '상담', '참여', '등록', '신청', '소개', '설명', '안내', '접수', '배정', '배치', '설명서', '결과', '보고서',
    # 동사/형용사
    '가능', '필요', '원함', '바람', '포함','기장','선택', '희망', '진행', '완료', '시행', '유지', '관리', '운영', '점검', '대비', '준비', '조정', '변경', '수정', '접수', '완료', '수행', '처리', '필수',
    # 추가 불용어
    '현장', '초보', '정관', '여자', '인근', '포장', '할아버지', '구인', '시설', '건물','기술','재','오전','일광','원사','드림','롯데','복국','방문','센터','최고','돼지국밥','단순','가공','차','홀','추가','계획','좌동','공무원','주간','고분','공개','숯불','동래','보조','실','도시','제','연산동','지역','용호동','장치','일반','케어','직원','노동자','객','조','닭고기','구합','이수','민원','활동','오후','업체','해운대','하반기','체육','사랑','금수','영도',
    '박해','참여자','통합','다공','완성','재단','마을','마린시티','부업','신라','투잡','브이','광안','임기','관제','정직','해물','남여','담당자','밥상','상례'
    ,'바퀴벌레','하방','업무','파트','공고','통영','자동','진흥','강화유리','양병','전문'
    ,'조리','간접','체인','무직','청사','인력','산업','요원','조리','일자리','단계','조사'
    ,'기계','행사','작업','사원','제조','기준','사업'
]

# 명사 및 필요한 단어 추출 (한 글자 단어 제외)
noun_adj_adv_list = []
for sentence in titles:
    morphs = okt.pos(sentence)
    for word, tag in morphs:
        # 명사(Noun) 또는 알파벳(Alpha)이며 불용어 목록에 포함되지 않고, 길이가 2자 이상인 단어만 추가
        if tag in ['Noun', 'Alpha'] and word not in stopwords and len(word) > 1:
            noun_adj_adv_list.append(word)

# 단어 빈도수 계산
count = Counter(noun_adj_adv_list)

# 워드 클라우드 밀도 줄이기 (단어의 수를 절반으로)
reduced_count = dict(count.most_common(len(count) // 24))

# 노란색 계열을 제외한 색상 목록 생성
colors = [color for name, color in mcolors.TABLEAU_COLORS.items() if 'yellow' not in name]

# 워드 클라우드 생성 (색상 설정됨)
wordcloud = WordCloud(
    font_path='malgun.ttf',  # 한글 폰트 경로 지정
    background_color='white',
    color_func=lambda *args, **kwargs: colors[hash(args[0]) % len(colors)],  # 노란색 제외한 컬러맵 적용
    width=1500,
    height=1000
).generate_from_frequencies(reduced_count)

# 워드 클라우드 시각화
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# 단어와 빈도수를 리스트로 변환 (순위를 추가)
word_freq_list = [{'rank': rank+1, 'word': word, 'freq': freq} for rank, (word, freq) in enumerate(reduced_count.items())]

# JSON 형식으로 저장
with open('./visualize/data/word_frequency_with_rank.json', 'w', encoding='utf-8') as f:
    json.dump(word_freq_list, f, ensure_ascii=False, indent=4)

# JSON 데이터 출력 (원하면 출력)
print(json.dumps(word_freq_list, ensure_ascii=False, indent=4))
