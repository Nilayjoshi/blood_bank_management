from django.shortcuts import get_object_or_404, redirect, render
from hospital.models import Hospital
from login.models import CustomUser
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
def home(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = get_object_or_404(CustomUser, pk=user_id)
        blood_group = request.GET.get('blood_group')
        city = request.GET.get('city')
        area = request.GET.get('area')
        
        hospitals = Hospital.objects.all()
        
        if blood_group or city or area:
            if blood_group == 'None' or not blood_group:
                hospitals = hospitals.filter(city__icontains=city, area__icontains=area)
                blood_group = '-'
            elif not city:
                hospitals = hospitals.filter(
                    bloodinventory__blood_group=blood_group,
                    bloodinventory__quantity__gt=0,
                    area__icontains=area
                ).distinct()
            elif not area:
                hospitals = hospitals.filter(
                    bloodinventory__blood_group=blood_group,
                    bloodinventory__quantity__gt=0,
                    city__icontains=city
                ).distinct()
            else:
                hospitals = hospitals.filter(
                    bloodinventory__blood_group=blood_group,
                    bloodinventory__quantity__gt=0,
                    city__icontains=city,
                    area__icontains=area
                ).distinct()

        return render(request, 'home.html', {
            'blood_group': blood_group,
            'city': city,
            'area': area,
            'hospitals': hospitals,
            'user': user
        })
    else:
        messages.error(request, 'Session is not established. Please Login Again.')
        return redirect('login:login')

def custom_user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser(username=username, email=email, password=make_password(password))
            user.save()
            request.session['user_id'] = user.id
            return redirect('login:home')
        else:
            messages.error(request, 'Username already exists.')
    return render(request, 'signup.html')

def custom_user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = CustomUser.objects.get(username=username)
            if check_password(password, user.password):
                request.session['is_custom_user'] = True
                request.session['user_id'] = user.id
                return redirect('login:home')
            else:
                messages.error(request, 'Invalid password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
    return render(request, 'login.html')

def user_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return render(request, 'logout.html')
