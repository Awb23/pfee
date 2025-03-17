from django.contrib import admin

# Register your models here.
from . models import  Word , Category , Paragraph , UserProgress , UserCategoryScore

admin.site.register(UserProgress)
admin.site.register(Word)
admin.site.register(UserCategoryScore)


admin.site.register(Category)
admin.site.register(Paragraph)


