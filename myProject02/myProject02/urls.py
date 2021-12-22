"""myProject02 URL Configuration

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
from myapp02 import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.write_from), #처음화면 설정(전체보기)
    path('write_from/', views.write_from), #입력폼
    path('list/', views.list), #전체보기(페이징 직접설정)
    path('list2/', views.list2), #전체보기(페이징 내장객체사용)
    path('insert/', views.insert), #입력
    path('detail_id/', views.detail_id), #상세보기(폼)
    path('update_form/<int:dto_id>/', views.update_form), #수정 폼 
    path('delete/<int:dto_id>/', views.delete), #삭제하기
    path('update/', views.update), #수정
    path('comment_insert/', views.comment_insert),
]
