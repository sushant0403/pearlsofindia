from django.shortcuts import render, redirect
from django.db.models import Q
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# mail verification import
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode ,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail, send_mass_mail

from datetime import date

# # Create your views here.

def index_view(request):
    try:
        top_packages = []
        count = 0
        packages    = Package.objects.all()
        try:
            for package in packages:
                if count <3 and package.averagereview() >=4 :
                    top_packages.append(package)
                    count +=1
        except:
            if top_packages == []:
                top_packages    = Package.objects.all().order_by('-id')[:3]

        banners         = Banner.objects.all().order_by('-id')[0:3]
        feedback        = Feedback.objects.all().order_by('-id')[0:1]
        drivers         = Driver.objects.all().order_by('-id')[0:4]
    except:
        top_packages    = Package.objects.all().order_by('-id')[:3]
        banners         = Banner.objects.all().order_by('-id')[0]
        feedback        = Feedback.objects.all().order_by('-id')[0]
        drivers         = Driver.objects.all().order_by('-id')[0]

    gallery_images  = Gallery.objects.all()
    
    
    context ={
        'top_packages'  :top_packages,
        'banners'       :banners,
        'feedback'      :feedback,
        'gallery_images':gallery_images,
        'drivers'       :drivers,
    }

    return render(request, 'app1/index.html',context)

def packages_view(request):

    packages        = Package.objects.all()
    paginator       = Paginator(packages,15)
    page            = request.GET.get("page")
    paged_packages  = paginator.get_page(page)

    context={
        'packages':paged_packages
    }

    return render(request, 'app1/packages.html', context)
    
# def Package_view(request):

#     return render(request, 'app1/productdetail.html')


def packageDetail_view(request, pk ):
    package     = Package.objects.get( id = pk )
    reviews     = Review.objects.filter( package = package )
    paginator       = Paginator(reviews,3)
    page            = request.GET.get("page")
    paged_packages  = paginator.get_page(page)
    drivers     = Driver.objects.all()
    events     = PackageEvent.objects.filter( package = package )
    photos     = PackageGallery.objects.filter( package = package )

    print(reviews)

    context = {
        'package' : package,
        'reviews' : paged_packages,
        'events'  : events,
        'photos'  : photos,
        'drivers'  : drivers,
    }
    return render(request, 'app1/packageDetail.html', context)


def search_view(request):
    packages        = None
    package_count   = 0
    if 'keyword' in request.GET:
        keyword     = request.GET["keyword"]
        if keyword:
            packages    = Package.objects.order_by('-created_at').filter( Q(description__icontains=keyword) | Q(title__icontains=keyword))
        package_count   = packages.count()
    context = {
        "packages"      :   packages,
        "package_count" :   package_count
    }
    return render(request, 'app1/search.html', context)


def drivers_view(request):
    drivers     = Driver.objects.all()
    carcharges  = CarCharge.objects.all()
    context = {
        'drivers' : drivers,
        'carcharges' : carcharges
    }
    return render(request, 'app1/driverPage.html', context)

def gallery_view(request):
    photos          = Gallery.objects.all()
    paginator       = Paginator(photos,21)
    page            = request.GET.get("page")
    paged_packages  = paginator.get_page(page)

    context = {
        'photos' : paged_packages,
    }
    return render(request, 'app1/galleryPage.html', context)




# # # # # # # # # Review add, delete, edit # # # # # # # # # # 
def review_add_view(  request, pk ):
    review1     = None
    package     = Package.objects.get( id = pk )
    user        = request.user
    user_review = Review.objects.filter(package = package, user= user)
    completed   = Order.objects.filter(package = package, user= user, started = True, completed = True)
    if user_review:
        messages.error(request, f"sorry ! only one review available!")
    elif ( len(completed) > 0 ):
        if request.method == 'POST':

            subject         = request.POST['subject']
            facilities      = request.POST['facilities']
            comfort         = request.POST['comfort']
            experiences     = request.POST['experiences']
            location        = request.POST['locations']
            review          = request.POST['review']
            driverSelect    = request.POST['driverSelect']
            DRating         = request.POST['DRating']
            
            driverSelect =  Driver.objects.get(id=int(driverSelect))
            # if request.FILES['images'] :
            #     images           = request.FILES.getlist('images')
            try:
                images           = request.FILES.getlist('images')
            except :
                images = None

            review1     = Review.objects.create(
                package         = package, 
                user            = user, 
                driverSelect    = driverSelect, 
                title           = subject, 
                facilities      = int(facilities),
                comfort         = int(comfort),
                experience      = int(experiences),
                location        = int(location),
                driver          = int(DRating),
                review          = review
            )
            review1.save()
            if driverSelect.no_rating:
                driverSelect.rating = (driverSelect.no_rating * driverSelect.rating + int(DRating)) / (driverSelect.no_rating + 1)  
                driverSelect.no_rating += 1
            else : 
                driverSelect.rating = int(DRating)
                driverSelect.no_rating = 1
            driverSelect.save()
            if images:
                for image in images:
                    reviewGallery = ReviewGallery.objects.create(
                        review = review1,
                    )
                    reviewGallery.image = image
                    reviewGallery.save()


        messages.success(request, f"review added successfully")

    else:
        messages.error(request, f"sorry ! You haven't completed the package yet!")

    return redirect('packageDetail_view', pk = pk ) 


def review_delete_view( request, pk, id ):

    review      = Review.objects.get( id = id )
    if request.user == review.user or request.user.is_staff:
        review.delete()
        messages.success(request, f"Review deleted successfully")

    else:
        messages.error(request, f"Only the reviewed user allowed")
    return redirect('Package_view' , pk = pk )


# # # # # # # # # # User login, logout, register # # # # # # # # # # 

def login_view(request):

    user = None 
    if request.method == 'POST':
        name    = request.POST['name']
        password    = request.POST['password']
        if "@" in name:
            user        = authenticate(email=name, password=password)
        else:
            user        = authenticate(username=name, password=password)

        if user :
            if user.is_authenticated :
                login(request, user)
                messages.success(request, f"Login Successful ! You are now logged in as {user.username}.")
                return redirect('/')
        else :
            messages.error(request, "Login failed ! username and password do not match.")

    return render(request, 'app1/loginPage.html')


def register_view(request):
    user = None
    if request.method == 'POST':
        firstname       = request.POST['firstname']
        lastname        = request.POST['lastname']
        email           = request.POST['email'] 
        username        = email.split("@")[0]
        password        = request.POST['password']
        confirmpassword = request.POST['confirmpassword']

        if password != confirmpassword and len(password) < 8 :
            messages.error(request, "password too short  or do not match.")

        else :
            try:
                user    = User.objects.create_user(
                    username    = username, 
                    email       = email, 
                    password    = password
                )
                user.first_name = firstname
                user.last_name  = lastname
                user.is_active  = False
                user.save()

                 # verification email

                current_site  = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('app1/includes/account_verification_email.html',{
                    'user':user,
                    'domain':current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                print(3)
                send_mail(
                    mail_subject, 
                    message, 
                    'thakurisushant0403@gmail.com',
                    [email], 
                    fail_silently=False,
                    )
                print(5)
                messages.success(request, "Registered successfully!")
                return redirect('/login/')
            
            except:
                messages.error(request, "email already exists try another.") 

    return render(request, 'app1/registerPage.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Log Out Successfull ! You are now logged out.")
    return index_view(request)

@login_required(login_url="login_view")
def profile_view(request):
    user = request.user
    if  user == User.objects.get(id=user.id) or user.is_staff == True :
        try:
            userprofile = UserProfile.objects.get(user = user)
        except:
            userprofile = None
        context={
            'userprofile':userprofile,
        }
        return render(request, 'app1/profilePage.html',context)
    else:
        messages.error(request, "sorry! cannot view other peoples profile.")
        return redirect('index_view')



@login_required(login_url="login_view")
def create_profile_view(request):
    user = request.user
    userprofile = None
    if request.method == 'POST':
        firstname       = request.POST['firstname']
        lastname        = request.POST['lastname']
        phone           = request.POST['phone']
        gender          = request.POST['gender']
        address         = request.POST['address']
        country         = request.POST['country']
        # if request.FILES['image'] :
        #     image           = request.FILES['image']
        try:
            image           = request.FILES['image']
        except:
            image = None

        user.first_name = firstname
        user.last_name = lastname
        user.save()
        userprofile = UserProfile.objects.create(
            user   = user, 
            gender = gender, 
            phone = phone, 
            address = address
            )
        if image :
            userprofile.image = image
        userprofile.country = country 
        userprofile.save()
        messages.success(request, "Profile Created Successfully")
        return redirect('profile_view')

    return render(request, 'app1/createProfilePage.html')

@login_required(login_url="login_view")
def edit_profile_view(request):
    user = request.user
    userprofile = UserProfile.objects.get(user = user)
    if request.method == 'POST':
        firstname       = request.POST['firstname']
        lastname        = request.POST['lastname']
        phone           = request.POST['phone']
        gender          = request.POST['gender']
        address         = request.POST['address']
        country         = request.POST['country']
        # if request.FILES['image'] :
        #     image           = request.FILES['image']

        try:
            image           = request.FILES['image']
        except:
            image = None
        # print(image)

        user.first_name = firstname
        user.last_name = lastname
        user.save()
        if image:
            userprofile.image = image
        userprofile.gender = gender
        userprofile.phone = phone
        userprofile.address = address
        userprofile.country = country 
        userprofile.save()
        messages.success(request, "Profile Edited Successfully")
        return redirect('profile_view')

    context={
        'userprofile' : userprofile,
    }
    return render(request, 'app1/editProfilePage.html',context)


def activate(request, uidb64, token):
    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        user.is_active  = True
        user.save()
        messages.success(request,'Congratulations your account is activated.')
        return redirect('login_view')

    else:

        messages.error(request,'Invalid activation link')
        return redirect('register_view')



def forgotpassword_view(request):

    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__iexact=email)

            # forgot password email
            current_site  = get_current_site(request)
            mail_subject = 'Reset password using the given link below:'
            message = render_to_string('app1/includes/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail(
                mail_subject, 
                message, 
                'thakurisushant0403@gmail.com',
                [to_email], 
                fail_silently=False,
                )
            messages.success(request,'Password reset link send to your email. Please check your email.')
            return redirect('login_view')
        
        else:
            messages.error(request,'The given email doesnot exists.')
            return redirect('forgotpassword_view')
    
    return render(request,"app1/forgotPasswordPage.html")


def resetpassword_validation_view(request, uidb64, token):

    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']  =   uid
        messages.success(request,"please reset your password.")
        return redirect('resetpassword_view')

    else:
        messages.error(request,"Invalid link.")
        return redirect('login_view')



def resetpassword_view(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password :
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful.")
            return redirect('login_view')
        
        else:
            messages.error(request,"passwords don't match")
    
    return render(request,'app1/resetPasswordPage.html')

@login_required(login_url="login_view")
def change_password_view(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,"Password updated sucessfully.")
                return redirect('profile_view')

            else:
                messages.error(request,"Please enter valid current password")
                return redirect('change_password_view')

        else:
            messages.error(request, "Password does not match")
            return redirect('change_password_view')
    
    return render(request, "app1/changePasswordPage.html")



def book_driver_view(request):
    book = None
    if request.method == 'POST':
        fullname        = request.POST['fullname']
        email           = request.POST['email'] 
        persons         = request.POST['persons'] 
        duration        = request.POST['duration'] 
        Departure_date  = request.POST['departure_date'] 
        
        today = date.today()
        
        if str(today) < Departure_date :

            book    = BookDriver.objects.create(
                fullname    = fullname, 
                email       = email, 
                persons    = persons,
                duration    = duration,
                Departure_date    = Departure_date
            )
            book.save()

            # email to the customer
            mail_subject = 'Your driver booked successfully'
            message = (f'Thank you for booking Your booking is confirmed.\n\tName: {fullname},\n\tEmail: {email},\n\tPersons: {persons},\n\tDuration: {duration},\n\tDeparture date: {Departure_date}')


            # email to yourself
            mail_subject1 = 'Your received a booking from your website pearls of india'
            message1 = f"\nDriver has been booked by :\n\tName: {fullname},\n\tEmail: {email},\n\tPersons: {persons},\n\tDuration: {duration},\n\tDeparture date: {Departure_date}"


            email1 = (mail_subject, message, 'thakurisushant0403@gmail.com', [email])
            email2 = (mail_subject1, message1, 'thakurisushant0403@gmail.com', ['thakurisushant0403@gmail.com'])
            send_mass_mail((email1, email2), fail_silently=False)
            
            messages.success(request,"Driver booked sucessfully. we have send you a confirmation email")
        else:
            messages.error(request,"Driver booking failed. you entered old date.")


    return redirect('index_view')


def driver_review_add_view(  request, pk ):
    review1     = None
    driver     = Driver.objects.get( id = pk )
    user        = request.user
    user_review = DriverReview.objects.filter(driver = driver, user= user)
    if user_review:
        messages.error(request, f"sorry ! only one review available!")
    else:
        if request.method == 'POST':

            subject         = request.POST['subject']
            rating          = request.POST['rating']
            review          = request.POST['review']

            review1     = Review.objects.create(
                driver          = driver, 
                user            = user, 
                title           = subject,
                rating          = int(rating),
                review          = review
            )
            review1.save()


        messages.success(request, f"review added successfully")
    return redirect('packageDetail_view', pk = pk ) 


def driver_review_delete_view( request, pk, id ):

    review      = DriverReview.objects.get( id = id )
    if request.user == review.user or request.user.is_staff:
        review.delete()
        messages.success(request, f"Review deleted successfully")

    else:
        messages.error(request, f"Only the reviewed user allowed")
    return redirect('Package_view' , pk = pk )


# # # # # Order views # # # # #

def order_view(request):
    user = request.user
    orders       = Order.objects.filter(user=user)

    context = {
        'orders' : orders
    }
    return render(request, 'app1/ordersPage.html',context)

def orderDetail_view(request, id):
    user = request.user
    order       = Order.objects.get(id=id)

    context = {
        'order' : order
    }
    return render(request, 'app1/orderDetailPage.html',context)

def book_package_view(request, id):
    order = None
    user = request.user
    package = Package.objects.get(id=id)
    if request.method == 'POST':
        fullname        = request.POST['fullname']
        email           = request.POST['email'] 
        address         = request.POST['address'] 
        persons         = int(request.POST['persons']) 
        Departure_date  = request.POST['departure_date'] 

        total  = persons * package.price
        today = date.today()
        
        if str(today) < Departure_date :

            order    = Order.objects.create(
                user               = user, 
                package            = package, 
                fullname           = fullname, 
                email              = email,
                address            = address,
                persons            = persons,
                total              = total,
                Departure_date     = Departure_date
            )
            order.save()

            # email to the customer
            mail_subject = 'Your package booked successfully'
            message = (f'Thank you for booking. Your booking is confirmed.\n\tName: {fullname},\n\tEmail: {email},\n\tPersons: {persons},\n\taddress: {address},\n\ttotal: {total},\n\tDeparture date: {Departure_date}')


            # email to yourself
            mail_subject1 = 'Your received a booking from your website pearls of india'
            message1 = f"\nPackage has been booked by :\n\tName: {fullname},\n\tEmail: {email},\n\tPersons: {persons},\n\taddress: {address},\n\ttotal: {total},\n\tDeparture date: {Departure_date}"


            email1 = (mail_subject, message, 'thakurisushant0403@gmail.com', [email])
            email2 = (mail_subject1, message1, 'thakurisushant0403@gmail.com', ['thakurisushant0403@gmail.com'])
            send_mass_mail((email1, email2), fail_silently=False)
            
            messages.success(request,"package booked sucessfully. we have send you a confirmation email")
        else:
            messages.error(request,"package booking failed. you entered old date or email is not valid.")
    else:
        context = {
            "package_id" : id
        }
        return render(request, 'app1/packagebooking_page.html',context)

    return redirect('order_view')
    

# # # # # Feedback views # # # # #

def feedback_view(request):
    feedbacks       = Feedback.objects.all()
    paginator       = Paginator(feedbacks,3)
    page            = request.GET.get("page")
    paged_packages  = paginator.get_page(page)

    context = {
        'feedbacks' : paged_packages
    }
    return render(request, 'app1/feedbackPage.html',context)


# # # # # about Us views # # # # #

def about_view(request):
    return render(request, 'app1/about.html')


# # # # # Contact Us views # # # # #
def contactUs_view(request):
    return render(request, 'app1/contactUs.html')


def contact_view(request):
    contact = None
    try:
        if request.method == 'POST':
            fullname        = request.POST['fullname']
            email           = request.POST['email'] 
            subject         = request.POST['subject'] 
            message        = request.POST['message'] 
        

            contact    = Contact.objects.create(
                fullname    = fullname, 
                email       = email, 
                subject    = subject,
                message    = message,
            )
            contact.save()

            # email to the customer
            mail_subject = 'You contacted Pearls Of India successfully'
            message = (f'Thank you, We will get in touch within 2 working days. \nPlease check your information:\n\tName: {fullname},\n\tEmail: {email},\n\tSubject: {subject},\n\tMessage: {message}')


            # email to yourself
            mail_subject1 = 'Your received a message from your website pearls of india'
            message1 = f"\nContacted information :\n\tName: {fullname},\n\tEmail: {email},\n\tSubject: {subject},\n\tMessage: {message}"


            email1 = (mail_subject, message, 'thakurisushant0403@gmail.com', [email])
            email2 = (mail_subject1, message1, 'thakurisushant0403@gmail.com', ['thakurisushant0403@gmail.com'])
            send_mass_mail((email1, email2), fail_silently=False)
            
            messages.success(request,"You contacted Pearls Of India successfully. we have send you a confirmation email")
    except:
        messages.success(request,"Contacting error please check your email correctly and try again")


    return redirect('contactUs_view')