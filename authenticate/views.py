from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django.contrib import messages 
from .forms import SignUpForm, EditProfileForm, UserProfileForm
# Create your views here.
def home(request): 
	return render(request, 'authenticate/home.html', {})

def login_user (request):
	if request.method == 'POST': #if someone fills out form , Post it 
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:# if user exist
			login(request, user)
			messages.success(request,('Youre logged in'))
			return redirect('/welcome.html') #routes to 'home' on successful login  
		else:
			messages.success(request,('Error logging in'))
			return redirect('login') #re routes to login page upon unsucessful login
	else:
		return render(request, 'authenticate/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request,('Youre now logged out'))
	return redirect('home')

'''here i am using two forms as state is not in default use form'''
def register_user(request):
	if request.method =='POST':
		form = SignUpForm(request.POST)
		profile_form=UserProfileForm(request.POST)
		if form.is_valid() and profile_form.is_valid():
			userform=form.save()
			userform.refresh_from_db()#making sure values are store in user table
			profile_form = UserProfileForm(request.POST, instance=userform.user)#was trying form.profile
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			profile_form.full_clean()
			profile_form.save()
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ('You\'re now registered'))
			return redirect('/auth/login')
	else: 
		form = SignUpForm() 
		profile_form=UserProfileForm()

	context = {'form': form,'profile_form':profile_form}
	return render(request, 'authenticate/register.html', context)

def register_user_2(request):
	if request.method =='POST':
		profile_form=UserProfileForm(request.POST)
		if profile_form.is_valid():
			profile_form = UserProfileForm(request.POST, instance=user.profile)
			username = profile_form.cleaned_data['username']
			password = profile_form.cleaned_data['password1']
			profile_form.full_clean()
			profile_form.save()
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ('You\'re now registered'))
			return redirect('/auth/login')
	else: 
		profile_form=UserProfileForm()

	context = {'profile_form':profile_form}
	return render(request, 'authenticate/register.html', context)

def edit_profile(request):#need to add state to edit profile 
	if request.method =='POST':
		form = EditProfileForm(request.POST, instance= request.user)
		if form.is_valid():
			form.save()
			messages.success(request, ('You have edited your profile'))
			return redirect('home')
	else: 		#passes in user information 
		form = EditProfileForm(instance= request.user) 

	context = {'form': form}
	return render(request, 'authenticate/edit_profile.html', context)
	#return render(request, 'authenticate/edit_profile.html',{})



def change_password(request):
	if request.method =='POST':
		form = PasswordChangeForm(data=request.POST, user= request.user)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			messages.success(request, ('You have edited your password'))
			return redirect('home')
	else: 		#passes in user information 
		form = PasswordChangeForm(user= request.user) 

	context = {'form': form}
	return render(request, 'authenticate/change_password.html', context)