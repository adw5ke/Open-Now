from django.shortcuts import render

from django.db import models
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from .models import Business, Forum, Discussion
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from .forms import * 
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.views import generic
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import *
import folium
from django.urls import path
from .models import Login


def login(request):
    return render(request, 'open_now/login.html')


class LoginView(generic.ListView):
    template_name = 'open_now/login.html'

    def get_queryset(self):
        """
        """
        return

class HomeView(generic.ListView):
    template_name = 'open_now/home.html'

    def get_queryset(self):
        """
        """
        return

class AboutView(generic.ListView):
    template_name = 'open_now/about.html'

    def get_queryset(self):
        """
        """
        return

class BusinessView(generic.ListView):
    template_name = 'open_now/business_list.html'
    context_object_name = 'business_list'

    def get_queryset(self):
        """
        """
        return Business.objects.all()
        return

class BusinessFormView(generic.CreateView):
    model = Business
    template_name = 'open_now/business_form.html'
    fields = ('business_name','description','website','phone_number','business_category')
    def get_success_url(self):
        return reverse('open_now:business_list')
    def get_queryset(self):
        """
        """
        return

def get_business(request):

    business_name = request.POST['business_name']
    description = request.POST['description']
    phone_number = request.POST['phone_number']
    website = request.POST['website']
    business_category = request.POST['business_category']
    t = Business(business_name=business_name,description=description, phone_number = phone_number, website = website,
                 business_category = business_category)
    t.save()
    return HttpResponseRedirect(reverse('open_now:business_list'))

def search_business(request):
    srh = request.GET['query'].lower().strip()
    businesses = Business.objects.filter(business_name__icontains=srh) | Business.objects.filter(description__icontains=srh) | Business.objects.filter(business_category__icontains=srh)
    params={'businesses': businesses, 'search':srh}
    return render(request, 'open_now/search_business.html', params)

def new_forum(request):
    
    form = CreateInForum()
    if request.method == 'POST':
        forum = Forum(email = request.user)
        form = CreateInForum(request.POST, instance=forum)
        if form.is_valid():
            forum.save()
            return redirect('/open_now/forums')
    context ={'form':form}
    return render(request,'open_now/new_forum.html',context)
    # email=request.user.email
    # topic= request.POST['topic']
    # description = request.POST['description']
    # newForum = Forum(email=email, topic=topic, description=description)
    # newForum.save()
    # return HttpResponseRedirect(reverse('open_now:forums'))
    

def discuss(request, pk):
    discussion = Forum.objects.get(id=pk)

    context = {'f': discussion}

    return render(request, 'open_now/new_discussion.html', context)
 
def new_discussion(request):
    # user = request.user
    discuss = request.POST['discuss']
    forum_topic = request.POST['forum']
    forum = Forum.objects.get(id=forum_topic)
    newDiscuss = Discussion(forum=forum ,discuss=discuss, email = request.user)
    newDiscuss.save()
    return HttpResponseRedirect(reverse('open_now:forums'))

def forums(request):
    all_forums=Forum.objects.all()
    count=all_forums.count()
    discussions=[]
    for i in all_forums:
        discussions.append(i.discussion_set.all())
 
    context={'forums':all_forums,
            'count':count,
            'discussions':discussions}
    return render(request,'open_now/forums.html',context)


def business_specs(request, business_name):
    business = Business.objects.get(business_name__startswith=business_name)

    context = {'business': business, 'reviews': business.review_set.all(), 'hours': business.openinghours_set.last()}

    return render(request, 'open_now/business_specs.html', context)

def get_review(request):

    business_name = request.POST['business_name']
    b = Business.objects.get(business_name__startswith=business_name)

    review_text = request.POST['review_text']
    rating = request.POST['rating']
    b.review_set.create(review_text = review_text, rating = rating, user = request.user)
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)


def get_hours(request):

    business_name = request.POST['store']
    b = Business.objects.get(business_name__startswith=business_name)

    weekday_from = request.POST['weekday_from']
    weekday_to = request.POST['weekday_to']
    from_hour = request.POST['from_hour']
    to_hour = request.POST['to_hour']


    b.openinghours_set.create(weekday_from = weekday_from, weekday_to = weekday_to, from_hour = from_hour,
                              to_hour = to_hour)

    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)



def location_view(request):

    # initial folium map focused on the center of the City of Charlottesville
    # center of US coords 40.619290458576074, -95.65487442647927
    m = folium.Map(width='100%', height='100%', location=get_center_coordinates(38.02931,-78.47668), zoom_start=13)
    m = m._repr_html_()

    form = LocationForm()
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/open_now/map/display/')


    context = {
        'form': form,
        'map': m,
    }
    return render(request, 'open_now/location.html', context)


def map_view(request):

    locations = Location.objects.all()
    count = locations.count()
    lat = None
    lng = None

    if count > 1:
        # print("There is more than one current location")
        pass

    # set the current location to the last location in the database
    current_location = locations[count-1]

    # get all of the fields
    street_address = current_location.street_address
    address_2 = current_location.address_2
    city = current_location.city
    state = current_location.state
    postal_code = current_location.postal_code

    # create the properly formatted address or postal code
    # does not factor in alternate info
    address_or_postal_code = str(street_address) + ', ' + str(city) + ', ' + str(state) + ' ' + str(postal_code)

    # get the latitude and longitude for the current location
    client = GoogleMapsClient(api_key=GOOGLE_API_KEY, address_or_postal_code=address_or_postal_code)
    lat, lng = client.lat, client.lng
    pointA = (lat, lng)

    # print(lat, lng)

    # ---------------------------------------------------------------------------------------- #
    # folium map with current location marked
    m = folium.Map(width='100%', height='100%', location=get_center_coordinates(lat, lng), zoom_start=17)

    folium.Marker([lat, lng], tooltip=address_or_postal_code, popup='You are here', icon=folium.Icon(color='red')).add_to(m)


    form = SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            search_category = form.cleaned_data.get('search_category')
            radius = form.cleaned_data.get('radius')

        # perform the search based on a keywork ex: "Mexican Food" or "Bagels"
        # radius is in meters
        # results = client.search(keyword=search_category, radius=radius*1000, location=address_or_postal_code)


        # get all the businesses that have been submitted and perform a search using the google maps API
        businesses = Business.objects.all()
        count = businesses.count()

        for business in businesses:

            # make sure we are searching for the correct type of business
            if search_category == business.business_category:

                result = client.search(keyword=business.business_name, radius=radius*1000, location=address_or_postal_code)

                min_distance = 1000000
                index = -1
                lat_f = -1
                lng_f = -1
                rough_address_f = ''
                name_f = ''

                # for multiple locations of a business, get the closest one
                for i in range(len(result['results'])):

                    lat_result = result['results'][i]['geometry']['location']['lat']
                    lng_result = result['results'][i]['geometry']['location']['lng']
                    rough_address = result['results'][i]['vicinity']
                    name = result['results'][i]['name'] 
                    pointB = (lat_result, lng_result)

                    distance_km = calculate_distance(pointA, pointB)

                    if distance_km < min_distance:
                        min_distance = distance_km
                        index = i
                        lat_f = lat_result
                        lng_f = lng_result
                        rough_address_f = rough_address
                        name_f = name


                # print(result['results'][index]['name'], end="")
                # print(" " + result['results'][index]['vicinity'], end="")
                # print(" --> " +  str(distance_km))

                # mark it on the map
                link = f"/open_now/businesses/{business.business_name}/"
                test = folium.Popup('<a href="'+ link +'"target="window">'+ name_f + '</a>')
                folium.Marker([lat_f, lng_f], tooltip=rough_address_f, popup=test, zoom_start=radius+3).add_to(m)

                # popup = folium.Popup('<a href=" [URL GOES HERE] \"target=\"_blank\"> [text for link goes here]\" </a>')


    m = m._repr_html_()

    context = {
        'form': form,
        'map': m,
    }
    return render(request, 'open_now/map.html', context)
    
def create_businessimage(request):
    form = BusinessImageForm()
    if request.method == 'POST':
        form = BusinessImageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/open_now/business-form')
    context = { 'form':form }
    return render(request,'open_now/business-form/create-businessimage.html',context)

"""def createNewBusiness(request):
    form = CreateBusinessForm()
    if request.method == 'POST':
        form = CreateBusinessForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/open_now/business-form')
    else:
        form = CreateBusinessForm()
    context={'form':form}
    return render(request, 'open_now/business_form.html',context)"""