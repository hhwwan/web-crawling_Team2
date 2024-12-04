import json
from django.shortcuts import render


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

    # 메시지 초기화
    error_message = None

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

    return render(
        request,
        "index.html",
        {
            "recipes": filtered_recipes,
            "query": query,
            "unique_levels": unique_levels,
            "selected_level": selected_level,
            "selected_time": selected_time,
            "error_message": error_message,
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

    return render(request, "recipe_detail.html", {"recipe": recipe})
