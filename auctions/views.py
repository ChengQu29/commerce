from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.forms import ModelForm, Form
from .models import User, Listing, Bid, Comment, Watchlist

class createform(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'link', 'category']
        labels = {
            'title': "Listing Title:",
            'description': "Description\n(max 1,000 characters):",
            'price': "Initial Price",
            'link': "Image URL:",
            'category': "Category (Choose one):"
        }

#the cs50web class method for creating forms
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Enter your comment', 'id': 'comment'}))

class BidForm(forms.Form):
    bid = forms.DecimalField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter amount', 'id': 'bid'}))

def index(request):
    items = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "items": items #items has an id automatically assigned by django
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == 'POST':
        # get info from form
        form = createform(request.POST)

        if form.is_valid():
            m = Listing()
            # extract data from form
            m.title = form.cleaned_data['title']
            m.price = form.cleaned_data['price']
            m.description = form.cleaned_data['description']
            m.category = form.cleaned_data['category']
            m.user = request.user
            if not form.data['link']:
                m.link = "https://thumbs.dreamstime.com/b/no-image-available-icon-photo-camera-flat-vector-illustration-132483141.jpg"
            else:
                m.link = form.cleaned_data['link']
            m.save()

            return redirect('index')
    
    return render(request, "auctions/create.html", {
        "createform": createform()
    })

def listingpage(request, id):
    #query listings by listing id (id is assigned by django automatically)
    item = Listing.objects.get(pk=id)
    
    #query for bids for that specific listing
    bids = Bid.objects.filter(listing=item)
    
    #query for comments for that specific listing
    comments = Comment.objects.filter(listing=item)

    if request.user.is_authenticated:
        commentform = CommentForm()
        bidform = BidForm()
        # check if you're the owner of the item
        if item.user == request.user:
            owner=True
        else:
            owner=False
        # check to see if you've added this item to the watchlist
        try: 
            if Watchlist.objects.get(user=request.user, listing=id):
                added = True
        except:
            added = False

        return render(request, "auctions/listingpage.html", {
            "item": item,
            "comments": comments,
            "bids": bids,
            "commentform": commentform,
            "bidform": bidform,
            "added": added,
            "owner": owner
        })
    else:
        return render(request, "auctions/listingpage.html", {
            "item": item,
            "comments": comments,
            "bids": bids
        })

def comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        # id is provided by {{item.id}} in html forms, see listingpage.html
        id = request.POST['id']
        if form.is_valid():
            comment = Comment()
            #get comments input
            comment.comment = form.cleaned_data['comment']
            # query comment associated with a specific listing (by id)
            comment.listing = Listing.objects.get(pk=id)
            # query comment associated with user
            comment.user = request.user
            comment.save()
            return redirect('index')
    else:

        return HttpResponseRedirect(reverse("index"))

def bid(request):
    if request.method == 'POST':
        form = BidForm(request.POST)
        # id is provided by {{item.id}} in html forms
        listing = Listing.objects.get(pk=request.POST['id'])
        if form.is_valid():
            bidamount = form.cleaned_data['bid']
            if bidamount > listing.price:
                bid = Bid()
                bid.bid_price = bidamount
                bid.bidder = request.user
                bid.listing = listing
                bid.save()
                # updating listing price to the current bid amount
                listing.price = bidamount
                listing.save()
                return redirect('index')
            else:
                message = "Invalid bid. The bid amount must be greater than the current price."
                return render (request, "auctions/error.html", {
                    "message": message
                })
    else:
        return HttpResponseRedirect(reverse("index"))

def categories(request):
    categories = []
    for category in Listing.CATEGORIES:
        #display the name from CATEGORIES by category[1]; category[0] is the index
        categories.append(category[1])

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request,category):
    items = Listing.objects.filter(active=True, category=category)

    return render(request, "auctions/index.html", {
        "items": items 
    })

def addtowatch(request):
    watch = Watchlist()
    listing = Listing.objects.get(pk=request.POST['id'])
    watch.user = request.user
    watch.listing=listing
    watch.save()
    return redirect('index')

def removewatch(request):
    w = Watchlist.objects.get(user=request.user, listing=request.POST['id'])
    w.delete()
    return redirect('index')

def watchlist(request):
    #watchlist has an associated user and associated listing
    #first filter the watchlist by the associated user
    w = Watchlist.objects.filter(user=request.user)
    items = []
    # find the listing 
    for i in w:
        items.append(Listing.objects.filter(id=i.id))
        
    return render(request, "auctions/watchlist.html", {
        "items": items
    })

def close(request):
        item = Listing.objects.get(pk=request.POST['id'])
        bids = Bid.objects.filter(listing=item)
        #handle attribute error: 'NoneType' object has no attribute 'bidder'
        try:
            winner = bids.order_by('-bid_price').first().bidder
        except:
            winner = item.user #winner is yourself if nobody has placed a bid
        item.active = False
        item.winner = winner
        item.save()
        return redirect('index')

def win(request):
    items = Listing.objects.filter(winner=request.user)
    return render(request, "auctions/winning.html", {
        "items": items 
    })
