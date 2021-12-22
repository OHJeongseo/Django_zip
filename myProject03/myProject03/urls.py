"""myProject03 URL Configuration

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
from myapp03 import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # crud
    path('', views.write_from), #입력폼
    path('list/', views.list), #전체
    path('insert/', views.insert), #입력
    path('download_count/', views.download_count), #다운로드(파일)개수
    path('download/', views.download), #다운로드 처리
    path('detail_id/', views.detail_id), #상세
    path('comment_insert/', views.comment_insert), #댓글입력
    path('write_form/', views.write_from), #입력폼
    path('delete/<int:board_id>/', views.delete), #삭제 
    path('update_form/<int:board_id>/', views.update_form), #수정폼
    path('update/', views.update), #수정

    ###
    path('movie/', views.movie),  #영화평점댓글 크롤링
    path('movie_chart/', views.movie_chart), #Movie테이블의 데이터를 가져와서 그래프로 출력
    path('weather/', views.weather), #날씨정보 크롤링하고 그래프로 출력
    path('map/', views.map), #지도 출력
    path('wordcloud/', views.wordcloud),
    path('movieTickting/', views.movieTickting),

    ## auth_user 
    path('signup/', views.signup), #회원가입
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'),name='login'), #로그인
    path('logout/', auth_views.LogoutView.as_view(),name='logout'), #로그아웃
]
