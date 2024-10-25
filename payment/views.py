from django.shortcuts import render

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from payment.models import UserPayment
import stripe
import time

@csrf_exempt
def product_page(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	if request.method == 'POST':
		product=settings.PRODUCT_PRICE[request.POST["plan"]]
		checkout_session = stripe.checkout.Session.create(
			payment_method_types = ['card'],
			line_items = [
				{
					'price': product[0],
					'quantity': 1,
				},
			],
			mode='subscription',
			success_url = settings.REDIRECT_DOMAIN + '/accounts/signup?session_id={CHECKOUT_SESSION_ID}',
			cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
		)
		return redirect(checkout_session.url, code=303)
	return redirect("home")
@csrf_exempt
def buy_coins(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	if request.method == 'POST':
		print(request.POST)
		checkout_session = stripe.checkout.Session.create(
			payment_method_types = ['card'],
			line_items = [
				{
					'price': settings.COINS_PRICE[request.POST["plan"]],
					'quantity': request.POST["credit"],
				},
			],
			mode='payment',
			success_url = settings.REDIRECT_DOMAIN + '/manageboughtcoins?session_id={CHECKOUT_SESSION_ID}',
			cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
		)
		return redirect(checkout_session.url, code=303)
	return redirect("home")

@csrf_exempt
def upgrade_plan(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	if request.method == 'POST':
		product=settings.PRODUCT_PRICE[request.POST["plan"]]
		checkout_session = stripe.checkout.Session.create(
			payment_method_types = ['card'],
			line_items = [
				{
					'price': product[0],
					'quantity': 1,
				},
			],
			mode='subscription',
			success_url = settings.REDIRECT_DOMAIN + '/updatesubscription?session_id={CHECKOUT_SESSION_ID}',
			cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
		)
		return redirect(checkout_session.url, code=303)
	return redirect("home")

def retrieve_Number_of_coins(payment_id,All_payment_data):
    for i in All_payment_data:
        if All_payment_data[i][0]==payment_id:
            return All_payment_data[i][1]
		
def update_subscription(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	checkout_session_id = request.GET.get('session_id', None)
	session = stripe.checkout.Session.retrieve(checkout_session_id)
	subscription_id=session.subscription
	payment_id=stripe.Subscription.retrieve(subscription_id).plan.id
	number_of_coin=retrieve_Number_of_coins(payment_id,settings.PRODUCT_PRICE)
	user=request.user
	if user.stripe_subscription_id:
		stripe.Subscription.delete(user.stripe_subscription_id)
	user.stripe_subscription_id=subscription_id
	user.subscription_active=True
	user.coins+=number_of_coin
	user.save()
	return redirect("manage_subscription")


def manage_bought_coins(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	checkout_session_id = request.GET.get('session_id', None)
	session = stripe.checkout.Session.retrieve(checkout_session_id)
	total_added_coins=session.amount_total//500
	print(request.user.coins)
	request.user.coins+=total_added_coins
	request.user.save()
	return redirect("manage_subscription")

def payment_successful(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	checkout_session_id = request.GET.get('session_id', None)
	session = stripe.checkout.Session.retrieve(checkout_session_id)
	customer = stripe.Customer.retrieve(session.customer)
	print(customer)
	user_id = request.user.id
	user_payment = UserPayment.objects.get(app_user=user_id)
	user_payment.stripe_checkout_id = checkout_session_id
	user_payment.save()
	return render(request, 'user_payment/payment_successful.html', {'customer': customer})


def payment_cancelled(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	return render(request, 'user_payment/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	time.sleep(10)
	payload = request.body
	signature_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(
			payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
		)
	except ValueError as e:
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		session_id = session.get('id', None)
		time.sleep(15)
		user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
		user_payment.payment_bool = True
		user_payment.save()
	return HttpResponse(status=200)
