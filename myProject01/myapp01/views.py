from os import write
from django.http import response
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q #and, or 키워드 사용

from myapp01.models import Board, Comment
import math, os #올림
import urllib.parse
from django.http.response import HttpResponse, JsonResponse

# Create your views here.

#파일경로 설정
UPLOAD_DIR= 'c:/DjangoWorkSpace/upload/'

#write_form
def write_form(request):
    return render(request, 'board/write.html')

#insert
@csrf_exempt
def insert(request):
    #파일여부
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

    dto= Board(writer=request.POST['writer'],
                title= request.POST['title'],
                content= request.POST['content'],
                filename= fname,
                filesize= fsize
    )
    dto.save() #db에 값 추가-> myapp01_board
    return redirect("/list/")

#list
def list(request):
    #페이징
    page= request.GET.get('page','1') 
    
    #검색내용 가져오기
    word= request.GET.get('word', '')
    field= request.GET.get('field', 'title') #처음보여지는 select 값을 title로 설정
    print(word, field) #검색내용 확인(출력)

    #개수(검색결과)
    if field== 'all':
        boardCount= Board.objects.filter(Q(writer__contains=word)
                                        |Q(writer__contains=word)
                                        |Q(writer__contains=word)).count()
    elif field== 'writer':
        boardCount= Board.objects.filter(Q(writer__contains=word)).count()

    elif field== 'title':
        boardCount= Board.objects.filter(Q(title__contains=word)).count()

    elif field== 'content':
        boardCount= Board.objects.filter(Q(content__contains=word)).count()
    
    else:
        boardCount= Board.objects.all().count() #myapp01_board 전체개수(테이블)

    #페이징
    pageSize= 5 #페이지당 표시할 개수
    blockPage= 3 #페이지 블록
    currentPage= int(page)  #현재페이지
    start= (currentPage-1)* pageSize

    totPage= math.ceil(boardCount/pageSize) #전체페이지
    startPage= math.floor((currentPage-1)/blockPage)*blockPage+1 #시작페이지
    endPage= startPage+blockPage-1 #마지막페이지

    if endPage > totPage:
        endPage= totPage

    #리스트(검색결과)
    if field== 'all':
        boardList= Board.objects.filter(Q(writer__contains=word)
                                        |Q(writer__contains=word)
                                        |Q(writer__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field== 'writer':
        boardList= Board.objects.filter(Q(writer__contains=word)).order_by('-idx')[start:start+pageSize]

    elif field== 'title':
        boardList= Board.objects.filter(Q(title__contains=word)).order_by('-idx')[start:start+pageSize]

    elif field== 'content':
        boardList= Board.objects.filter(Q(content__contains=word)).order_by('-idx')[start:start+pageSize]
    
    else:
        boardList= Board.objects.all().order_by('-idx')[start:start+pageSize]

    #boardList= Board.objects.all() #myapp01_board 전체보여주기(테이블)
    #print(boardCount) #cmd에 출력하여 결과를 확인

    content= {'boardList':boardList, 'boardCount':boardCount, 'currentPage':currentPage,
            'word':word, 'blockPage':blockPage, 'startPage':startPage, 'endPage':endPage,
            'totPage':totPage, 'field':field, 'range': range(startPage, endPage+1)} #전체개수, 전체데이터 값 
    return render(request, 'board/list.html', content) 


#상세보기1
def detail_idx(request):
    id= request.GET['idx']
    dto= Board.objects.get(idx=id) #조건()
    dto.hit_up() #조회수 증가
    dto.save()
    CommentList= Comment.objects.filter(board_idx=id).order_by("-idx")

    return render(request, 'board/detail.html', {'dto': dto, 'CommentList':CommentList})

#상세보기2
def detail(request, board_idx):
    print('board_idx', board_idx)
    dto= Board.objects.get(idx=board_idx) #조건()
    dto.hit_up() #조회수 증가
    dto.save()
    CommentList= Comment.objects.filter(board_idx=board_idx).order_by("-idx")

    return render(request, 'board/detail.html', {'dto': dto, 'CommentList':CommentList})


#삭제하기
def delete(request, dto_idx):
    print(dto_idx)
    Board.objects.get(idx=dto_idx).delete()

    return redirect("/list/")


#수정 폼 이동하기
def update_form(request, dto_idx):
    dto= Board.objects.get(idx=dto_idx)

    return render(request, 'board/update.html',{'dto': dto})


#수정하기
@csrf_exempt
def update(request):
    id= request.POST['idx']

    dto= Board.objects.get(idx=id)
    fname= dto.filename
    fsize= dto.filesize

    if 'file' in request.FILES:
        file= request.FILES['file']
        fname= file.name
        fsize= file.size
        fp= open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto_update= Board(id,
                writer=request.POST['writer'],
                title= request.POST['title'],
                content= request.POST['content'],
                filename= fname,
                filesize= fsize)
    dto_update.save()

    return redirect('/list/')


#download_count
def download_count(request):
    id= request.GET['idx']
    dto= Board.objects.get(idx=id)
    dto.down_up()
    dto.save()
    count= dto.down

    return JsonResponse({'idx':id, 'count':count})


#다운로드
def download(request):
    id= request.GET['idx']
    print('id', id)

    dto= Board.objects.get(idx=id)
    path= UPLOAD_DIR+dto.filename 
    filename= urllib.parse.quote(dto.filename) #경로+파일이름을 더한 데이터를 파일이름으로 설정한다
    with open(path, 'rb') as file:
        response= HttpResponse(file.read(),
        content_type='application/octet-stream')
        response['Content-Disposition']= "attachment;filename*=UTF-8''{0}".format(filename)
        # dto.down_up() #다운로드 횟수 증가
        # dto.save()
    return response



#댓글 입력
@csrf_exempt
def comment_insert(request):
    id= request.POST['idx']
    dto= Comment(board_idx= id,
                writer= 'aa',
                content= request.POST['content'])
    dto.save()
    return redirect("/detail_idx?idx="+id) #'/detail/'+id