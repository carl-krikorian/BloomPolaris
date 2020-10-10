from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from decimal import Decimal

"""
Models for restaurant representation
"""


class Opportunities(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    employer = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.name + " " + self.id
'''
    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False
'''

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    rows = models.IntegerField()
    columns = models.IntegerField()
    tables = models.IntegerField()
    is_ready = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Representing restaurant's menu item
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Representing restaurant's table
class Table(models.Model):
    number = models.IntegerField()
    row = models.IntegerField()
    column = models.IntegerField()
    currently_free = models.BooleanField(default=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.restaurant) + " " + str(self.number)


class Events(models.Model):
    Name = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    img = models.CharField(max_length=100,default="img.png")

    def __str__(self):
        return self.Name + " on  " + self.date

"""
Models for users representation
"""


class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, null=True, blank=True)
    accountType = models.CharField(max_length=100, null=True, blank=True, default="User")

    def __str__(self):
        return self.user.get_full_name()


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()


# Friendship between two different users
class Friendship(models.Model):
    user = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="creator")
    friend = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="friend")
    started = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        first_person = self.user.user.get_full_name()
        second_person = self.friend.user.get_full_name()
        return first_person + " and " + second_person


"""
Models for restaurant functionality
"""


class Reservation(models.Model):
    coming = models.DateTimeField('reservation time')
    duration = models.IntegerField()
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        person = self.guest.user.get_full_name()
        place = self.restaurant.name
        time = self.coming
        return person + " in " + place + " at " + str(time)

    def get_finishing_time(self):
        return self.coming + datetime.timedelta(hours=self.duration)


class ReservedTables(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.reservation) + " table: " + str(self.table)


class Visit(models.Model):
    ending_time = models.DateTimeField('ending time')
    grade = models.IntegerField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.reservation) + " ending: " + str(self.ending_time) + " for: " + str(self.guest)

    def has_ended(self):
        if self.confirmed:
            return timezone.now() > self.ending_time
        else:
            return False


class Gadget(models.Model):
    name = models.CharField(max_length=100)
    img_path = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0.00))
    Number = models.IntegerField(default=10)

    def __str__(self):
        return self.name +", Price: "+ str(self.price) + "$ , available = " + str(self.Number)


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(0.00))
    buy = 'buy'
    sell = 'sell'
    t_types = (
        (buy, 'buy'), (sell, 'sell'),
    )

    transaction_type = models.CharField(
        max_length=4, choices=t_types, )
    date = models.DateField(auto_now_add=True)
    item = models.CharField(max_length=200)

    def __str__(self):
        return 'item: ' + str(self.item) + ' of amount: $' + str(self.amount)


class Game(models.Model):
    reserver_id = models.CharField(max_length=200)
    one = '1'
    two = '2'
    three = '3'
    four = '4'
    five = '5'
    people_choices = (
        (one, 'one person'), (two, 'two people'),
        (three, 'three people'), (four, 'four people'), (five, 'five  people')
    )
    people = models.CharField(
        max_length=5, choices=people_choices, default=one)
    date_reserved = models.CharField(max_length=100)
    comment = models.TextField(blank=True)
    cards = 'cards games'
    billar = 'billar'
    chess = 'chess'
    poker = 'poker table'
    game_choices = (
        (cards, 'cards games'), (billar, 'billar'), (chess, 'chess'), (poker, 'poker table')
    )
    name = models.CharField(max_length=20, choices=game_choices)


class Apply(models.Model):
    user = models.ForeignKey(Guest, on_delete=models.CASCADE)
    event = models.ForeignKey(Opportunities, on_delete=models.CASCADE, related_name="event")

    def __str__(self):
        first_person = self.user.user.get_full_name()
        return first_person + " and " + self.event.name
