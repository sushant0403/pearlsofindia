from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index_view'),
    path('search/', views.search_view, name='search_view'),
    path('packages/', views.packages_view, name='packages_view'),
    path('packageDetail/<int:pk>/', views.packageDetail_view, name='packageDetail_view'),

    path('review/<int:pk>/', views.review_add_view, name='review_add_view'),
    path('reviewDelete/<int:pk>/<int:id>/', views.review_delete_view, name='review_delete_view'),

    path('login/', views.login_view, name='login_view'),
    path('register/', views.register_view, name='register_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.profile_view, name='profile_view'),
    path('editprofile/', views.edit_profile_view, name='edit_profile_view'),
    path('createprofile/', views.create_profile_view, name='create_profile_view'),
    path("activate/<uidb64>/<token>/", views.activate, name = "activate"),

    path('book/', views.book_driver_view, name='book_driver_view'),
    path('drivers/', views.drivers_view, name='drivers_view'),
    path('gallery/', views.gallery_view, name='gallery_view'),

    path('feedbacks/', views.feedback_view, name='feedback_view'),

    path('orders/', views.order_view, name='order_view'),
    path('order/<int:id>/', views.orderDetail_view, name='orderDetail_view'),
    path('bookPackage/<int:id>/', views.book_package_view, name='book_package_view'),

    path('about/', views.about_view, name='about_view'),

    path('contact/', views.contact_view, name='contact_view'),
    path('contactUs/', views.contactUs_view, name='contactUs_view'),

    path("forgotpassword/", views.forgotpassword_view, name = "forgotpassword_view"),
    path("resetpassword_validation/<uidb64>/<token>/", views.resetpassword_validation_view, name = "resetpassword_validation_view"),
    path("resetpassword/", views.resetpassword_view, name = "resetpassword_view"),
    path("changepassword/", views.change_password_view, name = "change_password_view"),
]
