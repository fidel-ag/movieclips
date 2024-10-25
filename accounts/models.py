from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_staff=False, is_admin=False, is_active=True): # may look repetitive adding staff, admin and active status, but it simplifies the
                                                                                        # work when using create_staffuser() and create_superuser()
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError('User must have a password')
        user_obj = self.model(email=self.normalize_email(email))
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.admin = is_admin
        user_obj.staff = is_staff
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True, is_admin=True)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    coins=models.IntegerField(default=0)
    USERNAME_FIELD = 'email'  # this now over rides the username field and now email is the default field
    # REQUIRED_FIELDS = [] if you add another field and need it to be required, include it in the list
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_active = models.BooleanField(default=False)
    last_coin_allocation = models.DateTimeField(auto_now_add=True)
    username=models.CharField(max_length=30, blank=True, null=True,default="No Name found this is a test")
    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    def set_coins(self,num):
        self.coins=num
    def get_coins(self):
        return self.coins
    def get_stripe_subscription_id(self):
        return self.stripe_subscription_id
    def set_stripe_subscription_id(self,stripe_subscription_id):
        self.stripe_subscription_id=stripe_subscription_id
    def get_subscription_active(self):
        return self.subscription_active
    def set_subscription_active(self,subscription_active):
        self.subscription_active=subscription_active
    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    """@property
    def is_active(self):
        return self.is_active"""

# keep the base user as simple as possible and only include the minimum basic required fields
# you can extend this user using a profile to get more info about your users. e.g.

#class Profile(models.Model):
    #user = models.OneToOneField(User)
    # then add some other fields e.g. first name, last name, phone number e.t.c.


class LoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_attempts = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'user: {}, attempts: {}'.format(self.user.email, self.login_attempts)





