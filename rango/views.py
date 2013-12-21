from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.bing_search import run_query
from django.contrib.auth.decorators import login_required

def encoding(url):
    return url.replace('_',' ')

def decoding(url):
    return url.replace(' ','_')

def get_categories():
    category_list = Category.objects.all()
    for category in category_list:
        category.url = decoding(category.name)

    return category_list

def index(request):
    # Run a test for the cookie as follows:
    # request.session.set_test_cookie()

    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.            
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    top_pages_list = Page.objects.order_by("-views")[:5]
    context_dict = {}
    context_dict['top_pages'] = top_pages_list
    context_dict['categories'] = get_categories()

    # Used shortcut here: render_to_response
    response = render_to_response('rango/index.html', context_dict, context)

    ''' Add cookie to the client's side
    # Track the number of visits, default is 0
    visits = int(request.COOKIES.get('visits', 0))

    # Check if last_visit exists in the cookie
    if request.COOKIES.has_key('last_visit'):
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # if it's been more than a day since last visit
        if (datetime.now() - last_visit_time).days > 0:
            response.set_cookie('visits', visits + 1)
            response.set_cookit('last_visit', datetime.now())

    else:
        # Cookie doesn't exist, create one
        response.set_cookie('last_visit', datetime.now())
    '''

    # Add cookie to the server's side
    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())

    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    # A nice extra advantage to storing session data server-side 
    # is that you do not need to always cast data from strings to 
    # the desired type. Be careful though, this only seems to hold 
    # for simple data types such as strings, integers, floats and booleans.        

    return response

def about(request):
    context = RequestContext(request)

    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render_to_response('rango/about.html', {'visits': count, 'categories': get_categories()}, context)

def category(request, category_name_url):
    context = RequestContext(request)
    # URL doesn't handle space well, we encode them into underscores
    category_name = encoding(category_name_url)
    context_dict = {'category_name' : category_name}

    try:
        category = Category.objects.get(name = category_name)
        pages = Page.objects.filter(category = category).order_by('-views')

        context_dict['pages'] = pages
        context_dict['category_name_url'] = category_name_url
        context_dict['category'] = category
        context_dict['categories'] = get_categories()

    except Category.DoesNotExist:
        pass

    result_list = []

    if request.method == "POST":
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['result_list'] = result_list

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

    return render_to_response("rango/add_category.html", {'form': form, 'categories': get_categories()}, context)

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
        'form' : form,
        'categories': get_categories()
        }, context)


def register(request):
    if request.session.test_cookie_worked():
        print ">>> Test cookie worked"
        request.session.delete_test_cookie()

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
        'registered': registered,
        'categories': get_categories()
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
        return render_to_response('rango/login.html', {'categories': get_categories()}, context)

@login_required
def restricted(request):
    return HttpResponse("Since you are logged in, you can see this response.")

@login_required
def user_logout(request):
    logout(request)
    # no need to fetch the request since we don't need it
    return HttpResponseRedirect('/rango/')

def search(request):
    context = RequestContext(request)
    result_list = []

    if request.method == "POST":
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list, 'categories': get_categories()}, context)

@login_required
def profile(request):
    context = RequestContext(request)
    user = request.user
    profile = UserProfile.objects.get(user = user)
    
    return render_to_response('rango/profile.html', {'profile': profile}, context)
    
def track_url(request):
    context = RequestContext(request)

    if request.method == "GET":
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            page = Page.objects.get(pk = page_id)
            page.views += 1
            page.save()

            return HttpResponseRedirect(page.url)

    return HttpResponseRedirect('/rango/')

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == "GET":
        cat_id = request.GET['category_id']

    likes = 0

    if cat_id:
        print cat_id    
        category = Category.objects.get(id = int(cat_id))
        if category:
            print "category", category
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

def get_category_list(max_categories = 0, starts_with = ''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith = starts_with)
    else:
        cat_list = Category.objects.all()

    if max_categories > 0:
        if len(cat_list) > max_categories:
            cat_list = cat_list[:max_categories]

    for cat in cat_list:
        cat.url = encoding(cat.name)

    return cat_list

def suggest_category(request):
    context = RequestContext(request)
    starts_with = ''
    cat_list = []

    if request.method == "GET":
        starts_with = request.GET['suggestion']
    else:
        starts_with = request.POST['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render_to_response('rango/category_list.html', {'categories': cat_list}, context)

