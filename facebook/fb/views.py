from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .models import stud

# Create your views here.

def hi(re):
    return HttpResponse('hello everyone')
