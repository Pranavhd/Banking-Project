"""BankingSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin, auth
from django.contrib.auth import views as auth_views
from BankingSystem.Users import views as users_views
from BankingSystem.Logs import views as logs_views

urlpatterns = [
    # admin
    url(r'^admin/', admin.site.urls),

    url(r'^users/external/getdetails/$', users_views.view_personal_details, name='view_personal_details'),
    url(r'^users/external/updatedetails/$', users_views.update_personal_details, name='update_personal_details'),
    # login & logout
    url(r'^login/$', auth_views.LoginView.as_view()),
    url(r'^logout/$', auth_views.LogoutView.as_view()),
    # users
    url(r'^users/internal/create/$', users_views.create_internal_user),
    url(r'^users/internal/update/$', users_views.update_internal_user),
    url(r'^users/internal/delete/$', users_views.delete_internal_user),
    # log
    url(r'^logs/log/system/$', logs_views.get_system_log),
]
