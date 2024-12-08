# 크롤한 웹 데이터로 만들어보는 시각화 웹 서비스 
## 주제: 웹 크롤링 기반 재료 맞춤형 레시피 추천 및 영양 정보 시각화 서비스
## Programmers 데브코스 Data Engineering 5기 
- <b>Team</b>`둘다하자`
  - <b>김동환</b> `웹 크롤링` `백엔드` `데이터 시각화`<br>
  - <b>이찬회</b> `웹 크롤링` `백엔드` `메인 페이지 프론트엔드`<br>
  - <b>유혜승</b> `웹 크롤링` `백엔드` `데이터 시각화`<br>
  - <b>윤여준</b> `웹 크롤링` `백엔드` `세부 페이지 프론트엔드`
- **프로젝트 진행 기간**: 2024.12.02 ~ 2024.12.09

## 목차
###### 1. 프로젝트 개요
###### 2. 활용 기술 및 프레임워크
###### 3. 프로젝트 결과
###### 4. 결론  

## 1. 프로젝트 개요
### 특징
- **웹 크롤링 데이터 활용**: 인터넷에서 수집한 실제 데이터를 기반으로 서비스 제공.
- **재료 기반 레시피 추천**: 보유 재료에 맞는 레시피를 맞춤 추천.
- **영양 정보 및 조리 방법 제공**: 상세한 재료 정보와 건강 관리에 도움을 주는 영양 성분 분석.
- **데이터 시각화**: 레시피와 영양 정보를 차트로 시각화하여 직관적인 정보 제공.
- **사용자 중심 인터페이스**: 직관적이고 간결한 UI/UX 설계.
 
### 선정 배경
바쁜 일상 속에 현대인들의 **유기농 및 친환경 제품**의 소비가 급증
- 소비자들이 건강을 중시하는 경향이 뚜렷하게 나타나고 있음
- 식품 산업의 유기농, 친환경, 제로 칼로리 제품 등 다양한 건강지향적인 옵션을 적극 출시
- 하지만 요리에 필요한 재료를 준비하거나 다양한 요리법을 찾는 과정이 복잡함
- 특히, 남은 재료를 활용하거나 건강에 맞춘 레시피를 찾는 일은 매우 번거로움
> [식생활 트렌드…음식 취향 다양화․세분화, 건강한 식생활 관심 증가 변화 확인, 메디컬 월드 뉴스, 2021.12.28](https://www.medicalworldnews.co.kr/m/view.php?idx=1510946998)

> [건강한 먹거리 찾는 소비자 증가…친환경·유기농 식품 시장 '쑥쑥', 뉴시스, 2021.09.14](https://www.newsis.com/view/NISX20210913_0001581455)

### 목적 
> 위의 문제를 해결하기 위한 **레시피 추천 서비스**를 제공하여 사용자의 요리 경험 개선
<br>

## 2. 활용 기술 및 프레임워크
### Programming Language
`Python`
  
### Frontend 
`HTML` `CSS` `Bootstrap`

### Backend
`Django`

### Crawling, Data
`BeautifulSoup` `Json` `Google Translate API` `USDA Food Data Central API`

### Visualization
`Matplotlib` `Seaborn` `Wordcloud`

### Comm & Collab
`Slack` `Git/Github` `Notion` `Zep`
<br>
<br>

## 3. 프로젝트 결과
### Crawling
```
Python을 기반으로 Requests를 이용해 웹 페이지 HTML을 요청 이후 BeautifulSoup으로 HTML을 파싱하여 필요한 데이터를 추출

**정규 표현식(re)**으로 URL 패턴을 분석한 뒤 json을 사용해 100,000개의 데이터를 파일로 저장

데이터 가공 및 저장 과정을 ETL 방식으로 구현 

tqdm을 활용해 진행 상황을 시각화하고, time.sleep으로 요청 간 지연을 추가하여 서버 과부하를 방지
```
1. 페이지 데이터 추출<br>
> 크롤링을 진행할 페이지를 이용해 각 페이지마다 레시피가 들어있는 URL 추출`

2. 페이지 데이터에서 필요한 부분 추출(Extract)<br>
> 레시피 페이지에서 레시피 이름, 재료, 도구, 인분 수, 수행시간, 난이도, 레시피 순서 정보를 추출`

3. 추출된 데이터를 필요한 형식으로 가공 (Transform)<br>
> 위 코드에서 추출된 데이터를 이용해 Key-Value 형식으로 가공`

4. 가공한 데이터를 JSON 파일에 저장<br>
> Key-Value 형식의 데이터를 Django에서 이용하기 쉽도록 JSON파일로 저장`

5. 데이터 전처리<br>
> 수집한 데이터를 확인한 후 오염이 있었던 Tools 칼럼과 제목이 Unknown처럼 제대로 수집되지 않은 데이터를 삭제`

### Visualization
> Python의 **Matplotlib**, **Seaborn**, **WordCloud** 등을 활용하여 수집한 데이터에 시각화 진행

- 레시피 재료 빈도 WordCloud<br>
`크롤링으로 수집한 데이터 중 가장 많이 사용되는 재료가 무엇인지 한 눈에 보기 위한 시각화`
<img src="https://github.com/user-attachments/assets/a7b9e7c5-8315-4f08-8339-6d7722e84538"  width="600" height="350"/><br>

- 레시피 시간 분포 막대 그래프<br>
`크롤링으로 수집한 데이터 중 레시피 수행 시간의 분포를 파악하기 위해 범주별로 막대 그래프를 그려 시각화`
<img src="https://github.com/user-attachments/assets/2b106138-454f-4f4e-b6b3-4f552d3d6e2d"  width="600" height="350"/><br>

- 검색 재료와 함께 사용되는 재료 막대 그래프<br>
`검색한 재료와 함께 사용되는 재료와 빈도수를 알기 쉽게 시각화`
<img src="https://github.com/user-attachments/assets/ac5eb7c4-a4e5-4737-acda-8e131a14ff33"  width="600" height="350"/><br>

- 레시피 영양 성분 파이 차트<br>
`API를 통해 재료 이름을 영어로 번역하고 재료의 영양정보를 검색하고 분석 진행`<br>
`분석한 데이터를 통해 총 칼로리를 파악하여 파이 차트로 시각화`
<img src="https://github.com/user-attachments/assets/a31358ce-8f81-4018-be17-245298075ac2"  width="600" height="450"/><br>

### Frontend
> 메인페이지(index.html)
- 재료를 검색하면 해당 재료를 사용하는 레시피와 레시피에 사용되는 다른 재료들을 막대그래프와 워드클라우드로 시각화
- 난이도별,  조리시간별 필터링 검색 구현
- 페이지네이션 구현
  
<img src="https://github.com/user-attachments/assets/45822a6e-50d8-4209-9f2d-6fdfdce61f9c"  width="600" height="450"/><br>

<img src="https://github.com/user-attachments/assets/7a0f9fb0-af59-42de-b492-c85fc8e2fbce"  width="600" height="450"/><br>\


> 상세페이지(recipe_detail.html)
- 메인페이지에서 재료 검색시 나온 레시피의 상세 정보 페이지
- 레시피에 필요한 재료, 조리방법등을 기재
- 레시피에 들어가는 영양소를 파이 차트로 시각화

<img src="https://github.com/user-attachments/assets/19aa9e35-6e04-4455-96fa-09699df6b276"  width="600" height="450"/><br>



※ base.html을 사용해 웹페이지 위,아래 기본 템플릿을 고정 

### Backend
> 메인페이지(index.html)
1. Json 데이터 로드
2. request.get으로 사용자 입력 
3. 빈 검색어, get에 아무런 파라미터도 없을 경우 등 처리
4. 난이도/조리시간별 레시피 필터링
5. 시각화 이미지 생성
6. 페이지네이션
7. 화면 렌더링
   
> 상세페이지(recipe_detail.html)
1. Json 데이터 로드
2. 시각화 이미지 생성
3. 화면 렌더링

<br>
<br>

## 4. 결론
### 요약
- 사용자가 입력한 재료에 맞는 레시피가 출력되고 클릭을 통해 재료 및 영양성분을 확인할 수 있는 웹 서비스
- Django를 중심으로 백엔드, API 연동, 데이터 처리와 시각화까지 통합적으로 구현.
- 웹 크롤링으로 확보한 데이터를 기반으로 사용자 맞춤형 추천 시스템 제공.
- 영양 성분 데이터를 그래프와 함께 제공

### 기대효과
- 사용자 경험 강화: 시각적으로 직관적인 데이터 제공으로 요리 선택 과정이 간단해짐
- 시간 절약: 맞춤형 추천으로 요리 준비 시간 단축
- 건강 증진: 영양소를 시각적으로 보여줌으로써 건강관리 가능

### 아쉬웠던 점
- Git/GitHub를 제대로 활용하지 못 하였으며 특히 branch를 생성하여 활용하는 데 어려움 겪음
- DB(SQLite)를 사용하지 못하고 모든 Data를 Json파일로 저장하여 활용하여 쿼리를 이용할 수 없어 아쉬웠음
