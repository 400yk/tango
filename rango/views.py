from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hello world! <a href='/rango/about/'>About</a>")

def about(request):
    return HttpResponse("Range says: here is the about page. <a href='/rango/'>Main page</a>")

