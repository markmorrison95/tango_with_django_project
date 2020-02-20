from django.shortcuts import render
from rango.models import Page
from django.http import HttpResponse
from rango.models import Category
from rango.forms import CategoryForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict ={}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] =  category_list
	context_dict['pages'] = page_list


	return render(request, 'rango/index.html', context = context_dict)


def about(request):
    print(request.method)
    print(request.user)

    return render(request, 'rango/about.html',{})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

       
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:

            if user.is_active:


                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:


                error_msg = "Your Rango account is disabled."
                return render(request, 'rango/login.html', {'error_msg': error_msg})
        else:
            error_msg = "Invalid login details: {0}, {1}".format(username, password)
            return render(request, 'rango/login.html', {'error_msg': error_msg})
        

    else:

        return render(request, 'rango/login.html', {})

def show_category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug=category_name_slug)

		pages = Page.objects.filter(category=category)

		context_dict['pages'] = pages

		context_dict['category'] = category

	except Category.DoesNotExist:

		context_dict['category'] = None

		context_dict['pages'] = None

	return render(request, 'rango/category.html', context = context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    #a http post?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #check if provided form valid
        if form.is_valid():
            #save new cat to database
            category = form.save(commit=True)
            print(category, category.slug)
            #saved, so give ok message
            #most recent cat added is on index page, thus take user back to index
            return index(request)
        else:
            #form contained errors, print to terminal.
            print(form.errors)
    #will handle the bad form, new form, or no form supplied cases.
    #render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)



