"""
URL configuration for hw2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from helpdesk import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', views.login_view, name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.logout_usr, name='logout'),

    path('', views.add_problem, name='add_problem'),
    # path('helpdesklist/', views.ProblemListView, name='show_problems_moder'),
    path('helpdesklist/', views.show_problems_moder, name='show_problems_moder'),
    path('helpdesklist/<int:problem_id>/', views.problem_page, name='problem_page'),
    path('success/', views.success, name='success'),
    path('delete_problem/<int:problem_id>/', views.delete_problem, name='delete_problem'),

]