## [2025] 조선대학생 맞춤형 챗봇



---

### 목차
- [프로젝트 소개](#프로젝트-소개)  
- [개발 기간 및 인원](#개발-기간-및-인원)  
- [팀원](#팀원)  
- [기술 스택](#기술-스택)  
- [설치 및 실행 방법](#설치-및-실행-방법)  

---

## 프로젝트 소개

> 조선대학교 재학생을 위한 AI 기반 챗봇입니다.  
> 학사 일정(개강·수강신청·중간·기말고사), 강의 시간표·강의실 위치, 동아리·학내 행사,  
> 식당 메뉴, 학교 공지사항 등 학생들이 자주 묻는 질문에 실시간으로 답변해 줍니다.  
> Rasa 프레임워크를 활용한 자연어 이해(NLU)와 대화 관리로, 웹과 메신저 연동을 통해  
> 언제 어디서나 편리하게 캠퍼스 생활 정보를 얻을 수 있습니다.

---

## 개발 기간 및 인원
- **기간**: 2025.03.10 ~ 2025.06.22  
- **백엔드 팀원**: 3명  
- **프론트 팀원**: 1명  
---

## 팀원

| 이름         | 역할    | GitHub                                        |
|:------------:|:-------:|:----------------------------------------------:|
| 김은효(조장) | 백엔드  | [GitHub](https://github.com/HyoMo-nim)        |
| 정명준       | 백엔드,프론트  | [GitHub](https://github.com/godjun123)        |
| 안민서       | 백엔드  | [GitHub](https://github.com/Minmin939)        |

---

## 기술 스택

- **Environment**
  - 운영체제(OS): Ubuntu 22.04 LTS
- **Backend**
  - 언어: Python 3.8
  - 프레임워크: Rasa Open Source, Flask
- **Database**
  - Json, Excel
- **Frontend**
  - HTML, CSS, JavaScript
- **Version Control**
  - Git, GitHub, GitKraken

---

## 설치 및 실행 방법

1. **레포지토리 클론**
```bash
git clone https://github.com/HYoMo-nim/chosun-chatbot.git
cd chosun-chatbot
```

2. **가상환경 생성 및 활성화 (Ubuntu 기준)**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **필수 패키지 설치**
```bash
pip install -r requirements.txt
```

4. **Rasa 학습 실행(가상환경안에서 학습실행)**
```bash
cd ~/rasa_project
source venv/bin/activate
rasa train
```

5. **Rasa 서버 실행 (NLU + Core)**
```bash
cd ~/rasa_project
source venv/bin/activate
rasa run --enable-api --cors "*" --debug
```

6. **Action 서버 실행**
```bash
cd ~/rasa_project
source venv/bin/activate
rasa run actions
```

7. **Flask 웹 서버 실행 (별도 디렉토리에서)**
```bash
cd ~/rasa_project/web
source ../venv/bin/activate
python3 app.py

```


## 챗봇 시연 화면

![조선대 챗봇 시연 화면](스크린샷%202025-06-22%2015-55-41.png)

8. **웹 접속**
- 웹 브라우저에서 `http://localhost:8000` 접속

> ⚠️ 참고: `menu.json`, `academic_schedule.json` 등은 `data/` 폴더에 위치해야 하며, JSON 형식은 사전에 정의된 구조를 따라야 합니다.
