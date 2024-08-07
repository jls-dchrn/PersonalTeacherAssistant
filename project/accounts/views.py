from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import os
from pathlib import Path
import pickle
from Smallfunctions import gpt

# BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = /home/hayato/PersonalTeacherAssistant/project

def signup_view(request):
    if request.method == 'POST':

        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            user_name = form.cleaned_data.get('username')

            # path = str(BASE_DIR)+'/contexts/'+str(user_name)+'.csv'
            # f = open(path, 'w')
            # f.write('')
            # f.close()
            gpt_ = gpt(user=user_name)
            # dill.dump(gpt_, open('../contexts'+str(user_name)+'.pickle','wb'))
            with open('./contexts/'+str(user_name)+'.pickle', 'wb') as f:
                pickle.dump(gpt_.sessionmemory, f)

            return redirect(to='/')


    else:
        form = SignupForm()
    
    param = {
        'form': form
    }

    return render(request, 'signup.html', param)

def login_view(request):
    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == 'None':
                    return redirect(to='/app/user/')
                else:
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get('next')

    param = {
        'form': form,
        'next': next
    }

    return render(request, 'login.html', param)


def logout_view(request):
    user = request.user
    os.remove('./contexts/'+str(user)+'.pickle')
    logout(request)

    return render(request, 'logout.html')

@login_required
def user_view(request):
    user = request.user

    params = {
        'user': user
    }

    return render(request, 'index.html', params)

@login_required
def other_view(request):
    users = User.objects.exclude(username=request.user.username)

    params = {
        'users': users
    }

    return render(request, 'other.html', params)