import os
import json
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud

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

# 워드클라우드 시각화를 위해 빈도 정보를 딕셔너리로 변환
wordcloud_data = dict(ingredient_count)

# 워드클라우드 생성
wordcloud = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf', width=800, height=800, background_color='white').generate_from_frequencies(wordcloud_data)

# 워드클라우드 시각화
plt.figure(figsize=(8, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 축 숨기기
plt.show()