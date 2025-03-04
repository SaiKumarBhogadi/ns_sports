from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = 'blog_app'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('',views.index,name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('blogs-management/', views.blog_management_view, name='blog_management'),
     path('contact/', views.contact_view, name='contact'),
  
    path('blogs/', views.blog_list, name='blog_list'),
    # path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('create/', views.create_blog, name='create_blog'),
    path('approve-blog/<int:blog_id>/', views.approve_blog, name='approve_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    #  path('edit-blog/<int:blog_id>/', views.edit_blog, name='edit_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('blogs/<int:blog_id>/', views.blog_detail, name='blog_detail'),  # Blog Detail
    path('blogs/<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),  # Edit Blog
    path('blogs/<int:blog_id>/reject/', views.reject_blog, name='reject_blog'),  

   path('review-blog/<int:blog_id>/', views.review_blog, name='review_blog'),


     path('jobs/', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),

    path('dashboard/applications/', views.admin_job_applications, name='admin_job_applications'),
path('dashboard/applications/<int:app_id>/<str:status>/', views.update_application_status, name='update_application_status'),



    


 path('password-reset/', views.password_reset_request_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset/success/', views.password_reset_done_view, name='password_reset_success'),




   
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)