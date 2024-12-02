import requests
from bs4 import BeautifulSoup
import time as t
import re
import json

base_url = 'https://www.10000recipe.com/recipe/list.html?order=reco&page='
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}

def fetch_recipe_html(recipe_url):
    """레시피 페이지에서 HTML을 가져오는 공통 함수"""
    final_url = f'https://www.10000recipe.com{recipe_url}'
    try:
        recipe_response = requests.get(final_url, headers=headers)
        recipe_response.raise_for_status()  # HTTP 상태코드가 400번대나 500번대면 예외발생
        return BeautifulSoup(recipe_response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch recipe page: {e}")
        return None
    
def extract_page_data(page_num):
    """페이지에서 레시피 링크를 추출"""
    page_url = f'{base_url}{page_num}'
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()  # HTTP 상태코드가 400번대나 500번대면 예외발생
        soup = BeautifulSoup(response.text, 'html.parser')

        # 레시피 링크들 가져오기 (이미지가 포함된 링크들)
        recipe_links = soup.select('div.common_sp_thumb a')
        return recipe_links
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch page {page_num}. Error: {e}")
        return []

def extract_recipe_data(recipe_url):
    """레시피 페이지에서 상세 정보를 추출"""
    recipe_soup = fetch_recipe_html(recipe_url)
    if recipe_soup:
        # 메뉴 이름 가져오기
        menu_name = recipe_soup.select_one('div.view2_summary.st3 h3')

        # 추가 정보 가져오기
        servings = recipe_soup.select_one('span.view2_summary_info1')  # 인분
        time = recipe_soup.select_one('span.view2_summary_info2')      # 시간
        difficulty = recipe_soup.select_one('span.view2_summary_info3')  # 난이도

        # 레시피 정보 반환
        return {
            'menu_name': menu_name.get_text(strip=True) if menu_name else 'Unknown',
            'servings': servings.get_text(strip=True) if servings else 'Unknown',
            'time': time.get_text(strip=True) if time else 'Unknown',
            'difficulty': difficulty.get_text(strip=True) if difficulty else 'Unknown',
        }
    return None

def extract_ingredients(recipe_url):
    """레시피 페이지에서 재료명과 양념을 추출"""
    recipe_soup = fetch_recipe_html(recipe_url)
    if recipe_soup:
        # 재료명, 양념 가져오기
        ingredient_names = recipe_soup.select('div.ingre_list_name a')
        ingredient_quantities = recipe_soup.select('span.ingre_list_ea')

        # 재료명과 양념 리스트 반환
        return [(name.get_text(strip=True), quantitie.get_text(strip=True)) for name, quantitie in zip(ingredient_names, ingredient_quantities)]
    return []
    
def extract_tools(recipe_url):
    """레시피 페이지에서 조리도구 추출"""
    recipe_soup = fetch_recipe_html(recipe_url)
    if recipe_soup:
        # 조리도구명 가져오기
        tool_names = recipe_soup.select('div.ready_ingre3 ul.case1 li .ingre_list_name')

        # 조리도구 리스트 반환
        return [tool.get_text(strip=True) for tool in tool_names]
    return []

def transform_recipe_data(recipe_id, recipe_data, ingredients, tools):
    """추출된 레시피 데이터를 변형 (필요한 형식으로 가공)"""
    if not recipe_data:
        return None
    transformed_data = {
        'ID': recipe_id,
        '메뉴명': recipe_data['menu_name'],
        '양': recipe_data['servings'],
        '시간': recipe_data['time'],
        '난이도': recipe_data['difficulty'],
        '재료 및 양념': [],
        '조리도구': tools
    }
    for ingredient_name, ingredient_quantity in ingredients:
        transformed_data['재료 및 양념'].append(f'{ingredient_name}, {ingredient_quantity}')
    
    return transformed_data

def save_data_to_file(data, filename='recipes.json'):
    """데이터를 JSON 파일에 저장"""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write('\n')  # 각 레시피 사이에 줄바꿈을 추가하여 가독성 향상
        print(f"Data successfully saved to {filename}")
        print()  # 각 레시피 끝에 빈 줄 추가
    except Exception as e:
        print(f"Failed to save data: {e}")

def load_data(recipe_id, transformed_data):
    """변형된 데이터를 로드 (예: 출력)"""
    if transformed_data:
        print(f'ID: {recipe_id}')
        print(f"메뉴명: {transformed_data['메뉴명']}")
        print(f"양: {transformed_data['양']}")
        print(f"시간: {transformed_data['시간']}")
        print(f"난이도: {transformed_data['난이도']}")
        print("재료 및 양념:")
        for ingredient in transformed_data['재료 및 양념']:
            print(f"  - {ingredient}")
        print(f"조리도구: {transformed_data['조리도구']}")
    else:
        print(f"레시피 ID {recipe_id}에서 데이터를 로드할 수 없습니다.")
        
def ETL_process(page_num):
    """ETL 과정 실행"""
    recipe_links = extract_page_data(page_num)
    for link in recipe_links:
        recipe_url = link.get('href')  # 레시피 페이지 링크 추출
        match = re.search(r'/recipe/(\d+)', recipe_url)
        recipe_id = match.group(1) if match else 'Unknown'

        recipe_data = extract_recipe_data(recipe_url) # 메뉴명과, 추가정보를 추출
        ingredients = extract_ingredients(recipe_url)  # 재료와 양념을 추출
        tools = extract_tools(recipe_url)  # 조리도구 추출
        transformed_data = transform_recipe_data(recipe_id, recipe_data, ingredients, tools)
        load_data(recipe_id, transformed_data)

        if transformed_data:
            save_data_to_file(transformed_data)

def main():
    # 1페이지부터 2페이지까지 크롤링
    for page_num in range(1, 2):  # 페이지 번호 1~2
        ETL_process(page_num)
        t.sleep(0.2)  # 요청 간 0.2초 지연

if __name__ == '__main__':
    main()
