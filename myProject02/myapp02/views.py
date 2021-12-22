from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from myapp02.models import Board, Comment
import math, os #올림
from django.db.models import Q #and, or 키워드 사용
from django.core.paginator import Paginator

#파일경로 설정
UPLOAD_DIR= 'c:/DjangoWorkSpace/upload/'

# Create your views here.

#입력폼
def write_from(request):
    return render(request, 'board/write.html')

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

    dto= Board(writer=request.POST['writer'],
                title= request.POST['title'],
                content= request.POST['content'],
                filename= fname,
                filesize= fsize
    )
    dto.save() #db에 값 추가-> myapp01_board
    return redirect('/list/')


#전체보기
def list2(request):
   #페이징 초기값 설정
    page= request.GET.get('page','1') 
    
    #검색내용 가져오기
    word= request.GET.get('word', '')
    
    #개수(검색결과)
    boardCount= Board.objects.filter(Q(writer__contains=word)
                                        |Q(writer__contains=word)
                                        |Q(writer__contains=word)).count()

    #리스트(검색결과)
    boardList= Board.objects.filter(Q(writer__contains=word)
                                        |Q(writer__contains=word)
                                        |Q(writer__contains=word)).order_by('-id')

    
    #페이징처리(내장객체 사용)
    pageSize= 5
    paginator= Paginator(boardList,pageSize)
    print('paginator', paginator)
    page_obj= paginator.get_page(page)
    print('page_list', page_obj)

    #리스트에서 번호를 차례대로 출력되도록 설정한다
    rowNo= boardCount-(int(page)-1)*pageSize

    context={'page_list':page_obj, 'page': page, 'word':word, 'boardCount': boardCount, 'rowNo':rowNo}
    return render(request, 'board/list2.html', context) 

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

    #페이징(직접설정)
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
                                        |Q(writer__contains=word)).order_by('-id')[start:start+pageSize]
    elif field== 'writer':
        boardList= Board.objects.filter(Q(writer__contains=word)).order_by('-id')[start:start+pageSize]

    elif field== 'title':
        boardList= Board.objects.filter(Q(title__contains=word)).order_by('-id')[start:start+pageSize]

    elif field== 'content':
        boardList= Board.objects.filter(Q(content__contains=word)).order_by('-id')[start:start+pageSize]
    
    else:
        boardList= Board.objects.all().order_by('-id')[start:start+pageSize]

    #boardList= Board.objects.all() #myapp01_board 전체보여주기(테이블)
    #print(boardCount) #cmd에 출력하여 결과를 확인

    content= {'boardList':boardList, 'boardCount':boardCount, 'currentPage':currentPage,
            'word':word, 'blockPage':blockPage, 'startPage':startPage, 'endPage':endPage,
            'totPage':totPage, 'field':field, 'range': range(startPage, endPage+1)} #전체개수, 전체데이터 값 
    return render(request, 'board/list.html', content) 


#상세보기
def detail_id(request):
    id= request.GET['id']
    dto= Board.objects.get(id=id)
    dto.hit_up() #조회수 증가
    dto.save()

    #댓글 리스트
    #  CommentList= Comment.objects.filter(board_id=id).order_by("-id")#정렬(내림차순)

    return render(request, 'board/detail.html', {'dto': dto}) 


#수정 폼 이동
def update_form(request, dto_id):
    dto= Board.objects.get(id=dto_id)
    return render(request, 'board/update.html',{'dto': dto})


#삭제 
def delete(request, dto_id):
    Board.objects.get(id=dto_id).delete()
    return redirect("/list/")


#수정하기
@csrf_exempt
def update(request):
    id= request.POST['id']

    dto= Board.objects.get(id=id) #id에 맞는 데이터를 가져와서
    print(id)
    fname= dto.filename #파일이름
    fsize= dto.filesize #파일크기를 가져온다

    #파일여부확인
    if 'file' in request.FILES:
        file= request.FILES['file']
        fname= file.name
        fsize= file.size
        fp= open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    #파일 수정(다시입력)
    dto_update= Board(id,
                writer=request.POST['writer'],
                title= request.POST['title'],
                content= request.POST['content'],
                filename= fname,
                filesize= fsize)
    dto_update.save() #저장

    return redirect('/list/')

# 댓글쓰기
@csrf_exempt
def comment_insert(request):
    id= request.POST['id']

    #댓글테이블에 데이터 입력
    dto= Comment(board_id= id,
                writer= 'writer'+id,
                content= request.POST['content'])
    dto.save()
    return redirect("/detail_id?id="+id) #댓글이 입력된 데이터의 상세보기로 이동    
