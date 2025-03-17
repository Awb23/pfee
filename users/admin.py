from django.contrib import admin

# Register your models here

from django.contrib import admin


from . models import CustomUser,Parent,Child


admin.site.register(CustomUser)
admin.site.register(Parent)
admin.site.register(Child)
