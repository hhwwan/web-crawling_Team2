import json

# 파일 경로 설정
input_file = "C:/Users/cest0/Downloads/practice_file_4/recipes_1501_1600.json"  # 원본 JSON 파일 경로
output_file = "C:/Users/cest0/Desktop/modified/modified_recipes.json"  # 수정된 JSON 파일 저장 경로

def process_recipes(input_path, output_path):
    # JSON 파일 로드
    with open(input_path, "r", encoding="utf-8") as file:
        recipes = json.load(file)

    modified_recipes = []
    
    for recipe in recipes:
        # 조건 확인 및 필터링
        if recipe.get("Title") == "Unknown" or not recipe.get("Ingredients") or not recipe.get("Recipe steps"):
            continue
        
        # Tools 키 제거
        recipe.pop("Tools", None)
        
        # 수정된 레시피 추가
        modified_recipes.append(recipe)
    
    # 결과를 JSON 파일로 저장
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(modified_recipes, file, ensure_ascii=False, indent=4)

# 실행
process_recipes(input_file, output_file)

print(f"Modified recipes saved to {output_file}")

