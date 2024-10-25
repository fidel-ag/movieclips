from django.urls import path
from . import views

urlpatterns = [
	path('product_page', views.product_page, name='product_page'),
	path('payment_successful', views.payment_successful, name='payment_successful'),
	path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
	path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
    path("buycoins",views.buy_coins,name="buy_coins"),
    path("manageboughtcoins",views.manage_bought_coins,name="manage_bought_coins"),
	path("updatesubscription",views.update_subscription,name="update_subscription"),
    path("upgradeplan",views.upgrade_plan,name="upgrade_plan"),
    
]