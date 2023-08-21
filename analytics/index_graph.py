from django.shortcuts import render

# Create your views here.
 

def Employee_Details(request):
    return render (request,'analytics/index_graph.html')