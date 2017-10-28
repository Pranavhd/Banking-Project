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
from django.conf.urls import include

urlpatterns = [
    # login & logout
    # url(r'^login/$', users_views.login_view),
    url(r'^login_post/$', users_views.login_post_view),
    url(r'^logout/$', users_views.logout_view),

    # account open
    url(r'^account_open/$', users_views.account_open_view),
    url(r'^account_open_post/$', users_views.account_open_post_view),

    # account update
    url(r'^account_update/$', users_views.account_update_view),
    url(r'^account_update_post/$', users_views.account_update_post_view),

    # account delete
    url(r'^account_delete_post/$', users_views.account_delete_post_view),

    # fund
    url(r'^make_transfer/$', users_views.make_transfer_view),
    url(r'^make_transfer_post/$', users_views.make_transfer_post_view),

    # payment
    url(r'^make_payment/$', users_views.make_payment_view),
    url(r'^make_payment_post/$', users_views.make_payment_post_view),

    # approve request
    url(r'^make_approve_request/$', users_views.make_approve_request_post_view),

    # users
    url(r'^$', users_views.index_view),
    url(r'^admin/$', users_views.admin_view),
    url(r'^tier1/$', users_views.tier1_view),
    url(r'^tier2/$', users_views.tier2_view),
    url(r'^customer/$', users_views.customer_view),
    url(r'^merchant/$', users_views.merchant_view),

    # request
    url(r'^request_approve_post/$', users_views.request_approve_post_view),

    # 2fa
    url(r'', include('two_factor.urls', 'two_factor')),

    # session
    url(r'', include('user_sessions.urls', 'user_sessions'))
]
