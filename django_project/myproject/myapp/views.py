import json
from django.shortcuts import render


# JSON 파일 로드 함수
def load_recipes():
    with open("data/recipes.json", "r", encoding="utf-8") as file:
        recipes = json.load(file)
    return recipes


def index(request):
    recipes = load_recipes()  # JSON 데이터 로드
    query = request.GET.get("ingredient", "")  # URL에서 'ingredient' 파라미터 가져오기
    filtered_recipes = []

    if query:
        # 입력받은 재료가 포함된 레시피 필터링
        for recipe in recipes:
            ingredients = recipe.get("Ingredients", {})
            if query in ingredients:
                filtered_recipes.append(recipe)

    return render(request, "index.html", {"recipes": filtered_recipes, "query": query})


# 상세 정보 뷰 함수
def recipe_detail(request, recipe_id):
    recipes = load_recipes()  # JSON 데이터 로드
    recipe = next((r for r in recipes if r["ID"] == recipe_id), None)

    if recipe is None:
        return render(request, "404.html", {"message": "Recipe not found"})  # 404 처리

    # "Recipe steps"를 "recipe_steps"로 변경
    recipe["recipe_steps"] = recipe.pop("Recipe steps")

    return render(request, "recipe_detail.html", {"recipe": recipe})
