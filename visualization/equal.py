import os
import json
import matplotlib.pyplot as plt
from collections import Counter

# 한글 폰트 설정 (Windows에서 한글 폰트 경로를 설정)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우 'Malgun Gothic'을 사용

# JSON 파일 경로 (하나의 파일일 경우)
file_path = r'C:\Users\hwan\Desktop\web_crawling_Team2\recipes.json'

# 재료 key들을 저장할 리스트
ingredients_keys = []

# JSON 파일 읽기
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

        # 만약 data가 리스트라면, 각 레시피마다 "Ingredients" 부분에서 key들 추출
        if isinstance(data, list):
            for recipe in data:
                ingredients = recipe.get("Ingredients", {})
                ingredients_keys.extend(ingredients.keys())
        # data가 리스트가 아니면 (예: 하나의 레시피만 포함된 경우)
        elif isinstance(data, dict):
            ingredients = data.get("Ingredients", {})
            ingredients_keys.extend(ingredients.keys())

# 재료 key들의 빈도 계산 (Counter 사용)
ingredient_count = Counter(ingredients_keys)

# 상위 10개 재료 추출
top_10_ingredients = ingredient_count.most_common(10)

# 시각화
ingredients, counts = zip(*top_10_ingredients)  # 재료 이름과 빈도를 분리

# plt.figure(figsize=(10, 6))
# plt.bar(ingredients, counts, color='skyblue')
# plt.xlabel('Ingredients')
# plt.ylabel('Frequency')
# plt.title('Top 10 Most Frequent Ingredients Keys in JSON File')
# plt.xticks(rotation=45, ha='right')  # X축 라벨 회전
# plt.tight_layout()
# plt.show()

# 색상 맵 생성 (tab10 색상 맵을 사용)
colors = plt.cm.tab10(range(len(top_10_ingredients)))

# 원형 그래프 그리기
plt.figure(figsize=(8, 8))
plt.pie(counts, labels=ingredients, autopct='%1.1f%%', colors=colors, startangle=90)

# 제목 설정
plt.title('Top 10 Most Frequent Ingredients Keys in JSON File')

# 그래프를 원형으로 만듦
plt.axis('equal')  # 원이 왜곡되지 않도록 비율을 맞춤

# 그래프 출력
plt.show()