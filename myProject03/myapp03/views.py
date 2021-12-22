import django
from django.shortcuts import get_object_or_404, redirect, render

from myapp03 import bigdataProcess
from .forms import UserForm
from django.contrib.auth import authenticate, login #인증권한
from django.contrib.auth.decorators import login_required #
from myapp03.models import Board, Comment, Movie, Forecast #테이블 import
import math, os #올림
from django.db.models import Q #and, or 키워드(검색시) 사용
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import urllib.parse
from django.http.response import HttpResponse, JsonResponse
from django.db.models.aggregates import Avg, Count
import os, pandas as pd
import json

# Create your views here.
#입력폼
@login_required(login_url='/login/')
def write_from(request):
    return render(request, 'board/write.html')


UPLOAD_DIR= 'c:/DjangoWorkSpace/upload/'
#입력
@csrf_exempt
def insert(request):
    fname= ''
    fsize= 0
    if 'file' in request.FILES:
        file= request.FILES['file']
        fname= file.name
        fsize= file.size
        fp= open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto= Board( writer= request.user, #로그인된 유저의 id
                title= request.POST['title'],
                content= request.POST['content'],
                filename= fname,
                filesize= fsize
    )
    dto.save() #db에 값 추가-> myapp01_board
    return redirect('/list/')

#전체보기(리스트, 페이징(내장객체 활용))
def list(request):
   #페이징 초기값 설정
    page= request.GET.get('page','1') 
    
    #검색내용 가져오기
    word= request.GET.get('word', '')
    
    #개수(검색결과)
    boardCount= Board.objects.filter(Q(title__icontains=word)
                                        |Q(content__contains=word)
                                        |Q(writer__username__icontains=word)).count()

    #리스트(검색결과)
    boardList= Board.objects.filter(Q(title__icontains=word)
                                        |Q(content__contains=word)
                                        |Q(writer__username=word)).order_by('-id')

    
    #페이징처리(내장객체 사용)
    pageSize= 5
    paginator= Paginator(boardList,pageSize)
    print('paginator', paginator)
    page_obj= paginator.get_page(page)
    print('page_list', page_obj)

    #리스트에서 번호를 차례대로 출력되도록 설정한다
    rowNo= boardCount-(int(page)-1)*pageSize

    context={'page_list':page_obj, 'page': page, 'word':word, 'boardCount': boardCount, 'rowNo':rowNo}
    return render(request, 'board/list.html', context) 


## 회원가입
def signup(request):
    if request.method== "POST":
        form= UserForm(request.POST) #import
        if form.is_valid():
            print('signup POST IS')
            form.save()
            username= form.cleaned_data.get('username')
            raw_password= form.cleaned_data.get('password1')
            user= authenticate(username=username, password=raw_password) #import
            login(request, user)
            return redirect('/')
        else:
            print('signup POST un_valid')
    else:
        form= UserForm()
    
    return render(request, 'common/signup.html', {'form':form})



#다운로드 개수
def download_count(request):
    id= request.GET['id']
    dto= Board.objects.get(id=id)
    dto.down_up()
    dto.save()
    count= dto.down

    return JsonResponse({'id':id, 'count':count})


#다운로드
def download(request):
    id= request.GET['id']
    print('id', id)

    dto= Board.objects.get(id=id)
    path= UPLOAD_DIR+dto.filename 
    filename= urllib.parse.quote(dto.filename) #경로+파일이름을 더한 데이터를 파일이름으로 설정한다
    with open(path, 'rb') as file:
        response= HttpResponse(file.read(),
        content_type='application/octet-stream')
        response['Content-Disposition']= "attachment;filename*=UTF-8''{0}".format(filename)
        # dto.down_up() #다운로드 횟수 증가
        # dto.save()
    return response


#상세보기
def detail_id(request):
    id= request.GET['id']
    dto= Board.objects.get(id=id) #조건()
    dto.hit_up() #조회수 증가
    dto.save()

    return render(request, 'board/detail.html', {'dto': dto})


#댓글입력
@login_required(login_url='/login/') #로그인 권한
@csrf_exempt
def comment_insert(request):  
    board_id= request.POST['id']
    board= get_object_or_404(Board, pk=board_id)
    dto = Comment(writer= request.user,
                  content= request.POST['content'],
                  board=board)
    dto.save()
    return redirect("/detail_id?id="+board_id)  


#수정폼
def update_form(request,board_id) : 
    dto = Board.objects.get(id=board_id)
    return render(request, 'board/update.html',{'dto' : dto})   


#수정
@csrf_exempt
def update(request):
    id = request.POST['id']

    dto = Board.objects.get(id=id)
    fname = dto.filename
    fsize = dto.filesize

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size
        fp = open('%s%s' %(UPLOAD_DIR, fname),'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()  
        
    dto_update  = Board(id,
            writer=request.user,
            title=request.POST['title'],
            content=request.POST['content'],
            filename=fname,
            filesize=fsize)
    dto_update.save()

    return redirect('/list/') 

#삭제
def delete(request, board_id):
    Board.objects.get(id=board_id).delete() 
    return redirect("/list/")    



###영화평점 클로링
def movie(request):
    data= [] #데이터를 저장할 리스트를 선언
    #영화평점 크롤링 메소드를 호출하고 데이터를 저장할 리스트를 매개변수로 전달
    bigdataProcess.movie_crawling(data)

    #데이터가 없을때까지 반복하여 데이터를 미리생성한 Movie테이블에 추가하여 저장
    for r in data:
        dto= Movie(title= r[0],
                   point= r[1],
                   content= r[2])
        dto.save()
    return redirect('/')

###영화평점 차트
def movie_chart(request):
    #Movie 테이블에서 title(칼럼)에 대한 평점평균값을 가져와서 저장한다
    data= Movie.objects.values('title').annotate(point_avg= Avg('point'))[0:10] #1개의 칼럼, 평점을 가져온다
    df= pd.DataFrame(data)
    #그래프 그리기 메소드를 호출(제목,평점평균전달)
    bigdataProcess.make_chart(df.title, df.point_avg)
    # print(df)
    #그림으로 저장한 그래프와 데이터를 전달하여 결과를 출력한다
    return render(request, 'bigdata/chart.html', {"data":data, "img_data":'movie_fig.png'})

###날씨 정보
def weather(request):
    last_data= Forecast.objects.values('tmef').order_by('-tmef')[:1] #마지막 날짜에 대한 정보를 1개만 가져와서 넣는다
    print(len(last_data))
    weather= {}
    # bigdataProcess.weather_crawling(last_data, weather) #날씨정보 크롤링 메소드 호출(마지막날짜데이터, 값을 저장할 사전전달)

    #forecast 테이블에 크롤링한 날씨정보데이터 넣는다
    # for i in weather:
    #     for j in weather[i]: 
    #         dto= Forecast(city= i,
    #                       tmef= j[0],
    #                       wf= j[1],
    #                       tmn= j[2],
    #                       tmx= j[3]
    #         )
    #         dto.save()
    
    #그래프로 표시한 데이터를 설정한다
    result= Forecast.objects.filter(city='부산') 
    result1= Forecast.objects.filter(city='부산').values('wf').annotate(dcount=Count('wf')).values('dcount','wf')
    print("result1 query ", str(result1.query)) #sql문 출력

    #원하는 데이터를 2차원으로 가공하여 출력한다
    df= pd.DataFrame(result1)
    print(df)
    image_dic= bigdataProcess.weather_make_chart(result, df.wf, df.dcount) #그래프 그리기 메소드를 호출(지역,날씨정보(흐름,맑음),날씨정보갯수를 전달)
    print(image_dic)

    #return render(request, 'bigdata/chart.html', {"img_data":'weather_busan.png'})
    return render(request, 'bigdata/chart1.html', {"img_data":image_dic}) #그래프로 그린 사전데이터를 전달하여 그래프를 출력한다



#지도
def map(request): 
    bigdataProcess.map()
    return render(request, 'bigdata/map.html')



#워드클라우드
def wordcloud(request):
    a_path= "C:/DjangoWorkSpace/myProject03/data/"
    data= json.loads(open(a_path+'4차 산업혁명.json', 'r', encoding='utf-8').read())
    bigdataProcess.make_wordCloud(data)
    return render(request, 'bigdata/chart.html', {"img_data":'k_wordCloud.png'})


#영화예매차트
def movieTickting(request):
    data= [] 
    bigdataProcess.movie_Tickting(data)
    movies= []
    for m in data[:5]:
        movies.append([m[0],m[2]])
    #print(movies)
    df= pd.DataFrame(movies, columns=['moviename','movieReser'])
    print(df)

    image_dic= bigdataProcess.make_movie_Ticking(df.moviename, df.movieReser)
    print(image_dic)
    return render(request, 'bigdata/chart2.html', {"img_data": image_dic})