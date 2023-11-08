from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.views import View

from .models import Problems
from .forms import ProblemsForm, ProblemsUpdateStatusForm, ProblemEditForm

from datetime import date
from random import randint


# Create your views here.

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'login\signup.html'

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('show_problems_moder')
        else:
            return render(request, 'login/login.html', {'error_message': 'Invalid login'})
    else:
        return render(request, 'login/login.html')

def logout_usr(request):
    logout(request)
    return redirect('/')

def add_problem(request):
    reception_group = Group.objects.get(name='Reception')
    assigned_users = reception_group.user_set.all()
    # print(assigned_users, type(assigned_users))
    assigned_users_indexes = [i for i in range(len(assigned_users))]
    random_index = randint(assigned_users_indexes[0], assigned_users_indexes[-1])

    if request.method == 'POST':
        form = ProblemsForm(request.POST)
        if form.is_valid():
            problem = form.save(commit=False)
            # problem.date = date.today()
            problem.assigned_user = assigned_users[random_index]
            problem.resolved_user = problem.assigned_user
            problem.save()
            return redirect('success')
        else:
            return render(request, 'problem/add_problem.html', {'form': form})
    else:
        form = ProblemsForm()
    
    return render(request, 'problem/add_problem.html', {'form': form, 'assigned_user': assigned_users[random_index]})

def success(request):
    return render(request, 'problem/success.html')

def delete_problem(request, problem_id):
    problem = get_object_or_404(Problems, pk=problem_id)
    
    if request.method == 'POST':
        problem.delete()
    
    return redirect('show_problems_moder')

@login_required
def show_problems_moder(request):
    problem = Problems.objects.all()
    return render(request, 'problem/all_problems.html', {'problems': problem})


# @login_required
# class ProblemListView(View):
#     template_name = 'all_problems.html'
    
#     def get(self, request):
    
#         user = request.user
    
#         if user.groups.filter(name='Reception').exists():
#             problems = Problems.objects.all()
#         else:
#             problems = Problems.objects.filter(assigned_user=user)
        
#         return render(request, self.template_name, {'problems': problems})

@login_required
def problem_page(request, problem_id):
    problem = get_object_or_404(Problems, id=problem_id)

    if request.method == 'POST':
        form = ProblemsUpdateStatusForm(request.POST, instance=problem)
        if form.is_valid():
            form.save()
            return redirect('show_problems_moder')

    else:
        form = ProblemsUpdateStatusForm(instance=problem)

    return render(request, 'problem/problem.html', {'problem': problem, 'form': form})

@receiver(post_save, sender=Problems)
def assign_reception_user(sender, instance, created, **kwargs):
    if created:
        reception_group = Group.objects.get(name='Reception')
        reception_users = reception_group.user_set.all()
        if reception_users:
            instance.assigned_user = reception_users[0]
            instance.save()

@receiver(pre_save, sender=Problems)
def update_assigned_and_resolved_user(sender, instance, **kwargs):
    try:
        old_problem = Problems.objects.get(pk=instance.pk)
    except Problems.DoesNotExist:
        old_problem = None
    
    if instance.status in ['resolved', 'confirmed']:
        if instance.assigned_user:
            instance.resolved_user = instance.assigned_user
        else:
            tester_group = Group.objects.get(name='Tester')
            tester_users = tester_group.user_set.all()
            if tester_users:
                instance.resolved_user = tester_users[0]

    if old_problem and old_problem.status in ['resolved', 'confirmed'] and instance.status not in ['resolved', 'confirmed']:
        instance.resolved_user = None

@login_required
def change_problem_status(request, problem_id):
    problem = get_object_or_404(Problems, pk=problem_id)
    
    if request.user.groups.filter(name='Reception').exists():
        form = ProblemsUpdateStatusForm(request.POST or None, instance=problem)
        
        if request.method == 'POST' and form.is_valid():
            problem = form.save(commit=False)
            if problem.status == 'confirmed' or problem.status == 'resolved':
                problem.save()
                return redirect('problem-list')
            else:
                form.add_error('status', 'Invalid status for Reception group.')
    else:
        form = ProblemsUpdateStatusForm(request.POST or None, instance=problem)
        
        if request.method == 'POST' and form.is_valid():
            problem = form.save()
            return redirect('problem-list')
    
    return render(request, 'change_problem_status.html', {'form': form, 'problem': problem})

@login_required
def edit_problem(request, problem_id):
    problem = get_object_or_404(problem, pk=problem_id)
    
    if (request.user == problem.assigned_user) or request.user.groups.filter(name='Tester').exists():
        if request.method == 'POST':
            form = ProblemEditForm(request.POST, instance=problem)
            if form.is_valid():
                form.save()
                return redirect('problem-detail', problem_id=problem.id)
        else:
            form = ProblemEditForm(instance=problem)
        
        return render(request, 'edit_problem.html', {'form': form, 'problem': problem})
    else:
        return redirect('problem-detail', problem_id=problem.id)