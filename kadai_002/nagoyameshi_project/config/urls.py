"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from nagoyameshi.views import TopView,RestaurantView,ReviewView,FavoriteView,ReservationView,MypageView,SuccessView,CheckoutView,PremiumView,PortalView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",TopView.as_view(), name="top"),
    path("restaurant/<int:pk>/",RestaurantView.as_view(), name="restaurant"),
    path("review/<int:pk>/",ReviewView.as_view(), name="review"),
    path("favorite/<int:pk>/",FavoriteView.as_view(), name="favorite"),
    path("reservation/<int:pk>/", ReservationView.as_view(), name="reservation"),
    
    path("mypage/", MypageView.as_view(), name="mypage"),

    path("success/", SuccessView.as_view(), name="success"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("premium/", PremiumView.as_view(), name="premium"),
    path("portal/", PortalView.as_view(), name="portal"),




    path('accounts/', include('allauth.urls')),
]
