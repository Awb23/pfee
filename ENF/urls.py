from django.urls import path
from ENF import views 



from django.contrib.auth import views as authv
urlpatterns = [
   


   
     path('catiers/', views.category_list , name = 'cat'),
      path('next_word/<str:category_name>/<int:level>/', views.next_word, name='next_word'),
     path('category/<str:category_name>/<int:level>/', views.level_view, name='level_view'),
     
     
     
      
      
   
     
   
]