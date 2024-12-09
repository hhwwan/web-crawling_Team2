import json
from collections import Counter
from matplotlib import rc, font_manager
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import random
import os
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from matplotlib import font_manager
from PIL import Image
import numpy as np

def load_data_from_multiple_json(file_list, key):
    """여러 JSON 파일에서 지정된 key 데이터를 추출"""
    all_data = []
    for file_path in file_list:
        with open(file_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
            
        if key == "Ingredients":
            # Ingredients 키를 처리할 경우, 재료명(딕셔너리 키)을 모두 추출
            all_data.extend(
                [ingredient for recipe in recipes for ingredient in recipe.get(key, {}).keys()]
            )
        else:
            # 일반적인 키는 그대로 처리
            val = [recipe.get(key, "Unknown") for recipe in recipes if recipe.get(key, "Unknown") != "Unknown"]
            all_data.extend(val)
    return all_data

def count_items(items):
    """데이터의 빈도를 계산"""
    return Counter(items)

def create_gradient_palette(base_color):
    """기준 색상을 기반으로 그라데이션 색상 팔레트 생성"""
    # 기준 색상 (RGB) 설정
    base_color_rgb = [int(base_color[i:i+2], 16)/255 for i in (1, 3, 5)]
    
    # 흰색 제외, 어두운 색에서 기준 색상으로 그라데이션
    colors = [
        (0.1, 0.1, 0.5),  # 어두운 파란색
        base_color_rgb,   # 기준 색상
        (0.6, 0.8, 1.0)   # 연한 파란색
    ]
    return LinearSegmentedColormap.from_list("custom_gradient", colors)

def gradient_color(word, font_size, position, orientation, font_path, random_state):
    """그라데이션 색상 생성기"""
    color_scale = create_gradient_palette("#0d6efd")  # 기준 색상
    r, g, b = color_scale(random.random())[:3]  # 임의의 색상
    return f"rgb({int(r*255)},{int(g*255)},{int(b*255)})"



def generate_wordcloud(counter, output_path='ingredients_wordcloud.png'):
    """워드클라우드 생성 및 저장"""
    wordcloud = WordCloud(
        font_path=font_path,
        width=3000,
        height=3000,
        scale = 2,
        background_color='rgba(255, 255, 255, 0)',
        mode='RGBA',
        min_font_size=20,
        prefer_horizontal=0.5,
        relative_scaling=0.5,
        max_words=50,
        stopwords=None,
        mask=mask,
        color_func=gradient_color  # 그라데이션 색상 사용
    ).generate_from_frequencies(counter)

    # 워드클라우드 시각화
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    #plt.title("많이 사용된 재료", pad=float(23), size = 25)
    plt.show()

    # 파일로 저장
    wordcloud.to_file(output_path)
    print(f"Wordcloud saved to {output_path}")

def create_gradient_colors(base_color, n_colors):
    """기준 색상을 기반으로 색상 리스트 생성"""
    # 기준 색상 RGB로 변환
    base_color_rgb = [int(base_color[i:i+2], 16)/255 for i in (1, 3, 5)]
    
    # 색상 그라데이션 생성
    colors = [
        (0.6, 0.8, 1.0), # 연한 파란색
        base_color_rgb,   # 기준 색상
        (0.1, 0.1, 0.4)    # 진한 파란색
    ]
    cmap = LinearSegmentedColormap.from_list("custom_gradient", colors, N=n_colors)
    return [cmap(i) for i in range(cmap.N)]

def save_barplot(x, y, output_path='time_distribution_barplot.png'):
    """막대그래프 생성 및 저장"""
    # 지정된 순서로 x축 항목 정렬
    desired_order = ["5분 이내", "10분 이내", "15분 이내", "20분 이내", 
                    "30분 이내", "60분 이내", "90분 이내", "120분 이내", "2시간 이상"]
    
    # x 데이터를 Categorical로 변환하여 순서 지정
    x_ordered = pd.Categorical(x, categories=desired_order, ordered=True)
    
    # n_colors 계산 및 색상 생성
    n_colors = len(desired_order)  # x값의 개수에 따라 색상 개수를 설정
    custom_palette = create_gradient_colors("#0d6efd", n_colors)  # 그라데이션 색상 생성

    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(15, 9))
    sns.barplot(x=x_ordered, y=y, palette=custom_palette)  # 정렬된 x_ordered를 사용
    
    # x축 텍스트 스타일 설정
    plt.xticks(fontproperties=font_prop, weight='bold', fontsize=15)
    
    # y축 범위 설정
    plt.ylim([30, 25000])
    
    # x, y축 레이블 및 타이틀 설정
    plt.xlabel("조리시간", fontproperties=font_prop, fontsize=20, labelpad=15)
    plt.ylabel("레시피 수", fontproperties=font_prop, fontsize=20, labelpad=15)
    plt.title("레시피 시간 분포", fontproperties=font_prop, pad=15, size=35)
    
    # 범례 데이터 준비
    legend_labels = [f"{desired_order[i]} ({y[i]})" for i in range(len(y))]
    legend_patches = [
        plt.Line2D([0], [0], marker='o', color=custom_palette[i], markersize=10, label=legend_labels[i])
        for i in range(len(y))
    ]

    # 범례 추가 (한글 폰트 적용)
    plt.legend(
        handles=legend_patches,  
        loc='upper right', 
        fontsize=12, 
        title_fontsize=14, 
        prop=font_prop  # 한글 폰트 적용
    )
    
    # 레이아웃 조정 및 저장
    plt.tight_layout()
    plt.savefig(output_path, transparent=True, dpi = 300)  # 그래프 파일로 저장
    plt.show()
    print(f"Barplot saved to {output_path}")

if __name__ == "__main__":
    path = "../django_project/myproject/data"  # JSON 파일들이 저장된 디렉토리
    file_list = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.json')]
    
    # NanumGothic 폰트 경로 설정
    font_path = './NanumGothic.ttf'
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
    
    icon = Image.open("./pot_image.png").convert("RGBA")    # 마스크가 될 이미지 불러오기
    plt.imshow(icon)

    mask = Image.new("RGB", icon.size, (255,255,255))
    mask.paste(icon,icon)
    mask = np.array(mask)
    
    
    # 워드클라우드 그리기
    ingredients = load_data_from_multiple_json(file_list, "Ingredients")
    ingredient_counts = count_items(ingredients)
    generate_wordcloud(ingredient_counts, 'ingredients_wordcloud.png')

    # 막대그래프 그리기 (시간별)
    times = load_data_from_multiple_json(file_list, "Time")
    time_counts = count_items(times)
    times_sorted = sorted(time_counts.items(), key=lambda x: (x[0] == "Unknown", x[0]))
    x, y = zip(*times_sorted)
    
    # 막대그래프 저장
    save_barplot(x, y, 'time_distribution_barplot.png')