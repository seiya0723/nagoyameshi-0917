from django.shortcuts import render,redirect
from django.views import View
from .models import Restaurant,Category,Review,Favorite,Reservation,PremiumUser
from .forms import ReviewForm,FavoriteForm,ReservationForm
from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from django.urls import reverse_lazy
import stripe

stripe.api_key  = settings.STRIPE_API_KEY

class TopView(View):
    def get(self,request):
        query = Q()

        if"search" in request.GET:
           print(request.GET["search"])


           words = request.GET["search"].replace("　"," ").split(" ")
           print(words)


           for word in words:
               query &= Q(name__icontains=word)


        if "category" in request.GET:
            print( request.GET["category"] )       
            if "" != request.GET["category"]:
                query &= Q(category=request.GET["category"])


        restaurants = Restaurant.objects.filter(query)

        categories = Category.objects.all()

        context={
            "restaurants":restaurants,
            "greet":"こんにちは",
            "price":1000,
            "categories":categories
        }

        return render(request,"top.html",context)



class RestaurantView(LoginRequiredMixin,View):
    def get(self,request,pk):
        
        print(pk)

        context = {}

        context["restaurant"] = Restaurant.objects.filter(id=pk).first()

        context["reviews"] = Review.objects.filter(restaurant=pk)

        return render(request, "restaurant.html",context)


class ReviewView(LoginRequiredMixin, View):
    def post(self,request,pk):

        print(pk, "に対してレビュー")

        restaurant = Restaurant.objects.filter(id=pk).first()
        request.user
        request.POST["content"]        

        """
        review = Review(restaurant=restaurant, user=request.user, content=request.POST["content"])
        review.save()   
        """
        
        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant

        ReviewForm(copied)    

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print(form.errors)

        return redirect("top")


class FavoriteView(LoginRequiredMixin,View):
    def post(self, request,pk):
        restaurant = Restaurant.objects.filter(id=pk).first()

        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant

        form = FavoriteForm(copied)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print(form.errors)

        return redirect("top")


class ReservationView(LoginRequiredMixin,View):
    def post(self, request,pk):

        restaurant = Restaurant.objects.filter(id=pk).first()   
        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant


        form = ReservationForm(copied)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            print(form.errors)

        return redirect("top")



class MypageView(LoginRequiredMixin,View):
    def get(self, request):

        context = {}

        context["favorites"] = Favorite.objects.filter(user=request.user)
        context["reviews"] = Review.objects.filter(user=request.user)
        context["reservations"] = Reservation.objects.filter(user=request.user)

        return render(request, "mypage.html", context)


class CheckoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):

        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='subscription',

        
            success_url=request.build_absolute_uri(reverse_lazy("success")) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse_lazy("mypage")),
        )

        
        print( checkout_session["id"] )

        return redirect(checkout_session.url)


class SuccessView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        print("有料会員登録しました！")


        if "session_id" not in request.GET:
            print("セッションIDがありません。")
            return redirect("mypage")


        try:
            checkout_session_id = request.GET['session_id']
            checkout_session    = stripe.checkout.Session.retrieve(checkout_session_id)
        except:
            print( "このセッションIDは無効です。")
            return redirect("mypage")

        print(checkout_session)

        if checkout_session["payment_status"] != "paid":
            print("未払い")
            return redirect("mypage")

        print("支払い済み")

        premium_user = PremiumUser()
        premium_user.user = request.user
        premium_user.premium_code = checkout_session["customer"]
        premium_user.save()


        return redirect("mypage")


# 有料会員の設定
class PortalView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        # userフィールドが自分(request.user)の有料会員情報(PremiumUser)を取り出す
        premium_user = PremiumUser.objects.filter(user=request.user).first()

        if not premium_user:
            print( "有料会員登録されていません")
            return redirect("mypage")

        # ユーザーモデルに記録しているカスタマーIDを使って、ポータルサイトへリダイレクト
        portalSession   = stripe.billing_portal.Session.create(
            customer    = premium_user.premium_code,
            return_url  = request.build_absolute_uri(reverse_lazy("mypage")),
        )

        return redirect(portalSession.url)



class PremiumView(View):
    def get(self, request, *args, **kwargs):
        
        premium_user = PremiumUser.objects.filter(user=request.user).first()


        if not premium_user:
            print("カスタマーIDがセットされていません。")
            return redirect("mypage")

        try:
            subscriptions = stripe.Subscription.list(customer=premium_user.premium_code)
        except:
            print("このカスタマーIDは無効です。")
            premium_user.delete()

            return redirect("mypage")


        is_premium = False

        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")
                is_premium = True

        if is_premium:
            print("有料会員です")
        else:
            print("有料会員ではない")

        return redirect("mypage")


