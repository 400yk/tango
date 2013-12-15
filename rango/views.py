from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required

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


def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # We hash the password with set_password method.
            # After hashing we can update the user object
            user.set_password(user.password)
        
            user.save()
            
            # This is where we populate profile_form with user_form info
            profile = profile_form.save(commit = False)
            profile.user = user

            # If user provided a picture, we need to get it from the input and
            # put it in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response('rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
        }, context)

def user_login(request):
    context = RequestContext(request)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # User django's machinary to see if the username and password match record, 
        # if so it will return a User object
        user = authenticate(username = username, password = password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your Rango account is disabled.')

        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
    return HttpResponse("Since you are logged in, you can see this response.")

@login_required
def user_logout(request):
    logout(request)
    # no need to fetch the request since we don't need it
    return HttpResponseRedirect('/rango/')

