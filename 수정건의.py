from bs4 import BeautifulSoup

recipe_steps = {}
step = 1

while True:
    try:
        # 각 단계의 요소를 ID로 검색
        step_element = soup.find(id=f"stepdescr{step}")
        if not step_element:
            break  # 요소가 없으면 반복 종료

        # 첫 번째 줄 텍스트 추출
        main_text = step_element.get_text(separator="\n").split("\n")[0].strip()

        # 추가 정보 추출 (괄호에 포함)
        additional_info = []
        p_elements = step_element.find_all("p")
        for p in p_elements:
            if not p.find("a"):  # <a> 태그가 없는 경우만 추가
                additional_info.append(f"({p.get_text(strip=True)})")

        # 최종 조리 순서 텍스트
        full_text = f"{main_text} {' '.join(additional_info)}"
        recipe_steps[step] = full_text

        step += 1
    except Exception as e:
        print(f"Error processing step {step}: {e}")
        break

# 결과 출력
for step, text in recipe_steps.items():
    print(f"Step {step}: {text}")
