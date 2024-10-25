from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    #  path('/voice-subtitle', views.index, name='index'),
    path('', include('accounts.urls')),

    path('accounts', include('django.contrib.auth.urls')),
    # path('/voice-subtitle', views.upload_files, name='voice-subtitle'),
    path('submitSubtitle', views.submitSubtitle, name='submitSubtitle'),
    path('create-lead', views.edit_slides, name='create-lead'),
    path("upload_files",views.upload_files,name="upload_files"),
    path('download', views.download, name='download'),
    path('download_file/<str:filename>/', views.download_file, name='download_file'),
    path('music',views.music,name="music"),
    path('loading',views.loading,name="loading"),
    path("loadingMusic",views.loadingMusic,name="loadingMusic"),
    path("loadingforFileUpload",views.loadingforFileUpload,name="loadingforFileUpload"),
    path('checkEditing',views.checkEditing,name="checkEditing"),
    path('', include('payment.urls')),
    path("manageSubscription",views.manage_subscription,name="manage_subscription")
]
