from django.shortcuts import render
from .form import NEW, LoginForm
from .models import CustomUser , Child , Parent
from .emailv import send_verification_email
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import logout, login, authenticate
# Create your views here.
def last_product(request):
    po = 44
    return render(request, 'index.html', {'po': po})



from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .form import NEW
from .models import CustomUser
from django.contrib import messages
from django.shortcuts import render, redirect

class Sign(View):
    def get(self, request):
        form = NEW()
        return render(request, "pas/sign.html", {'form': form})

    def post(self, request):
        form = NEW(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # تفعيل الحساب مباشرة
            role = form.cleaned_data.get('role')

            if role == 'parent':
                user.is_parent = True
                user.is_child = False
                user.role = 'parent'
                user.save()
                messages.success(request, "Parent account created successfully! You can now log in.")
            
            elif role == 'child':
                user.is_child = True
                user.is_parent = False
                user.role = 'child'
                user.save()
                invitation_code = user.generate_invitation_code()
                messages.success(request, f"Child account created! Your invitation code is: {invitation_code}. Share it with your parent.")
            
            return render(request, "pas/sign.html", {'form': form})  # عرض الرسائل على نفس الصفحة
        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, "pas/sign.html", {'form': form})
#a3a3a323-6e5d-4655-b070-37b96c61d3dd


@login_required
def loug(request):
    logout(request)
    return redirect("home")    


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import CustomUser

@login_required
def link_child(request):
    if not request.user.is_parent:
        messages.error(request, "Only parents can link children.")
        return redirect('home')

    if request.method == 'POST':
        invitation_code = request.POST.get('invitation_code')
        try:
            child = CustomUser.objects.get(invitation_code=invitation_code, is_child=True, parent__isnull=True)
            child.parent = request.user
            child.invitation_code = None
            child.save()
            messages.success(request, f"{child.username} has been linked to your account!")
            return redirect('parent_profile')
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid or already used invitation code.")
            return redirect('home')  # أو صفحة أخرى
    
    return redirect('home')  # إذا كان GET، يرجع للصفحة الرئيسية


@login_required
def parent_profile(request):
    user = request.user
    if user.is_parent:
        children = user.children_users.all()
        return render(request, 'pas/parent_profile.html', {'children': children})
    else:
        messages.error(request, "You are not a parent.")
        return redirect('home')