from django.urls import path
from users import views 
from .form import LoginForm , RESETFORM 


from django.contrib.auth import views as authv
urlpatterns = [
   


    path('', views.last_product , name = 'home'),
    path("accounts/sign up/",views.Sign.as_view(),name="sign" ),
path("loug out",views.loug,name="logout" ),
path('link-child/', views.link_child, name='link_child'),
    path('parent-profile/', views.parent_profile, name='parent_profile'),
    # باقي الـ URLs
path("accounts/login/",authv.LoginView.as_view(template_name="pas/login.html",authentication_form=LoginForm),name="login" ),
]