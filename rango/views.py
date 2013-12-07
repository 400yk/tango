from django.http import HttpResponse

def index(request):
    return HttpResponse('Rango says hello world!')

def page(request):
    return HttpResponse('Range says: here is the about page.')

