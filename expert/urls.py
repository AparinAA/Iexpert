"""expert URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from xml.etree.ElementInclude import include

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import userexpert.views
from expert import views
from app import views as app_views
from userexpert import views as exp_views
from info import views as info_views
from score import views as score_views
from result import views as result_views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
]

urlpatterns += [
    path('expert/<int:pk>/', exp_views.ExpertOneViews, name='expert-detail'),
    path('expert/<int:pk>/update/', exp_views.ExpertUpdate.as_view(), name='expert_update'),
    path('experts/', exp_views.ExpertViews, name='experts'),
    path('commission/<int:pk>/', exp_views.ExperGroupOneViews, name='commission-detail'),
]

urlpatterns += [
    path('company/', info_views.CompanyView, name='company'),
    path('company/<int:pk>/', info_views.CompanyOneView, name='company-detail'),
    path('company/create/', info_views.CompanyCreate.as_view(), name='company_create'),
]

urlpatterns += [
    path('apps/', app_views.ApplicationView, name='application'),
    path('app/<int:pk>/', app_views.ApplicationOneView, name='application-detail'),
    path('apps/create/', app_views.ApplicationCreate.as_view(), name='application_create'),
    path('app/<int:pk>/update/', app_views.ApplicationUpdate.as_view(), name='application_update'),
]

urlpatterns += [
    path('score_common/<int:pk>/form/', score_views.ScoreCommonOne.as_view(), name='score_common_form'),
    path('score_common/<int:pk>/', score_views.ScoreCommonOneView, name='score_common_detail'),
    path('score_expert/<int:pk>/form/', score_views.ScoreExpertOne.as_view(), name='score_expert_form'),
    path('score_expert/<int:pk>/', score_views.ScoreExpertOneView, name='score_expert_detail'),
    path('score_common_all/<int:pk>/', score_views.ScoreCommonAllView, name='score_common_all_detail'),
    path('score_common_all/<int:pk>/form/', score_views.ScoreCommonAllForm.as_view(), name='score_common_all_form'),
    path('score_expert_all/<int:pk>/', score_views.ScoreExpertAllView, name='score_expert_all_detail'),
    path('score_expert_all/<int:pk>/form/', score_views.ScoreExpertAllForm.as_view(), name='score_expert_all_form'),

]
urlpatterns += [
    path('score_for_expert/<int:pk>/', result_views.AllScoreForExpertForm.as_view(), name='all_score_for_expert_form'),
    path('check_score/', result_views.AllScoreForExpertIndex, name='check_score')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
