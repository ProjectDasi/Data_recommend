import subprocess

# 스크립트 파일 목록
scripts = ["./1.crawling/워크넷.py","./1.crawling/부산경영자총협회.py","./1.crawling/장노년일자리지원센터.py","./1.crawling/벼룩시장.py"]

# 병합일자리.py

# pre...py


# 각 스크립트 실행
for script in scripts:
    try:
        print(f"Running {script}...")
        subprocess.run(["python", script], check=True)
        print(f"Finished {script}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script}: {e}")