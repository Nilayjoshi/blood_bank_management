from django.shortcuts import render, get_object_or_404, redirect
from login.models import CustomUser
from .models import BloodRequest, Donor, BloodInventory, Hospital
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password


def hospital_user_signup(request):
    if request.method == 'POST':
        hospital_name = request.POST['hospital_name']
        city = request.POST['city']
        area = request.POST['area']
        phone_number = request.POST.get('phone_number', '1234567890')
        email = request.POST['email']
        password = request.POST['password'] 
        
        if not Hospital.objects.filter(email=email).exists():
            user = Hospital(hospital_name=hospital_name, city=city, area=area, phone_number=phone_number, email=email, password=make_password(password))
            user.save()
            request.session['user_id'] = user.id
            return redirect('hospital:hospital_list', hospital_id=user.pk)
        else:
            messages.error(request, 'Email already exists.')
    return render(request, 'hospital_signup.html')

def hospital_user_login(request):
    if request.method == 'POST':
        hospital_name = request.POST.get('hospital_name')
        password = request.POST.get('password')
        try:
            user = Hospital.objects.get(hospital_name=hospital_name)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['is_hospital'] = True
                return redirect('hospital:hospital_list', hospital_id=user.pk)
            else:
                messages.error(request, 'Invalid password.')
        except Hospital.DoesNotExist:
            messages.error(request, 'Hospital does not exist.')
    return render(request, 'hospital_login.html')

def hospital_logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return render(request, 'hospital_logout.html')

def hospital_list(request, hospital_id):
    user_id = request.session.get('user_id')
    if user_id:
        hospital = get_object_or_404(Hospital, id=hospital_id)
        inventory = BloodInventory.objects.filter(hospital=hospital)
        donors = Donor.objects.filter(hospital=hospital)
        
        return render(request,'hospital_list.html', {'donors': donors, 'inventory':inventory, 'hospital':hospital})
    messages.error(request, 'Session is not established. Please Login Again.')
    return render(request, 'hospital_login.html')

def manage_inventory(request, hospital_id):
    user_id = request.session.get('user_id')
    if user_id:
        hospital = get_object_or_404(Hospital, id=hospital_id)
        inventory = BloodInventory.objects.filter(hospital=hospital)
        blood_groups = BloodInventory.BLOOD_GROUPS

        if request.method == 'POST':
            blood_group = request.POST.get('blood_group')
            quantity = int(request.POST.get('quantity'))
            
            if not blood_group or not quantity:
                messages.error(request, "Please fill out all fields.")
            else:
                # Check if this blood group already exists for this hospital
                existing_inventory = BloodInventory.objects.filter(hospital=hospital, blood_group=blood_group).first()
                if existing_inventory:
                    # Update the quantity if it exists
                    existing_inventory.quantity += quantity
                    existing_inventory.save()
                else:
                    # Create a new entry if it does not exist
                    BloodInventory.objects.create(hospital=hospital, blood_group=blood_group, quantity=quantity)
                messages.success(request, 'Blood Imported Successfully.')
                return redirect('hospital:manage_inventory', hospital_id=hospital.id)

        return render(request, 'manage_inventory.html', {
            'hospital': hospital,
            'inventory': inventory,
            'blood_groups': blood_groups,
        })
    messages.error(request, 'Session is not established. Please Login Again.')
    return redirect('hospital:manage_inventory', hospital_id=hospital.id)

def donate_blood(request, hospital_id):
    user_id = request.session.get('user_id')
    if user_id:       
        hospital = get_object_or_404(Hospital, id=hospital_id)
        donors = Donor.objects.filter(hospital=hospital)
        if request.method == 'POST':
            donor_id = request.POST.get('donor_name')
            blood_group = request.POST.get('blood_group')
            donor_city = request.POST.get('donor_city')
            donor_area = request.POST.get('donor_area')
            donor_phone_number = request.POST.get('donor_phone_number')
            quantity = request.POST.get('quantity')

            donor_user = CustomUser.objects.get(id=donor_id)

            donor = Donor(
            donor_name=donor_user,
            hospital=hospital,
            blood_group=blood_group,
            donor_city=donor_city,
            donor_area=donor_area,
            donor_phone_number=donor_phone_number
            )
            donor.donate_blood(int(quantity))
            messages.success(request, 'Blood donated successfully.') 
            return redirect('hospital:hospital_list', hospital_id=hospital.id)
        else:
            users = CustomUser.objects.all()
            donors = Donor.objects.filter(hospital=hospital)
            return render(request, 'donate_blood.html', {'users': users, 'donors': donors, 'hospital': hospital})
    messages.error(request, 'Session is not established. Please Login Again.')
    return render(request, 'donate_blood.html')

def request_blood(request):
    user_id = request.session.get('user_id')
    if user_id:
        if request.method == 'POST':
            hospital_id = request.POST.get('hospital_id')
            blood_group = request.POST.get('blood_group')
            quantity = int(request.POST.get('quantity'))

            hospital = get_object_or_404(Hospital, id=hospital_id)
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, 'User not logged in.')
                return redirect('login:login')
            
            try:
                custom_user = CustomUser.objects.get(id=request.session.get('user_id'))
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('login:login')

            if BloodInventory.objects.filter(hospital=hospital, blood_group=blood_group, quantity__gte=quantity).exists():
                blood_request = BloodRequest.objects.create(
                    hospital=hospital,
                    patient=custom_user,
                    blood_group=blood_group,
                    quantity=quantity,
                    status='PENDING'
                )
                blood_request.save()
                messages.success(request, 'Blood request submitted successfully.')
                request.session['user_id'] = user_id
                return redirect('login:home')
            else:
                messages.error(request, 'Current Quantity is not available in inventory.')
                return redirect('hospital:request_blood')
        
        hospitals = Hospital.objects.all()
        return render(request, 'request_blood.html', {'hospitals': hospitals})
    messages.error(request, 'Session is not established. Please Login Again.')
    return render(request, 'request_blood.html')

def manage_requests(request, hospital_id):
    user_id = request.session.get('user_id')
    if user_id:       
        hospital = get_object_or_404(Hospital, id=hospital_id)
        requests = BloodRequest.objects.filter(hospital=hospital)

        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')
            blood_request = get_object_or_404(BloodRequest, id=request_id)

            if action == 'accept':
                blood_request.status = 'ACCEPTED'
                blood_request.save()
                inventory = BloodInventory.objects.get(hospital=hospital, blood_group=blood_request.blood_group)
                inventory.quantity -= blood_request.quantity
                inventory.save()
                messages.success(request, 'Blood request accepted.')
            elif action == 'reject':
                blood_request.status = 'REJECTED'
                blood_request.save()
                messages.success(request, 'Blood request rejected.')

            return redirect('hospital:manage_requests', hospital_id=hospital.id)

        return render(request, 'manage_requests.html', {'hospital': hospital, 'requests': requests})
    messages.error(request, 'Session is not established. Please Login Again.')
    return render(request, 'manage_requests.html')
    
def request_history(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = get_object_or_404(CustomUser, pk=user_id)
        accepted_requests = BloodRequest.objects.filter(patient=user)
        return render(request, 'request_history.html', {'user': user, 'accepted_requests': accepted_requests})
    else:
        messages.error(request, 'Session is not established. Please Login Again.')
        return redirect('login:login')
    