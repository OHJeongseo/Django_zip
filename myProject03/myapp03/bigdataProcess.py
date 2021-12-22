import os
from typing import Counter
from numpy import double #경로설정
import requests #url 가공
from bs4 import BeautifulSoup #html 파싱 
import matplotlib.pyplot as plt #그래프
from matplotlib import font_manager, rc
import pandas as pd #
import folium #지도
from myProject03.settings import STATIC_DIR, TEMPALATE_DIR #settings의 설정한static, tempalate 파일 경로를 사용
from konlpy.tag import Okt
import re
from wordcloud import WordCloud

def movie_crawling(data): #네이버 영화평점 댓글 크롤링
     for i in range(10):
        base_url= "https://movie.naver.com/movie/point/af/list.nhn?&page="
        url= base_url+str(i+1)
        req= requests.get(url)
       

        if req.ok:
            html= req.text
            print('html: ', html)
            soup= BeautifulSoup(html, 'html.parser') 
            titles= soup.select('td.title > a.movie.color_b')
            #print(titles)
            points= soup.select('td.title > div > em')
            #print(points)
            #old_content > table > tbody > tr:nth-child(1) > td.title > br
            contents= soup.select('td.title')
            #print(contents)

            for i in range(len(titles)):
                title= titles[i].get_text()
                point= points[i].get_text()
                content_arr= contents[i].get_text().replace('신고','').split("\n\n")
                content= content_arr[2].replace("\t",'').replace("\n",'')
                data.append([title,point, content])
            #print(data)


def make_chart(titles, points): #영화 평점 그래프 그리기
    #그래프 한글처리
    font_location= "c:/Windows/fonts/malgun.ttf"
    font_name= font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)

    plt.cla() #누적되지않도록 설정
    plt.ylabel('영화평점평균')
    plt.xlabel('영화제목')
    plt.bar(range(len(titles)),points, align='center')
    plt.xticks(range(len(titles)),list(titles),rotation=70)
    plt.savefig(os.path.join(STATIC_DIR,'images\\movie_fig.png')) #static파일의 images에 설정한이름으로 파일을 저장



def weather_crawling(last_data, weather): #날씨 정보 크롤링
    req= requests.get('https://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108')
    html= req.text
    soup= BeautifulSoup(html,'lxml')

    for i in soup.find_all('location'):
        weather[i.find('city').text]=[] 
        for j in i.find_all('data'):
            temp= []
            if(len(last_data)==0) or (j.find('tmef').text > last_data[0]['tmef']):
                temp.append(j.find('tmef').text) #날짜
                temp.append(j.find('wf').text) #날씨
                temp.append(j.find('tmn').text) #최소기온
                temp.append(j.find('tmx').text) #최고기온
                #print(temp)
                weather[i.find('city').string].append(temp) 
    #print(weather)


def weather_make_chart(result, wfs, dcounts): #날씨(최저, 최고)기온 그래프 그리기
    font_location= "c:/Windows/fonts/malgun.ttf"
    font_name= font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)

    high= []
    low= []
    xdata= []

    for row in result.values_list():
        high.append(row[5])
        low.append(row[4])
        xdata.append(row[2].split('-')[2])
    print(xdata)
    plt.cla() #누적되지않도록 설정
    plt.figure(figsize=(10,6))
    plt.plot(xdata,low, label='최저기온')
    plt.plot(xdata,high, label='최고기온')
    plt.legend()
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_busan.png'),dpi=300) #static의 images에 파일저장

    plt.cla()
    plt.bar(wfs, dcounts)
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_bar.png'),dpi=300)

    plt.cla()
    plt.pie(dcounts,labels=wfs,autopct='%.1f%%')
    plt.savefig(os.path.join(STATIC_DIR, 'images\\weather_pie.png'),dpi=300)
    image_dic= {'plot': 'weather_busan.png', 'bar': 'weather_bar.png', 'pie':'weather_pie.png'}
    #print("image_dic :", image_dic)
    return image_dic



def map(): #지도 사용 
    #맵에서 사용할 경도,위도,구분 설정
    ex = {'경도' : [127.061026,127.047883,127.899220,128.980455,127.104071,127.102490,127.088387,126.809957,127.010861,126.836078
                ,127.014217,126.886859,127.031702,126.880898,127.028726,126.897710,126.910288,127.043189,127.071184,127.076812
                ,127.045022,126.982419,126.840285,127.115873,126.885320,127.078464,127.057100,127.020945,129.068324,129.059574
                ,126.927655,127.034302,129.106330,126.980242,126.945099,129.034599,127.054649,127.019556,127.053198,127.031005
                ,127.058560,127.078519,127.056141,129.034605,126.888485,129.070117,127.057746,126.929288,127.054163,129.060972],
        '위도' : [37.493922,37.505675,37.471711,35.159774,37.500249,37.515149,37.549245,37.562013,37.552153,37.538927,37.492388
                ,37.480390,37.588485,37.504067,37.608392,37.503693,37.579029,37.580073,37.552103,37.545461,37.580196,37.562274
                ,37.535419,37.527477,37.526139,37.648247,37.512939,37.517574,35.202902,35.144776,37.499229,35.150069,35.141176
                ,37.479403,37.512569,35.123196,37.546718,37.553668,37.488742,37.493653,37.498462,37.556602,37.544180,35.111532
                ,37.508058,35.085777,37.546103,37.483899,37.489299,35.143421],
        '구분' : ['음식','음식','음식','음식','생활서비스','음식','음식','음식','음식','음식','음식','음식','음식','음식','음식'
                ,'음식','음식','소매','음식','음식','음식','음식','소매','음식','소매','음식','음식','음식','음식','음식','음식'
                ,'음식','음식','음식','음식','소매','음식','음식','의료','음식','음식','음식','소매','음식','음식','음식','음식'
                ,'음식','음식','음식']}

    #2차원
    ex= pd.DataFrame(ex)
    print(ex)    

    #평균(위도,경도)
    lat= ex['위도'].mean()
    long= ex['경도'].mean()

    #지도 띄우기
    m= folium.Map([lat,long],zoom_start=9)

    #위의 경도,위도에 구분데이터를 마킹하고 tempalate파일에 maptest.html를 생성(자동)
    for i in ex.index:
        sub_lat= ex.loc[i, '위도']
        sub_long= ex.loc[i, '경도']

        tltle= ex.loc[i, '구분']

        folium.Marker([sub_lat,sub_long], tooltip=tltle).add_to(m)
        m.save(os.path.join(TEMPALATE_DIR,'bigdata/maptest.html'))


def make_wordCloud(data):
    message= ''
    for item in data:   
        if 'message' in item.keys():
            message= message+ re.sub(r'[^\w]',' ', item['message'])
        
    nlp= Okt()
    message_N= nlp.nouns(message) #명사 가져오기
    count= Counter(message_N)
    #print(count)

    word_count= dict()
    for tag, counts in count.most_common(80): #상위 80개만 사용
        if(len(str(tag))>1):
            word_count[tag]= counts
            #print("%s: %d" %(tag,counts))
    
    #한글처리
    font_path= "c:/Windows/Fonts/malgun.ttf"
    #font_name= font_manager.FontProperties(fname=font_path).get_name()

    #워드클라우드(그림시각화) 사용하여 이미지로 저장
    wc= WordCloud(font_path ,background_color='ivory', width=800, height=600)
    cloud= wc.generate_from_frequencies(word_count)
    plt.cla()
    plt.figure(figsize=(10,8))
    plt.imshow(cloud)
    plt.axis('off')
    #plt.show()
    plt.savefig(os.path.join(STATIC_DIR, 'images\\k_wordCloud.png'),dpi=300)
    #cloud.to_file('./static/images/k_wordCloud.png')


#영화예매율 크롤링
def movie_Tickting(data):
    req= requests.get("https://movie.daum.net/ranking/reservation") 
    html= req.text
    soup= BeautifulSoup(html, 'html.parser') 

    #원하는 데이터(영화 이름, 평점, 예약률) 추출하여 결과를 출력
    ols= soup.find('ol', 'list_movieranking')
    rankcont= ols.find_all('div', 'thumb_cont')
    
    for i in rankcont:
        moviename= i.find('a','link_txt').get_text() #제목
        moviegrade= i.find('span','txt_grade').get_text() #평점
        movieReser= i.find('span', 'txt_num').get_text() #예매률
        movieResers= re.sub('%', '', movieReser) #예매률 % 지우기
        #개봉일 데이터추출(문자+숫자)
        movieopendate= i.find('span', 'txt_info').get_text() 
        #가져온 데이터에서 숫자만 추출
        moviedate= movieopendate.split('개봉')[1].strip() 
        data.append([moviename,moviegrade,movieResers,moviedate])
    #print(data)
    #print(rankcont)


#영화예매 파이그래프
def make_movie_Ticking(moviename, movieReser): 

    font_location= "c:/Windows/fonts/malgun.ttf"
    font_name= font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)
    explode = [0.1, 0.1, 0.1, 0.1, 0.1] #파이그래프 공간 설정
    plt.cla()
    
    Total= str(round(sum(double(movieReser)),1)) #Top5의 예매율(합계 소수점1자리까지만 사용)
    print(Total)

    plt.title("영화예매율 Top5 [전체:"+Total+"% 의]")
    plt.pie(double(movieReser),labels=moviename,autopct='%1.1f%%',explode=explode)
    plt.savefig(os.path.join(STATIC_DIR, 'images\\movieTicking_pie.png'),dpi=300)
    #print(data)

    plt.cla() #누적되지않도록 설정
    plt.figure(figsize=(10,8))
    plt.ylabel('영화예매율')
    plt.xlabel('영화제목')
    plt.bar(range(len(moviename)),double(movieReser),align='center')
    plt.xticks(range(len(moviename)),list(moviename),rotation=70)
    plt.savefig(os.path.join(STATIC_DIR,'images\\movieTicking_bar.png')) #static파일의 images에 설정한이름으로 파일을 저장

    image_dic= {'bar': 'movieTicking_pie.png', 'pie':'movieTicking_bar.png'}
    return image_dic



