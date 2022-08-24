from django.db import models
from django.utils.timezone import now


class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False,max_length=300)
    
    def __str__(self):
        return "\nName: "+ self.name + "\nDescription: " + self.description



class CarModel(models.Model):
    make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=True,max_length=30)
    dealer_id = models.IntegerField(null=True)

    SEDAN= 'sedan'
    SUV= 'suv'
    WAGON= 'wagon'
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon')
    ]
    type = models.CharField(
        null=False,
        max_length=20,
        choices=TYPE_CHOICES,
    )
    year = models.DateField(default=now)
    def __str__(self):
        return "Name: " + self.name + "," + \
                "Make: " + str(self.make) + ","+ \
                "Dealer: " + str(self.dealer_id)+ "," + \
                "Type: " + self.type + ","+ \
                "Year: " +str(self.year)




class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st,state, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        self.state = state
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

class DealerReview:
    def __init__(self, id,name,dealership,review,purchase,purchase_date,car_make,car_model,car_year):
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.dealership = dealership
        self.id = id  # The id of the review
        self.name = name  # Name of the reviewer
        self.purchase = purchase  # Did the reviewer purchase the car? bool
        self.purchase_date = purchase_date
        self.review = review  # The actual review text
        self.sentiment = ""  # Watson NLU sentiment analysis of review

    def __str__(self):
        return "Reviewer: " + self.name + " Review: " + self.review + " Sentiment: " + str(self.sentiment)
