from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (Amenities, Hotel)
from django.db.models import Q


def home(request):

    return render(request, 'home.html')


def hotels(request):
    amenities_obj = Amenities.objects.all()
    hotel_obj = Hotel.objects.all()

    # query for sorting
    sort_by = request.GET.get('sort_by')

    if sort_by:
        sort_by = request.GET.get('sort_by')
        if sort_by == 'ASC':
            hotel_obj = hotel_obj.order_by('hotel_price')
        elif sort_by == 'DSC':
            hotel_obj = hotel_obj.order_by('-hotel_price')

    # query for search
    search = request.GET.get('search')

    if search:
        hotel_obj = hotel_obj.filter(
            Q(hotel_name__icontains=search) | Q(place__icontains=search) | Q(
                amenities__amenity_name__icontains=search)
        ).distinct()

    context = {'amenities_obj': amenities_obj,
               'hotel_obj': hotel_obj,
                'sort_by': sort_by, 
                'search': search
    }
    return render(request, 'hotels.html', context)



# hotel detail view....................................

def hotel_detail(request, uid):
    try:
        hotel_obj = Hotel.objects.get(uid=uid)
    except Hotel.DoesNotExist:
        hotel_obj = None

    if hotel_obj:
         # Calculate the total amount including GST
        gst_percentage = hotel_obj.gst_percentage
        gst_amount = (gst_percentage / 100) * hotel_obj.hotel_price
        total_amount = hotel_obj.hotel_price + gst_amount

        # Calculate the price to pay (after applying the instant discount)
        discount = hotel_obj.actual_price - hotel_obj.hotel_price

        # Make sure hotel_discount is not negative
        hotel_discount = max(discount, 0)

        context = {
            'hotel_obj': hotel_obj,
            'gst_percentage':gst_percentage,
            'hotel_discount': hotel_discount,
            'gst_amount':gst_amount,
            'total_amount': total_amount,

        }

        return render(request, 'hotel_detail.html', context)
    else:
        # Handle the case where the hotel with the given UID does not exist
        messages.error(request, "Hotel not found")
        # You can replace 'some_redirect_view' with an appropriate URL
        return redirect('/home')


# login view

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print("Username:", username)
        # print("Password:", password)

        user = authenticate(request, username=username, password=password)

        # print("User:", user)
        if user is not None:
            login(request, user)
            # Check if there's a 'next' parameter in the URL
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)  # Redirect to the 'next' URL
            return redirect('home')  # Default redirect after login
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'error_message': messages.get_messages(request)})

# @login_required(login_url='home')  # Redirects authenticated users to the 'home' page


def register_view(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.warning(request, "Passwords do not match!")
            # Redirect back to the registration page with the error message
            return redirect('/register')

        user_obj = User.objects.filter(username=username)

        if user_obj.exists():
            messages.error(request, "Username already exists!")
            # Redirect back to the registration page with the error message
            return redirect('/register')

        user = User.objects.create_user(
            username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Register successfully!")
        # Redirect to the login page after successful registration
        return redirect('/login')

    # Show the registration form for non-authenticated users
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def payment(request):
    return render(request , 'payment.html')
