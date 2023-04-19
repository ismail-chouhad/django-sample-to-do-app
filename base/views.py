from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from .models import Task
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import auth


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    return redirect('register')
                else:
                    user = User.objects.create_user(
                        username=username, email=email, password=password)
                    user.save()
                    auth_user = authenticate(
                        request, username=username, password=password)
                    login(request, auth_user)
                    return redirect('tasks')
        else:
            return redirect('register')
    else:
        return render(request, 'base/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            return redirect('login')
    else:
        return render(request, 'base/login.html')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required
def tasks(request):
    tasks = Task.objects.all()
    context = {
        'tasks': tasks.filter(user=request.user),
        'count': tasks.filter(complete=False, user=request.user).count()
    }
    return render(request, 'base/tasks.html', context)


@login_required
def details(request, id):
    details = Task.objects.filter(id=id)
    template = loader.get_template('base/details.html')
    context = {
        'details': details,
    }
    return HttpResponse(template.render(context, request))


@login_required
def create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        user = request.user
        task = Task.objects.create(
            title=title, description=description, user=user)
        task.save()
        return redirect('tasks')
    else:
        template = loader.get_template('base/create.html')
        return HttpResponse(template.render({}, request))


@login_required
def update(request, id):
    task = Task.objects.get(id=id)
    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST['description']
        if 'complete' in request.POST:
            complete = request.POST['complete']
            if complete == 'on':
                task.complete = True
            else:
                task.complete = False
        task.save()
        return redirect('tasks')
    else:
        template = loader.get_template('base/update.html')
        context = {
            'task': task,
        }
        return HttpResponse(template.render(context, request))


@login_required
def delete(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect('tasks')
