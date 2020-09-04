from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_bid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    link = models.CharField(max_length=64,default=None,blank=True,null=True)
    time = models.CharField(max_length=64)
    winner = models.ForeignKey(User, null=True, default=None, on_delete=models.PROTECT, related_name="winning_listings")
    active = models.BooleanField(default=True)

    bids = models.ManyToManyField('Bid', blank=True, related_name='bids')
    
    def __str__(self):
        return f"{self.id}: {self.title} owned by {self.user} @ {self.price} active: {self.active} winner is {self.winner}"
    
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=12, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_bids')

    def __str__(self):
        return f"{self.bidder} ({self.bid_price}) @ {self.listing}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments")
    comment = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.user} commented on listing {self.listing}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watch_listing")

    def __str__(self):
        return f"{self.user} is watching {self.listing}"