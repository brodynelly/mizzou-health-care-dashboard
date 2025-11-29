"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import UserDetailView
from documents.views import DrugAutocompleteView

urlpatterns = [
    path("", include("pages.urls")),
    path("", include("documents.urls")),

    #user management
    path('accounts/', include('allauth.urls')),  # Include all other AllAuth URLs
    path("admin/", admin.site.urls),
    #patient management
    path("patient/", include("patients.urls")),
    path('editor/', include('django_summernote.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('api/drug-autocomplete/', DrugAutocompleteView.as_view(), name='drug_autocomplete'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
