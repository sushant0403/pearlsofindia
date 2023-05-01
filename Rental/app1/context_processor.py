from .models import *

def menu_links(request):
    user = request.user
    user_image = None
    try:
        if user.is_authenticated :
            userprofile = UserProfile.objects.get(user = user)
            if userprofile.image :
                user_image = userprofile.image
    except:
        user_image = None

    return dict( user_image = user_image )