import requests
import json

# Edamam API 자격 증명 (본인의 자격 증명으로 교체하세요)
APP_ID = "954ff38e"
APP_KEY = "e312c2dcb2afea6b51850378ba8d1f8d"
API_URL = "https://api.edamam.com/api/nutrition-details"

# 영양 성분 항목의 영어 라벨과 한글 라벨을 매핑한 딕셔너리
NUTRITION_LABELS = {
    "ENERC_KCAL": "칼로리 (kcal)",
    "FAT": "총 지방 (g)",
    "FASAT": "포화 지방 (g)",
    "FATRN": "트랜스 지방 (g)",
    "FAMS": "단일 불포화 지방 (g)",
    "FAPU": "다불포화 지방 (g)",
    "CHOCDF": "탄수화물 (g)",
    "CHOCDF.net": "순 탄수화물 (g)",
    "FIBTG": "식이 섬유 (g)",
    "SUGAR": "당류 (g)",
    "SUGAR.added": "추가된 당류 (g)",
    "PROCNT": "단백질 (g)",
    "CHOLE": "콜레스테롤 (mg)",
    "NA": "나트륨 (mg)",
    "CA": "칼슘 (mg)",
    "MG": "마그네슘 (mg)",
    "K": "칼륨 (mg)",
    "FE": "철분 (mg)",
    "ZN": "아연 (mg)",
    "P": "인 (mg)",
    "VITA_RAE": "비타민 A (µg)",
    "VITC": "비타민 C (mg)",
    "THIA": "티아민 (B1) (mg)",
    "RIBF": "리보플라빈 (B2) (mg)",
    "NIA": "나이아신 (B3) (mg)",
    "VITB6A": "비타민 B6 (mg)",
    "FOLDFE": "엽산 (µg)",
    "VITB12": "비타민 B12 (µg)",
    "VITD": "비타민 D (µg)",
    "TOCPHA": "비타민 E (mg)",
    "VITK1": "비타민 K (µg)",
    "WATER": "물 (g)"
}

def get_nutrition(ingredients):
    """
    주어진 재료를 기반으로 Edamam API를 이용해 영양 성분 데이터를 가져옵니다.
    
    매개변수:
        ingredients (dict): 재료와 수량을 포함한 딕셔너리.

    반환값:
        dict: 영양 성분 정보.
    """
    headers = {"Content-Type": "application/json"}

    # API 요청에 사용할 데이터 준비
    payload = {
        "title": "Recipe Nutrition Analysis",
        "ingr": []
    }
    
    # 재료를 API에서 요구하는 형식으로 변환
    for ingredient, quantity in ingredients.items():
        payload["ingr"].append(f"{quantity} {ingredient}")

    try:
        response = requests.post(
            f"{API_URL}?app_id={APP_ID}&app_key={APP_KEY}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # 응답 상태 코드가 오류일 경우 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {e}")
        return None

def translate_nutrition(nutrition_data):
    """
    영양 성분 데이터를 한글로 변환하여 반환합니다.
    
    매개변수:
        nutrition_data (dict): Edamam API에서 받은 영양 성분 데이터.
    
    반환값:
        dict: 영양 성분 데이터의 한글 변환본.
    """
    translated_data = {}

    # 각 영양 성분 항목을 한글로 변환
    for key, value in nutrition_data.get('totalNutrients', {}).items():
        if key in NUTRITION_LABELS:
            translated_data[NUTRITION_LABELS[key]] = {
                "quantity": value.get("quantity"),
                "unit": value.get("unit")
            }

    return translated_data

if __name__ == "__main__":
    # 예제 입력 JSON (영어로 바꾼 재료 부분)
    ingredients_json = {
        "eggplant": "2",
        "water": "3 tbsp",
        "flour": "2 tbsp",
        "soy sauce": "2 tbsp",
        "vinegar": "1 tbsp",
        "minced garlic": "1/2 tbsp",
        "honey": "2 tbsp",
        "chili pepper": "a little"
    }

    # 영양 성분 데이터 가져오기
    nutrition_data = get_nutrition(ingredients_json)

    if nutrition_data:
        # 한글로 변환한 영양 성분 데이터 출력
        translated_data = translate_nutrition(nutrition_data)
        print(json.dumps(translated_data, indent=4, ensure_ascii=False))
    else:
        print("영양 성분 데이터를 가져오지 못했습니다.")
