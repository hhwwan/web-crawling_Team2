import requests
from bs4 import BeautifulSoup
import time as t
import re
import pandas as pd

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

def extract_title_data(recipe_url):
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
        ingredients = set()  # 중복 제거를 위해 set 사용

        # 재료명과 양념 리스트 반환
        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredients.add(f"{name.get_text(strip=True)}, {quantity.get_text(strip=True)}")
        return list(ingredients)
    return []
    
def extract_tools(recipe_url):
    """레시피 페이지에서 조리도구 추출"""
    recipe_soup = fetch_recipe_html(recipe_url)
    if recipe_soup:
        tool_names = recipe_soup.select('div.ready_ingre3 ul.case1 li .ingre_list_name')
        return list({tool.get_text(strip=True) for tool in tool_names})  # 중복 제거
    return []

def extract_recipe_data(recipe_url):
    """레시피 페이지에서 조리 순서 추출"""
    recipe_soup = fetch_recipe_html(recipe_url)
    if recipe_soup:
        steps = []
        # 조리 순서와 이미지 추출
        step_divs = recipe_soup.select('div.view_step_cont.media')
        for step_div in step_divs:
            step_text = step_div.select_one('div.media-body')
            step_img = step_div.select_one('div.media-right img')
            step_data = {
                'text': step_text.get_text(strip=True) if step_text else '',
                'image_url': step_img['src'] if step_img else ''
            }
            steps.append(step_data)
        return steps
    return []

def transform_recipe_data(recipe_id, recipe_data, ingredients, tools, recipe_steps):
    """추출된 레시피 데이터를 변형 (필요한 형식으로 가공)"""
    if not recipe_data:
        return None
    return {
        'ID': recipe_id,
        'Title': recipe_data['menu_name'],
        'Serving': recipe_data['servings'],
        'Time': recipe_data['time'],
        'Level': recipe_data['difficulty'],
        'Ingredients': '/ '.join(ingredients),  # 리스트를 문자열로 변환
        'Tools': '/ '.join(tools),
        'Recipe steps': ' | '.join([step['text'] for step in recipe_steps if 'text' in step])  # 조리 단계를 문자열로 변환
    }

# def save_data_to_file(data, filename='recipes.json'):
#     """데이터를 JSON 파일에 저장"""
#     try:
#         # 파일이 이미 존재하면 데이터를 배열로 읽어오기
#         try:
#             with open(filename, 'r', encoding='utf-8') as f:
#                 existing_data = json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             existing_data = []

#         # 새로운 데이터를 기존 데이터에 추가
#         existing_data.append(data)

#         # 파일에 덮어쓰기
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(existing_data, f, ensure_ascii=False, indent=4)

#         print(f"Data successfully saved to {filename}")
#         print() # 빈 줄 추가
#     except Exception as e:
#         print(f"Failed to save data: {e}")

def load_data(recipe_id, transformed_data):
    """변형된 데이터를 로드 (예: 출력)"""
    if transformed_data:
        print(f'ID: {recipe_id}')
        print(f"Title: {transformed_data['Title']}")
        print(f"Serving: {transformed_data['Serving']}")
        print(f"Time: {transformed_data['Time']}")
        print(f"Level: {transformed_data['Level']}")
        print(f"Ingredients: {transformed_data['Ingredients']}")
        print(f"Tools: {transformed_data['Tools']}")
        print(f"Recipe steps: {transformed_data['Recipe steps']}")
        print()
    else:
        print(f"레시피 ID {recipe_id}에서 데이터를 로드할 수 없습니다.")
        
def ETL_process(page_num, df):
    """ETL 과정 실행"""
    recipe_links = extract_page_data(page_num)
    for link in recipe_links:
        recipe_url = link.get('href')  # 레시피 페이지 링크 추출
        match = re.search(r'/recipe/(\d+)', recipe_url)
        recipe_id = match.group(1) if match else 'Unknown'

        recipe_data = extract_title_data(recipe_url) # 메뉴명과, 추가정보를 추출
        ingredients = extract_ingredients(recipe_url)  # 재료와 양념을 추출
        tools = extract_tools(recipe_url)  # 조리도구 추출
        recipe_steps = extract_recipe_data(recipe_url)  # 조리 순서 추출

        transformed_data = transform_recipe_data(recipe_id, recipe_data, ingredients, tools, recipe_steps)
        load_data(recipe_id, transformed_data)
        if transformed_data:
            df = pd.concat([df, pd.DataFrame([transformed_data])], ignore_index=True)
    return df

def main():
    # 빈 데이터프레임 생성
    columns = ['ID', 'Title', 'Serving', 'Time', 'Level', 'Ingredients', 'Tools', 'Recipe steps']
    df = pd.DataFrame(columns=columns)

    # 1페이지부터 2페이지까지 크롤링
    for page_num in range(1, 2):
        df = ETL_process(page_num, df)
        t.sleep(0.2)

    # 데이터프레임 저장
    df.to_csv('recipes.csv', index=False, encoding='utf-8-sig')
    print("Data saved to recipes.csv")

if __name__ == '__main__':
    main()
