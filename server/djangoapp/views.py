from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake, CarDealer, DealerReview
from .restapis import get_dealers_from_cf,get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, get_request,post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


def login_request(request):
    context = {}

    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)


def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)

    return redirect('djangoapp:index')


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://65ad4a99.eu-de.apigw.appdomain.cloud/car-dealerships/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context = {"dealerships":dealerships}

        return render(request, 'djangoapp/index.html', context)



def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}

        dealer_url = "https://65ad4a99.eu-de.apigw.appdomain.cloud/car-dealerships/api/dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        if(not dealer):
            return HttpResponseRedirect(reverse(viewname='djangoapp:get_dealerships'))
        

        context["dealer"] = dealer
    
        review_url = "https://65ad4a99.eu-de.apigw.appdomain.cloud/car-dealerships/api/review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        context["reviews"] = reviews

        return render(request, 'djangoapp/dealer_details.html', context)


def add_review(request, id):
    context = {}
    dealer_url =  "https://65ad4a99.eu-de.apigw.appdomain.cloud/car-dealerships/api/dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        context["cars"] = cars
        context["dealer_id"] = id
        
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
                    payload["purchase_date"] = request.POST["purchasedate"]
                    payload["car_make"] = car.make.name
                    payload["car_model"] = car.name
                    payload["car_year"] = int(car.year.strftime("%Y"))


            new_payload = {}
            new_payload["review"] = payload
            review_post_url = "https://65ad4a99.eu-de.apigw.appdomain.cloud/car-dealerships/api/review"
            post_request(review_post_url, new_payload, id=id)
        return redirect("djangoapp:dealer_details", id=id)      