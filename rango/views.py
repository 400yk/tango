from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from rango.models import Category, Page

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.            
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!

    category_list = Category.objects.order_by("-likes")[:5]
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = category.name.replace(' ', '_')

    # Used shortcut here: render_to_response
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    about_message = {'self_intro': "Hi there it's fun programming in Django!"}
    return render_to_response('rango/about.html', about_message, context)

def category(request, category_name_url):
    context = RequestContext(request)
    # URL doesn't handle space well, we encode them into underscores
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'category_name' : category_name}

    try:
        category = Category.objects.get(name = category_name)
        pages = Page.objects.filter(category = category)

        context_dict['pages'] = pages

        context_dict['category'] = category

    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)



