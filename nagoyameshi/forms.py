from django import forms

# models.py の Review をimportする。
from .models import Review,Favorite,Reservation


# フォームクラス(バリデーションルール)を作る
# Reviewのバリデーションルールを作る。
class ReviewForm(forms.ModelForm):

    class Meta:
        # Reviewモデルのデータをバリデーションする。
        model = Review
        # Reviewモデルの何をバリデーションするか？ 
        # (DB書き込み時、自動的に値が入る created_at と updated_at 以外のすべてのフィールドを指定する。)
        fields = [ "restaurant","user","content" ]


# Favoriteのバリデーションルールを作る。
class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = [ "restaurant","user" ]


# Reservationのバリデーションルールを作る。
# ModelFormを継承することで、モデルの制約を元にバリデーションルールを作ることができる。
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [ "restaurant","user","datetime","headcount" ]
    