from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # 메인 페이지 URL
    path(
        "recipe/<str:recipe_id>/", views.recipe_detail, name="recipe_detail"
    ),  # 상세 정보 페이지
]
