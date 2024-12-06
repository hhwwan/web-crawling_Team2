import json
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import requests
import concurrent.futures
from collections import Counter
from io import BytesIO
from django.shortcuts import render
from django.core.paginator import Paginator


# 한글 폰트 설정 (Windows에서 한글 폰트 경로를 설정)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우 'Malgun Gothic'을 사용

# API 설정
API_KEY = "AIzaSyBxPz3lopyrSdiisdbb49Bh9CoAnyiMie8"  # 구글 번역 API 키
USDA_API_KEY = "NncATZrKuB07r2DmsliUslTXTnxfdYmfDDqpiod9"  # USDA API 키
Translate_BASE_URL = "https://translation.googleapis.com/language/translate/v2"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# JSON 파일 로드 함수
def load_recipes():
    with open("data/recipes.json", "r", encoding="utf-8") as file:
        recipes = json.load(file)
    return recipes

# 메인 페이지 뷰 함수
def index(request):
    recipes = load_recipes()  # JSON 데이터 로드

    # GET 파라미터
    query = request.GET.get("ingredient", "")  # 재료 검색
    selected_level = request.GET.get("level", "")  # Level 검색
    selected_time = request.GET.get("time", "")  # Time 검색
    page_number = request.GET.get("page", 1)  # 페이지 번호
    error_message = None  # 에러 메시지 초기화

    # 초기 상태 처리
    if not request.GET:  # GET 요청에 아무런 파라미터도 없을 경우
        return render(
            request,
            "index.html",
            {
                "recipes": [],  # 빈 리스트 전달
                "query": "",
                "unique_levels": sorted(set(recipe["Level"] for recipe in recipes)),
                "selected_level": "",
                "selected_time": "",
                "error_message": None,
                "graph_url": None,
                "page_obj": None,  # 페이지 객체 초기화
            },
        )

    # 빈 검색어 처리
    if not query.strip():
        error_message = "검색어를 입력해주세요."
        filtered_recipes = []
    else:
        # 레시피 필터링
        filtered_recipes = recipes
        if query:
            filtered_recipes = [
                recipe
                for recipe in filtered_recipes
                if query in recipe.get("Ingredients", {})
            ]
        if selected_level:
            filtered_recipes = [
                recipe
                for recipe in filtered_recipes
                if recipe.get("Level") == selected_level
            ]
        if selected_time:
            filtered_recipes = filter_by_time(filtered_recipes, selected_time)

    # 고유한 Level 값 추출
    unique_levels = sorted(set(recipe["Level"] for recipe in recipes))

    # 필터링된 데이터를 기반으로 그래프 생성
    graph_url = generate_graph(filtered_recipes)

    # 페이지네이션
    paginator = Paginator(filtered_recipes, 8)  # 한 페이지당 6개 레시피
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "index.html",
        {
            "recipes": page_obj,  # 페이지 객체 전달
            "query": query,
            "unique_levels": unique_levels,
            "selected_level": selected_level,
            "selected_time": selected_time,
            "error_message": error_message,
            "graph_url": graph_url,  # 그래프 URL
        },
    )

# Time 필터 함수
def filter_by_time(recipes, time_range):
    time_mappings = {
        "10미만": lambda t: t < 10,
        "10분대": lambda t: 10 <= t < 20,
        "20분대": lambda t: 20 <= t < 30,
        "30분대": lambda t: 30 <= t < 40,
        "40분대": lambda t: 40 <= t < 50,
        "50분대": lambda t: 50 <= t < 60,
        "60이상": lambda t: t >= 60,
    }

    if time_range not in time_mappings:
        return recipes

    # Time 값을 숫자로 변환
    def parse_time(recipe_time):
        try:
            return int(recipe_time.split("분")[0])
        except ValueError:
            return 999  # "60분 이상" 같은 경우를 처리

    # 필터 적용
    return [
        recipe
        for recipe in recipes
        if time_mappings[time_range](parse_time(recipe.get("Time", "999분")))
    ]

# 상세 정보 뷰 함수
def recipe_detail(request, recipe_id):
    recipes = load_recipes()  # JSON 데이터 로드
    recipe = next((r for r in recipes if r["ID"] == recipe_id), None)

    if recipe is None:
        return render(request, "404.html", {"message": "Recipe not found"})  # 404 처리

    # "Recipe steps"를 "recipe_steps"로 변경
    recipe["recipe_steps"] = recipe.pop("Recipe steps")

    # 그래프 URL 생성
    graph_url = nutrition_graph(recipe_id)

    return render(request, "recipe_detail.html", {"recipe": recipe, "graph_url": graph_url})

# 조건에 따른 재료 그래프 생성 함수 / url 사용
def generate_graph(filtered_recipes):
    # 재료 key들을 저장할 리스트
    ingredients_keys = []

    # 필터링된 레시피 데이터에서 Ingredients 추출
    for recipe in filtered_recipes:
        ingredients = recipe.get("Ingredients", {})
        ingredients_keys.extend(ingredients.keys())

    # 재료 key들의 빈도 계산 (Counter 사용)
    ingredient_count = Counter(ingredients_keys)

    # 상위 20개 재료 추출
    top_20_ingredients = ingredient_count.most_common(20)

    if not top_20_ingredients:
        return None

    # 시각화 준비
    ingredients, counts = zip(*top_20_ingredients)  # 재료 이름과 빈도를 분리

    # seaborn을 사용하여 막대그래프 그리기
    plt.figure(figsize=(6.4, 4.5))
    sns.barplot(x=list(ingredients), y=list(counts), palette='Blues_d')
    plt.xlabel('Ingredients')
    plt.ylabel('Frequency')
    plt.title('Top 20 Ingredients')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 그래프를 BytesIO 객체에 저장하고 base64로 인코딩
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return graph_url

# 재료 번역 함수
def translate_text(text, target_language="en"):
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

# 주어진 재료에 대해 영양 성분 정보 반환   
def get_nutrition_info(ingredient):
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

# 영양소 그래프 함수
def nutrition_graph(recipe_id):
    recipes = load_recipes()  # JSON 데이터 로드
    recipe = next((r for r in recipes if r["ID"] == recipe_id), None)

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

    # 원형 그래프 시각화 (칼로리 제외, 탄단지만 포함)
    labels = ['Protein', 'Fat', 'Carbohydrates']
    values = [total_protein, total_fat, total_carbohydrates]
    
    # 원형 그래프 시각화 (칼로리 제외, 탄단지로만 표시)
    labels = ['단백질', '지방', '탄수화물']
    values = [total_protein, total_fat, total_carbohydrates]
    
    # 그래프 그리기
    plt.figure(figsize=(4,4))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#66b3ff','#ff9999','#99ff99'])
    
    # 총 칼로리 텍스트 추가 및 텍스트 위치 설정
    total_calories_text = f"총 칼로리: {total_calories} kcal"
    plt.text(0, -1.2, total_calories_text, ha='center', va='center', fontsize=12, color='black')  # 칼로리 텍스트 아래로 이동

    plt.axis('equal')  # 원형 그래프 유지

    # 그래프를 BytesIO 객체에 저장하고 base64로 인코딩
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return graph_url