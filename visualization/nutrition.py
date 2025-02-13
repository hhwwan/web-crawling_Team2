import json
import requests
import concurrent.futures
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows에서 한글 폰트 경로를 설정)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우 'Malgun Gothic'을 사용

# API 설정
API_KEY = "AIzaSyBxPz3lopyrSdiisdbb49Bh9CoAnyiMie8"  # 구글 번역 API 키
USDA_API_KEY = "NncATZrKuB07r2DmsliUslTXTnxfdYmfDDqpiod9"  # USDA API 키
Translate_BASE_URL = "https://translation.googleapis.com/language/translate/v2"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def translate_text(text, target_language="en"):
    """
    텍스트를 지정된 언어로 번역합니다.
    :param text: 번역할 텍스트 (str)
    :param target_language: 목표 언어 (기본값: 영어)
    :return: 번역된 텍스트 (str)
    """
    url = f"{Translate_BASE_URL}?key={API_KEY}"
    params = {
        "q": text,
        "target": target_language
    }
    
    response = requests.post(url, data=params)
    if response.status_code == 200:
        result = response.json()
        return result["data"]["translations"][0]["translatedText"]
    else:
        raise Exception(f"Translation API error: {response.status_code}")

def get_nutrition_info(ingredient):
    """
    주어진 재료에 대한 영양 성분 정보를 반환합니다.
    :param ingredient: 재료 이름 (str)
    :return: 영양 성분 정보 (dict)
    """
    # 재료명을 영어로 번역
    ingredient_en = translate_text(ingredient)

    # USDA API 설정
    params = {
        "query": ingredient_en,
        "pageSize": 1,
        "api_key": USDA_API_KEY
    }
    response = requests.get(USDA_BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("foods"):
            food = data["foods"][0]
            nutrients = food.get("foodNutrients", [])
            # 안전하게 영양 성분 정보 추출
            nutrition_info = {
                "name": food.get("description", "Unknown"),
                "calories": next((item["value"] for item in nutrients if item["nutrientName"] == "Energy"), "N/A"),
                "protein": next((item["value"] for item in nutrients if item["nutrientName"] == "Protein"), "N/A"),
                "fat": next((item["value"] for item in nutrients if item["nutrientName"] == "Total lipid (fat)"), "N/A"),
                "carbohydrates": next((item["value"] for item in nutrients if item["nutrientName"] == "Carbohydrate, by difference"), "N/A")
            }
            return nutrition_info
    return {"error": f"No data found for {ingredient}"}

def process_json_file(json_file):
    """
    JSON 파일의 재료를 읽고 영양 성분 정보를 출력합니다.
    :param json_file: JSON 파일 경로 (str)
    """
    with open(json_file, "r", encoding="utf-8") as file:
        recipes = json.load(file)

    for recipe in recipes:
        print(f"\nRecipe: {recipe['Title']}")
        ingredients = recipe.get("Ingredients", {})

        # 영양 성분 합계를 위한 변수 초기화
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbohydrates = 0

        # 병렬로 영양 성분 정보를 요청하기 위해 ThreadPoolExecutor 사용
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 각 재료에 대해 영양 정보를 비동기적으로 요청
            future_to_ingredient = {executor.submit(get_nutrition_info, name): name for name in ingredients.keys()}
            
            for future in concurrent.futures.as_completed(future_to_ingredient):
                name = future_to_ingredient[future]
                nutrition_info = future.result()
                
                if "error" in nutrition_info:
                    print(nutrition_info["error"])
                else:
                    calories = nutrition_info["calories"]
                    protein = nutrition_info["protein"]
                    fat = nutrition_info["fat"]
                    carbohydrates = nutrition_info["carbohydrates"]
                    
                    try:
                        total_calories += float(calories) if calories != "N/A" else 0
                        total_protein += float(protein) if protein != "N/A" else 0
                        total_fat += float(fat) if fat != "N/A" else 0
                        total_carbohydrates += float(carbohydrates) if carbohydrates != "N/A" else 0
                    except ValueError:
                        pass

        # 레시피의 총합 출력
        print("\nTotal Nutritional Information:")
        print(f"Total Calories: {total_calories} kcal")
        print(f"Total Protein: {total_protein} g")
        print(f"Total Fat: {total_fat} g")
        print(f"Total Carbohydrates: {total_carbohydrates} g")

        # 원형 그래프 시각화 (칼로리 제외, 탄단지로만 표시)
        labels = ['단백질', '지방', '탄수화물']
        values = [total_protein, total_fat, total_carbohydrates]
        
        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#66b3ff','#ff9999','#99ff99'])
        
        # 총 칼로리 텍스트 추가 및 텍스트 위치 설정
        total_calories_text = f"총 칼로리: {total_calories} kcal"
        plt.text(0, -1.2, total_calories_text, ha='center', va='center', fontsize=12, color='black')  # 칼로리 텍스트 아래로 이동
        plt.axis('equal')
        plt.show()

# JSON 파일 경로
json_file_path = "recipe_practice.json"  # JSON 파일 경로를 지정하세요

# 프로그램 실행
process_json_file(json_file_path)