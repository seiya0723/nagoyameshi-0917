from django.shortcuts import render,redirect
from django.views import View

from .models import Restaurant,Category,Review,Favorite,Reservation,PremiumUser
# forms.pyから ReviewFormをimportするには
from .forms import ReviewForm,FavoriteForm,ReservationForm


from django.db.models import Q

# ビューに多重継承することで、ビュー実行時、ログインをしていなければログインページにリダイレクトされる。
from django.contrib.auth.mixins import LoginRequiredMixin



# stripeに必要なものをimportする
from django.conf import settings
from django.urls import reverse_lazy
import stripe

# stripeAPIキーをセットする。
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



# 未ログインユーザーは、店舗の詳細ページは見せない。
class RestaurantView(LoginRequiredMixin, View):
    def get(self,request,pk):
        
        print(pk)

        context = {}
        context["restaurant"] = Restaurant.objects.filter(id=pk).first()

        # TODO:投稿されたレビューを表示する。Reviewのデータを取り出す
        context["reviews"] = Review.objects.filter(restaurant=pk)

        return render(request, "restaurant.html",context)

# 未ログインユーザーはアクセスできないようにしたい。
# LoginRequiredMixinを多重継承する。
class ReviewView(LoginRequiredMixin, View):
    def post(self,request,pk):
        
        
        # pk のRestaurantに対してレビューを送信する。
        print(pk, "に対してレビュー")
        restaurant = Restaurant.objects.filter(id=pk).first()
        request.user
        request.POST["content"]
        
        # Reviewモデルを使って保存する。(バリデーションされていないのでここはコメントアウトする) 
        """
        review = Review(restaurant=restaurant, user=request.user, content=request.POST["content"])
        review.save()
        """

        # ReviewForm(バリデーションしてほしいデータ(辞書型))
        # userとrestaurantのデータを追加する。
        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant

        form = ReviewForm(copied)

        # .is_valid() でルールに則っているか(True)、いない(False)のか判定できる。
        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            # エラーの理由
            print(form.errors)


        return redirect("top")

# お気に入りの登録をするビュー( ログイン必須、Viewを継承 )
class FavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # お気に入りしたい店舗の特定。
        restaurant = Restaurant.objects.filter(id=pk).first()

        # TODO: ここでお気に入り登録をする
        # FavoriteForm を使い バリデーションし、保存する
        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant

        form = FavoriteForm(copied)

        # .is_valid() でルールに則っているか(True)、いない(False)のか判定できる。
        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            # エラーの理由
            print(form.errors)        

        return redirect("top")


# 予約を受け付けるビュー(要ログイン) 
class ReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        #                   ↑ 予約したい Restaurant の id

        #========↓お気に入りとレビューにも追加する=====================================
       
        # userフィールドが自分(request.user)の有料会員情報(PremiumUser)を取り出す。
        premium_user = PremiumUser.objects.filter(user=request.user).first()

        if not premium_user:
            print("カスタマーIDがセットされていません。")
            return redirect("mypage")

        # カスタマーIDを元にStripeに問い合わせ
        try:
            subscriptions = stripe.Subscription.list(customer=premium_user.premium_code)
        except:
            print("このカスタマーIDは無効です。")
            premium_user.delete()

            return redirect("mypage")

        is_premium = False

        # ステータスがアクティブであるかチェック。
        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")
                is_premium = True

        if is_premium:
            print("有料会員です")
        else:
            print("有料会員ではない")
            return redirect("mypage")

        #=============================================



        # 予約したい店舗とユーザーを特定、送られてきたデータに追加をする。
        restaurant = Restaurant.objects.filter(id=pk).first()
        copied = request.POST.copy()
        copied["user"] = request.user
        copied["restaurant"] = restaurant


        # TODO:予約したい店舗を特定、バリデーション(forms.pyでReservationのバリデーションルールを作る、importして↓で使う) 
        form = ReservationForm(copied)

        # .is_valid() でルールに則っているか(True)、いない(False)のか判定できる。
        if form.is_valid():
            print("バリデーションOK")
            form.save()
        else:
            # エラーの理由
            print(form.errors)


        return redirect("top")



# マイページの表示をするビュー
class MypageView(LoginRequiredMixin, View):
    def get(self, request):
        #          ↑ この中にアクセスした自分自身のユーザー情報が含まれている。request.user
        context = {}
        # アクセスした人がお気に入り登録した店舗を取り出す
        context["favorites"] = Favorite.objects.filter(user=request.user)
        # Favorite のデータの中から、お気に入り登録した人 = アクセスした人 のデータを取り出す。

        # Review のデータの中から、レビュー投稿者 = アクセスした人 のデータを取り出す。
        context["reviews"] = Review.objects.filter(user=request.user)

        # Reservation のデータの中から、予約者 = アクセスした人 のデータを取り出す。
        context["reservations"] = Reservation.objects.filter(user=request.user)

        # 有料会員登録をしているかどうか？
       

        context["is_premium"] = False

        # userフィールドが自分(request.user)の有料会員情報(PremiumUser)を取り出す。
        premium_user = PremiumUser.objects.filter(user=request.user).first()

        if not premium_user:
            print("カスタマーIDがセットされていません。")
            return render(request, "mypage.html", context)
            

        # カスタマーIDを元にStripeに問い合わせ
        try:
            subscriptions = stripe.Subscription.list(customer=premium_user.premium_code)
        except:
            print("このカスタマーIDは無効です。")
            premium_user.delete()
            return render(request, "mypage.html", context)

        # ステータスがアクティブであるかチェック。
        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")
                context["is_premium"] = True

        if context["is_premium"]:
            print("有料会員です")
        else:
            print("有料会員ではない")


      
        return render(request, "mypage.html", context)



# StripeのAPIキーを使ってセッションを作る。
class CheckoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):

        # セッションを作る
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='subscription',

            # リダイレクト先のURL
            success_url=request.build_absolute_uri(reverse_lazy("success")) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse_lazy("mypage")),
        )

        # セッションid
        print( checkout_session["id"] )

        return redirect(checkout_session.url)


# サブスクリプションを本当に決済したかをチェックする。
class SuccessView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        print("有料会員登録しました！")
        
        # パラメータにセッションIDがあるかチェック
        if "session_id" not in request.GET:
            print("セッションIDがありません。")
            return redirect("mypage")


        # そのセッションIDは有効であるかチェック。
        try:
            checkout_session_id = request.GET['session_id']
            checkout_session    = stripe.checkout.Session.retrieve(checkout_session_id)
        except:
            print( "このセッションIDは無効です。")
            return redirect("mypage")

        print(checkout_session)

        # statusをチェックする。未払であれば拒否する。(未払いのsession_idを入れられたときの対策)
        if checkout_session["payment_status"] != "paid":
            print("未払い")
            return redirect("mypage")

        print("支払い済み")

        #TODO: カスタマーidを記録する。
        # PremiumUser の premium_codeフィールドへ、カスタマーidを記録する。
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
        
        # userフィールドが自分(request.user)の有料会員情報(PremiumUser)を取り出す。
        premium_user = PremiumUser.objects.filter(user=request.user).first()

        # idが1のデータを取り出す
        #PremiumUser.objects.filter(id=1)



        if not premium_user:
            print("カスタマーIDがセットされていません。")
            return redirect("mypage")

        # カスタマーIDを元にStripeに問い合わせ
        try:
            subscriptions = stripe.Subscription.list(customer=premium_user.premium_code)
        except:
            print("このカスタマーIDは無効です。")
            premium_user.delete()

            return redirect("mypage")


        is_premium = False

        # ステータスがアクティブであるかチェック。
        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")
                is_premium = True

        if is_premium:
            print("有料会員です")
        else:
            print("有料会員ではない")

        return redirect("mypage")


