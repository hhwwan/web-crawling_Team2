import requests
import json

# Google Translate API 설정 (본인의 API 키로 교체)
GOOGLE_TRANSLATE_API_URL = "https://translation.googleapis.com/language/translate/v2"
GOOGLE_API_KEY = "비밀"  # 여기에 본인의 API 키를 입력하세요

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
        for i, translated_text in enumerate(result['data']['translations']):
            translated_ingredients[list(ingredients.keys())[i]] = translated_text['translatedText']
        
        # 번역된 재료와 수량을 각각 분리하여 반환
        translated_dict = {}
        for ingredient, translation in translated_ingredients.items():
            quantity, *rest = translation.split(' ', 1)  # 수량과 재료 분리
            translated_dict[rest[0]] = f"{quantity} {rest[1]}" if len(rest) > 1 else quantity
        
        return translated_dict

    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {e}")
        return {}

# 예제 입력 (한글 재료)
ingredients_json = {
    "감자": "2개",
    "스팸": "200g",
    "진간장": "4스푼",
    "설탕": "4스푼",
    "후추": "조금",
    "올리고당": "1스푼",
    "다진마늘": "1스푼",
    "물": "120ml"
}

# 한글 재료를 영어 재료로 자동 변환
translated_ingredients = translate_to_english(ingredients_json)

# 결과 출력
print("영어로 변환된 재료:", translated_ingredients)
