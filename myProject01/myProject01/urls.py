"""myProject01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp01 import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('',views.list), #전체보기
    path('write_form', views.write_form), #db에 값 추가하는 폼
    path('insert/', views.insert), #db에 값 추가
    path('list/', views.list), #전체보기
    path('detail_idx/', views.detail_idx), #상세보기
    path('detail/<int:board_idx>/', views.detail), #상세보기
    path('delete/<int:dto_idx>/', views.delete), #삭제하기
    path('update_form/<int:dto_idx>/', views.update_form), #수정 폼 이동하기
    path('update/', views.update), #수정하기
    path('download/', views.download), #이미지 다운로드하기
    path('download_count', views.download_count), #다운로드 개수 추가(jquery)와 다운로드 
    path('comment_insert/', views.comment_insert), #댓글 입력
]
