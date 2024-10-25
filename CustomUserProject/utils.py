import datetime
from django.utils import timezone
import stripe
from django.conf import settings
from dateutil.relativedelta import relativedelta

def retrieve_Number_of_coins(payment_id,All_payment_data):
    for i in All_payment_data:
        if All_payment_data[i][0]==payment_id:
            return All_payment_data[i][1]
def parse_user_data(user):
    context={
        "username":use
    }     

def subscription_renewal_due(user):
    # Retrieve the subscription ID from the user's profile
    stripe.api_key=settings.STRIPE_SECRET_KEY_TEST
    stripe_subscription_id = user.get_stripe_subscription_id()

    if stripe_subscription_id:
        # Retrieve the subscription details from Stripe
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        current_period_end = subscription.current_period_end
        current_period_end_date = datetime.datetime.fromtimestamp(current_period_end)

        # Check if the subscription is active
        if subscription.status == 'active':
            months_passed = relativedelta(timezone.now().date(), user.last_coin_allocation.date()).months

            if months_passed>0:
                payment_id=subscription.plan.id
                number_of_coin=(retrieve_Number_of_coins(payment_id,settings.PRODUCT_PRICE))
                user.coins += months_passed*number_of_coin  # Default to 100 coins per month if not set
                user.last_coin_allocation = timezone.now().date()  # Update the last coin allocation date
                user.save()

                return True  # Coins were allocated for this month
            else:
                return False  # It's not time to allocate coins yet

    return False  # Subscription is not active or not found
 
def subscription_plan_retrieve(user):
    # Retrieve the subscription ID from the user's profile
    stripe.api_key=settings.STRIPE_SECRET_KEY_TEST
    stripe_subscription_id = user.get_stripe_subscription_id()
    if stripe_subscription_id:
        
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)
        current_period_end = subscription.current_period_end
        current_period_end_date = datetime.datetime.fromtimestamp(current_period_end)
        time_now=datetime.datetime.now()
        remainning_days=relativedelta(current_period_end_date,time_now).days
        plan=settings.PRICE_COINS[subscription.plan.id]+[remainning_days]
    else:
        plan=[0,"Free Trial",0]
    return plan