# 리눅스 명령어 학습 시뮬레이터

이 프로그램은 리눅스 명령어를 처음 배우는 사용자를 위한 교육용 시뮬레이터입니다. 
Windows 환경에서 리눅스 명령어의 동작을 시각적으로 이해할 수 있도록 도와줍니다.

## 제작자 정보
- 제작자: 김연범
- 이메일: yeonbumk@gmail.com

## 기능

- 상단 패널: Windows 환경에서의 동작을 시각적으로 표시
- 하단 패널: 리눅스 터미널 환경 시뮬레이션
- 지원하는 명령어:
  - ls: 디렉토리 내용 보기
  - cd: 디렉토리 이동
  - pwd: 현재 작업 디렉토리 확인
  - mkdir: 새 디렉토리 생성
  - rm: 파일/디렉토리 삭제
  - cp: 파일/디렉토리 복사
  - mv: 파일/디렉토리 이동
  - cat: 파일 내용 보기
  - touch: 빈 파일 생성
  - clear: 화면 지우기
  - exit: 프로그램 종료
  - echo: 텍스트 출력
  - whoami: 현재 사용자 정보
  - date: 현재 날짜와 시간
  - help: 도움말 정보
  - history: 명령어 히스토리 보기
  - vi/vim: 텍스트 에디터 (기본 모드)
  - nano: 텍스트 에디터 (간단 모드)
  - top: 시스템 프로세스 정보 보기

## 설치 방법

1. Python 3.7 이상이 설치되어 있어야 합니다.
2. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 실행 방법

```
python linux_simulator.py
```

## 사용 방법

1. 프로그램을 실행하면 상단에 Windows 환경 시뮬레이션 패널, 하단에 터미널이 표시됩니다.
2. 하단 터미널에서 리눅스 명령어를 입력하고 Enter 키를 누릅니다.
3. 명령어의 실행 결과가 터미널에 표시되고, 상단 패널에는 Windows 환경에서의 동작이 시각적으로 표시됩니다.

## 명령어 사용 예시

- 디렉토리 작업:
  ```
  ls          # 현재 디렉토리의 내용 보기
  cd /home    # /home 디렉토리로 이동
  pwd         # 현재 디렉토리 경로 확인
  mkdir test  # test 디렉토리 생성
  ```

- 파일 작업:
  ```
  touch file.txt    # 빈 파일 생성
  cat file.txt      # 파일 내용 보기
  rm file.txt       # 파일 삭제
  ```

- 텍스트 편집:
  ```
  vi file.txt       # vi 에디터로 파일 편집
  vim file.txt      # vim 에디터로 파일 편집
  nano file.txt     # nano 에디터로 파일 편집
  ```

- 시스템 정보:
  ```
  whoami    # 현재 사용자 정보
  date      # 현재 날짜와 시간
  top       # 시스템 프로세스 정보 보기
  ```

- 유틸리티:
  ```
  echo "Hello"    # 텍스트 출력
  clear           # 화면 지우기
  help            # 도움말 보기
  history         # 명령어 히스토리 보기
  exit            # 프로그램 종료
  ```

## 주의사항

- 이 프로그램은 실제 리눅스 시스템이 아닌 시뮬레이션 환경입니다.
- 모든 명령어는 실제 Windows 파일 시스템에서 실행됩니다.
- 일부 고급 리눅스 명령어는 지원되지 않습니다. 
