from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
# Create your views here.

class CheckoutView(generic.View):
    def get(self, request):
        return HttpResponse('checkout')
