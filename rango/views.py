from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.            
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Used shortcut here: render_to_response
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    about_message = {'self_intro': "Hi there it's fun programming in Django!"}
    return render_to_response('rango/about.html', about_message, context)


