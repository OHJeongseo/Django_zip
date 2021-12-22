from os import popen
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from numpy import mod

# Create your models here.
class Board(models.Model): #게시판 테이블
    writer= models.ForeignKey(User, on_delete=models.CASCADE)
    title= models.CharField(null=False,max_length=200)
    content= models.TextField(null=False)
    hit= models.IntegerField(default=0)
    post_date= models.DateTimeField(default=datetime.now, blank=True)
    filename= models.CharField(null=True,blank=True,default='',max_length=500)
    filesize= models.IntegerField(default=0)
    down= models.IntegerField(default=0)

    def hit_up(self):
        self.hit+= 1

    def down_up(self):
        self.down+= 1

class Comment(models.Model): #댓글 테이블
    board= models.ForeignKey(Board, on_delete=models.CASCADE) #외래키 설정
    writer= models.ForeignKey(User, on_delete=models.CASCADE)
    content= models.TextField(null=False)
    post_date= models.DateTimeField(default=datetime.now,blank=True)

class Movie(models.Model): #영화평점데이터 테이블
    title= models.CharField(null=False,max_length=500)
    content= models.TextField(null=True)
    point= models.IntegerField(default=0)

class Forecast(models.Model): #날씨정보데이터 테이블
    city= models.CharField(null=False,max_length=100)
    tmef= models.TextField(null=True)
    wf= models.TextField(null=True)
    tmn= models.IntegerField(default=0)
    tmx= models.IntegerField(default=0)
