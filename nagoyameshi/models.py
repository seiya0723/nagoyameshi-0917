from django.db import models

# Create your models here.
# models.py → admin.py → views.py → urls.py → templates 

# Djangoの中にあるデフォルトのユーザーモデル。
# python manage.py createsuperuser このコマンドでUserモデルにデータが追加される。
from django.contrib.auth import get_user_model
User = get_user_model()
# これがER図の会員の部分になる。

from django.utils import timezone

# 下記 要件定義書を参考
# https://drive.google.com/file/d/1hsKfW7BnokHGAMlxbWPmk-uYg-dqeduu/view
# 実装必須: ↑お気に入りが無い



# カテゴリ
class Category(models.Model):

    name        = models.CharField(verbose_name="名前", max_length=15)
    created_at  = models.DateTimeField(verbose_name="作成日時", default=timezone.now)
    updated_at  = models.DateTimeField(verbose_name="更新日時", auto_now=True)

    def __str__(self):
        return self.name

# 店舗
class Restaurant(models.Model):

    category        = models.ForeignKey(Category, verbose_name="カテゴリ", on_delete=models.CASCADE)

    name            = models.CharField(verbose_name="名前", max_length=50)
    # ImageField で画像の保存ができる。(アップロード先のパスを指定。)
    image           = models.ImageField(verbose_name="画像", upload_to="nagoyameshi/restaurant/image/")
    # DBに保存されるのは、画像ではなく、画像の保存先のパス(文字列)
    # 画像本体はプロジェクトディレクトリのmediaディレクトリに保存する。(settings.pyで設定)

    description     = models.CharField(verbose_name="店舗説明", max_length=500)

    # 時刻だけを入力するフィールド 10:00 ~ 22:00 の場合、 start_at に10:00　、 end_at に 22:00 
    start_at        = models.TimeField(verbose_name="営業開始時間",default=timezone.now)
    end_at          = models.TimeField(verbose_name="営業終了時間",default=timezone.now)
    
    cost            = models.PositiveIntegerField(verbose_name="価格帯")



    # 111-1111 などとハイフンを含める場合、文字列型で8文字までとする。
    post_code       = models.CharField(verbose_name="郵便番号", max_length=8)

    # 住所は文字列型。
    address         = models.CharField(verbose_name="住所", max_length=100)


    # 電話番号は0から始まるので、数値型ではなく文字列型で。
    # 携帯電話番号であれば11桁、固定回線の場合は10桁 混乱を招くためハイフンを除外する。
    tel             = models.CharField(verbose_name="電話番号", max_length=11)


    # 計算をしないのであれば、数値ではなく文字列で。


    # 定休日は必須には含まれず、多対多を知る必要があるため、一旦除外
    #holiday         = models.ManyToManyField(Holiday, verbose_name="定休日")
    # 店舗Aは、火曜と木曜が休み
    # 店舗Bは、火曜と土曜が休み
    # 店舗Cは、月曜と土曜と日曜が休み
    # 店舗ごとに曜日を複数指定する。
    # https://noauto-nolife.com/post/django-many-to-many/

    created_at      = models.DateTimeField(verbose_name="投稿日時", default=timezone.now)
    updated_at      = models.DateTimeField(verbose_name="更新日時", auto_now=True)


# 星のレビュー
# https://noauto-nolife.com/post/django-star-review/
#from django.core.validators import MinValueValidator,MaxValueValidator

#MAX_STAR      = 5
class Review(models.Model):

    restaurant  = models.ForeignKey(Restaurant, verbose_name="店舗", on_delete=models.CASCADE)
    user        = models.ForeignKey(User, verbose_name="投稿者", on_delete=models.CASCADE)
    

    #star        = models.IntegerField(verbose_name="星",validators=[MinValueValidator(1),MaxValueValidator(MAX_STAR)],default=1)
    content     = models.CharField(verbose_name="内容", max_length=100)

    created_at  = models.DateTimeField(verbose_name="投稿日時", default=timezone.now)
    updated_at  = models.DateTimeField(verbose_name="更新日時", auto_now=True)


    # 星のレビューの表示で使う
    """
    def star_icon(self):
        dic               = {}
        dic["true_star"]  = self.star * " "
        dic["false_star"] = ( MAX_STAR - self.star) * " "

        return dic
    """


# TODO: サンプルの要件定義書には含まれていないが、お気に入りは実装必須。
class Favorite(models.Model):
    """
    #同一ユーザーが複数回同じレストランをお気に入り登録できないように設定する（重複を防ぐ）
    class Meta:
        unique_together=("user","restaurant")
    """

    user       = models.ForeignKey(User, verbose_name="登録者",on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, verbose_name="店舗",on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="作成日時", default=timezone.now)


# 予約
class Reservation(models.Model):
    user            = models.ForeignKey(User, verbose_name="予約者", on_delete=models.CASCADE)
    restaurant      = models.ForeignKey(Restaurant, verbose_name="店舗", on_delete=models.CASCADE)

    datetime        = models.DateTimeField(verbose_name="予約日時")
    headcount       = models.PositiveIntegerField(verbose_name="人数")

    created_at  = models.DateTimeField(verbose_name="投稿日時", default=timezone.now)
    updated_at  = models.DateTimeField(verbose_name="更新日時", auto_now=True)



# 有料会員と無料会員の見分けをするモデル。
class PremiumUser(models.Model):
    user            = models.ForeignKey(User, verbose_name="有料会員", on_delete=models.CASCADE)
    # TextFieldは文字数の制限がないフィールド
    premium_code    = models.TextField(verbose_name="有料会員コード")
