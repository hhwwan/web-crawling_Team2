import requests
import json

# Google Translate API 설정 (본인의 API 키로 교체)
GOOGLE_TRANSLATE_API_URL = "https://translation.googleapis.com/language/translate/v2"
GOOGLE_API_KEY = "AIzaSyBxPz3lopyrSdiisdbb49Bh9CoAnyiMie8"  # 여기에 본인의 API 키를 입력하세요

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

# 수량 단위 변환 함수
def convert_quantity(quantity):
    """
    수량 단위를 Edamam API에서 요구하는 형식으로 변환합니다.
    """
    conversion_dict = {
        "T": 15,   # 1 큰술 = 15ml
        "t": 5,    # 1 작은술 = 5ml
        "컵": 200, # 1 컵 = 200ml
        "종이컵": 180, # 1 종이컵 = 180ml
        "조금": 1,  # "조금"은 a little로 간주
        "스푼": 15 # 1 스푼 = 15ml
    }
    
    # 수량과 단위를 나누고 변환
    parts = quantity.split()
    if len(parts) == 2 and parts[1] in conversion_dict:
        return f"{parts[0]} {conversion_dict[parts[1]]}ml"
    elif len(parts) == 1:
        return f"{parts[0]}"
    return quantity

# Google Translate API로 재료 번역
def translate_to_english(ingredients):
    """
    Google Translate API를 사용하여 한글 텍스트를 영어로 번역합니다.
    
    매개변수:
        ingredients (dict): 한글 재료와 수량을 포함한 딕셔너리.
    
    반환값:
        dict: 번역된 영어 재료와 수량을 포함한 딕셔너리.
    """
    # 재료와 수량을 결합한 텍스트 리스트 생성
    texts_to_translate = [f"{quantity} {ingredient}" for ingredient, quantity in ingredients.items()]
    
    params = {
        'q': texts_to_translate,
        'source': 'ko',  # 한글 (한국어)
        'target': 'en',  # 영어
        'key': GOOGLE_API_KEY
    }

    try:
        response = requests.post(GOOGLE_TRANSLATE_API_URL, data=params)
        response.raise_for_status()  # 응답 상태 코드가 오류일 경우 예외 발생
        result = response.json()
        
        # 번역된 재료와 수량을 다시 딕셔너리로 저장
        translated_ingredients = {}
        for i, translation in enumerate(result['data']['translations']):
            translated_ingredients[translation['translatedText']] = texts_to_translate[i].split()[0]

        return translated_ingredients
    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {e}")
        return {}

# Edamam API로 영양 성분 데이터 가져오기
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

# 영양 성분 데이터를 한글로 변환
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
    # 한글 재료와 수량
    ingredients_kor = {
        "가지": "2개",
        "물": "3 큰술",
        "밀가루": "2 큰술",
        "간장": "2 큰술",
        "식초": "1 큰술",
        "다진 마늘": "1/2 큰술",
        "꿀": "2 큰술",
        "고추": "조금"
    }

    # 수량 단위 변환 및 영어 번역
    converted_ingredients = {ingredient: convert_quantity(quantity) for ingredient, quantity in ingredients_kor.items()}
    translated_ingredients = translate_to_english(converted_ingredients)

    # 영양 성분 데이터 가져오기
    nutrition_data = get_nutrition(translated_ingredients)

    if nutrition_data:
        # 한글로 변환한 영양 성분 데이터 출력
        translated_data = translate_nutrition(nutrition_data)
        print(json.dumps(translated_data, indent=4, ensure_ascii=False))
    else:
        print("영양 성분 데이터를 가져오지 못했습니다.")
