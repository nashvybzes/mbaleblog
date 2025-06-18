from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/',views.about,name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('news', views.blog_list, name='list'),
    path('trending/', views.trending_list, name='trending'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('<slug:slug>/', views.blog_detail, name='detail'),
    path('<slug:slug>/comment/', views.ajax_add_comment, name='ajax_comment'),
]
