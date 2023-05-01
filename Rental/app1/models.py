from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count

# Create your models here.
class UserProfile(models.Model):
    gender_choice = (
        ('male','male'),
        ('female','female'),
        ('others','others')
    )
    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    gender              = models.CharField(max_length=200,blank = True, null= True, choices=gender_choice)
    phone               = models.IntegerField(null=True, blank=True)
    address             = models.TextField(blank = True, null= True)
    country             = models.CharField(max_length=200,blank = True, null= True)
    created_at          = models.DateTimeField(auto_now=True)
    updated_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# # # # # # banner and offer model # # # # #
class Offer(models.Model): 
    title               = models.TextField(blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Banner(models.Model): 
    title               = models.TextField(blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    offer               = models.ForeignKey(Offer, on_delete=models.CASCADE)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



# # # # # packages model # # # # # #
class Package(models.Model):
    country_choice = (
        ('India','India'),
        ('Nepal','Nepal'),
        ('Indo-Nepal','Indo-Nepal')
    )
    title               = models.CharField(max_length=200,blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    country             = models.CharField(max_length=200,blank = True, null= True,choices=country_choice)
    departure           = models.TextField(blank = True, null= True)
    speciality          = models.TextField(blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    map_link            = models.TextField(blank = True, null= True)
    days                = models.IntegerField(default=0)
    nights              = models.IntegerField(default=0)
    price               = models.IntegerField(default=0)
    available           = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now=True)
    updated_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} {self.country}" 

    def averagereview(self):
        reviews = Review.objects.filter(package=self).aggregate(average=(Avg('facilities')+Avg('comfort')+Avg('experience')+Avg('location'))/4)
        # reviews = self.avgfacilities + self.avgcomfort + self.avgsurroundings + self.avglocation
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
            avg = round(avg,1)

        return avg

    def countreview(self):
        reviews = Review.objects.filter(package=self).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class PackageEvent(models.Model): 
    package             = models.ForeignKey(Package, on_delete=models.CASCADE)
    title               = models.CharField(max_length=250,blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package.title


class PackageGallery(models.Model): 
    package             = models.ForeignKey(Package, on_delete=models.CASCADE)
    title               = models.CharField(max_length=250,blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.package.title

    class Meta:
        verbose_name= 'PackageGallery'
        verbose_name_plural = 'PackageGalleries'


# # # # # Gallery model # # # # #
class Gallery(models.Model): 
    title               = models.TextField(blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name= 'Gallery'
        verbose_name_plural = 'Galleries'


# # # # # review model # # # # #
class Feedback(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    title               = models.CharField(max_length=250, blank = True)
    address             = models.CharField(max_length=250, blank = True)
    review              = models.TextField(blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def userImage(self):
        profile = UserProfile.objects.get(user = self.user)
        return profile.image
    
    def __str__(self):
        return self.title  + ". User : " + self.user.username




# # # # driver model # # # # #
class Driver(models.Model):
    fullname            = models.CharField(max_length=200,blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    address             = models.TextField(blank = True, null= True)
    no_rating              = models.IntegerField(blank = True,null=True,default=0)
    rating              = models.IntegerField(blank = True,null=True,default=0)
    speciality          = models.TextField(blank = True, null= True)
    description         = models.TextField(blank = True, null= True)
    available           = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now=True)
    updated_at          = models.DateTimeField(auto_now_add=True)


    def averagereview(self):
        review = Review.objects.filter(driverSelect=self)
        reviews = review.aggregate(average=Avg('driver'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
            avg = round(avg,1)
        return avg
    
    def countreview(self):
        review = Review.objects.filter(driverSelect=self)
        reviews = review.aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


    def __str__(self):
        return self.fullname 
    
class DriverReview(models.Model):
    driver              = models.ForeignKey(Driver, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    rating              = models.IntegerField(blank = True,null=True)
    title               = models.CharField(max_length=250, blank = True)
    review              = models.TextField(blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.driver.fullname  + ". User : " + self.user.username

class BookDriver(models.Model): 
    fullname            = models.CharField(max_length=200,blank = True, null= True)
    email               = models.TextField(blank = True, null= True)
    persons             = models.IntegerField(default=0)
    duration            = models.IntegerField(default=0)
    Departure_date      = models.DateTimeField(blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname
    


# # # # contact model # # # # #
class CarCharge(models.Model):
    carname             = models.CharField(max_length=200,blank = True, null= True)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    persons             = models.TextField(blank = True, null= True)
    price               = models.TextField(blank = True, null= True)
    perKM               = models.TextField(blank = True, null= True)
    available           = models.BooleanField(default=False)
    created_at          = models.DateTimeField(auto_now=True)
    updated_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.carname 



# # # # contact model # # # # #
class Contact(models.Model):
    fullname            = models.CharField(max_length=200,blank = True, null= True)
    subject             = models.CharField(max_length=200,blank = True, null= True)
    message             = models.TextField(blank = True, null= True)
    email               = models.TextField(blank = True, null= True)
    created_at          = models.DateTimeField(auto_now=True)
    updated_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email 
    

class Review(models.Model):
    package             = models.ForeignKey(Package, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    driverSelect        = models.ForeignKey(Driver, on_delete=models.SET_NULL, null= True)
    facilities          = models.IntegerField(blank = True,null=True)
    comfort             = models.IntegerField(blank = True,null=True)
    experience          = models.IntegerField(blank = True,null=True)
    location            = models.IntegerField(blank = True,null=True)
    driver              = models.IntegerField(blank = True,null=True)
    title               = models.CharField(max_length=250, blank = True)
    review              = models.TextField(blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def images(self):
        images = ReviewGallery.objects.filter(review=self)
        return images
    
    def userImage(self):
        profile = UserProfile.objects.get(user = self.user)
        return profile.image


    def __str__(self):
        return self.package.title  + ". User : " + self.user.username


class ReviewGallery(models.Model): 
    review              = models.ForeignKey(Review, on_delete=models.CASCADE)
    image               = models.ImageField(upload_to='static/images', blank = True, null= True)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.review.title
    
    class Meta:
        verbose_name= 'ReviewGallery'
        verbose_name_plural = 'ReviewGalleries'


class Order(models.Model):
    package             = models.ForeignKey(Package, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname            = models.CharField(max_length=200,blank = True, null= True)
    email               = models.TextField(blank = True, null= True)
    address             = models.TextField(blank = True, null= True)
    Departure_date      = models.DateTimeField(blank = True, null= True)
    persons             = models.IntegerField(default=0)
    total               = models.IntegerField(default=0)
    started             = models.BooleanField(default=False)
    completed           = models.BooleanField(default=False)
    created_date        = models.DateTimeField(auto_now_add=True)
    updated_date        = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.package.title  + ". User : " + self.user.username
