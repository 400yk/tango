from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

def encoding(url):
    return url.replace('_',' ')

def decoding(url):
    return url.replace(' ','_')

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.            
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!

    category_list = Category.objects.order_by("-likes")[:5]
    top_pages_list = Page.objects.order_by("-views")[:5]
    
    context_dict = {'categories': category_list}
    context_dict['top_pages'] =  top_pages_list

    for category in category_list:
        category.url = decoding(category.name)

    # Used shortcut here: render_to_response
    return render_to_response('rango/index.html', context_dict, context)

def about(request):
    context = RequestContext(request)
    about_message = {'self_intro': "Hi there it's fun programming in Django!"}
    return render_to_response('rango/about.html', about_message, context)

def category(request, category_name_url):
    context = RequestContext(request)
    # URL doesn't handle space well, we encode them into underscores
    category_name = encoding(category_name_url)
    context_dict = {'category_name' : category_name}

    try:
        category = Category.objects.get(name = category_name)
        pages = Page.objects.filter(category = category)

        context_dict['pages'] = pages
        context_dict['category_name_url'] = category_name_url
        context_dict['category'] = category

    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)

def add_category(request):
    context = RequestContext(request)
    
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit = True)
            return index(request)

        else:
            print form.errors

    else:
        form = CategoryForm()

    return render_to_response("rango/add_category.html", {'form': form}, context)

def add_page(request, category_name_url):
    context = RequestContext(request)
    category_name = decoding(category_name_url)

    if  request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            # This is we don't commit here since not all fields are filled automatically
            page = form.save(commit = False)

            cat = Category.objects.get(name = category_name)
            page.category = cat
            page.views = 0
            page.save() # Without the commit = True, need to manually save the page
            return category(request, category_name_url)

        else: 
            print form.errors

    else:
        form = PageForm()

    return render_to_response('rango/add_page.html', {
        'category_name_url' : category_name_url,
        'category_name' : category_name,
        'form' : form 
        }, context)

