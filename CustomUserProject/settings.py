
import os
from pathlib import Path
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm!rylh71h*25(n3rr1=tnfk8oe#al^hicw&j(2xri2wo%gytgd'

# SECURITY WARNING: don't run with debug turned on in production!
BASE_DIR2 = Path(__file__).resolve().parent.parent
DEBUG = True
MEDIA_URL = '/media/'
MEDIA_ROOT = Path.joinpath(BASE_DIR2, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = Path.joinpath(BASE_DIR2, 'static')

UPLOAD_FOLDER = Path.joinpath(BASE_DIR2, 'tmp')
FINAL_OUTPUT_FOLDER = Path.joinpath(BASE_DIR2, 'static', 'final')
BEFORE_AUDIO_OUTPUT_FOLDER = Path.joinpath(BASE_DIR2, 'static', 'finalbeforeMusic')
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom user app
    'accounts',
    "payment",
    # third party apps
    'crispy_forms',
]

AUTH_USER_MODEL = 'accounts.User'  # changes the built-in user model to ours

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CustomUserProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),os.path.join(BASE_DIR2, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'CustomUserProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'musicdb',
#         'USER': 'root',
#         'PASSWORD': '',  # Empty password
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }



# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
# MEDIA_URL="/static/final/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR,'media'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# auth urls
from django.urls import reverse_lazy
LOGIN_URL = reverse_lazy('accounts:login')
LOGOUT_REDIRECT_URL = LOGIN_URL
LOGIN_REDIRECT_URL = reverse_lazy('accounts:home') # change this to your home page

# email configuration for development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = "support@LeadEditor.io"
EMAIL_HOST_PASSWORD = 'mvcccndpnrkltstc'
EMAIL_PORT = 587

# Time in seconds after each login attempts
LOGIN_ATTEMPTS_TIME_LIMIT = 0
# limit the amount of attempts to which the user will be inactive and password set mail sent
MAX_LOGIN_ATTEMPTS = 5


# stripe 

STRIPE_PUBLIC_KEY_TEST =os.getenv('STRIPE_PUBLIC_KEY_TEST')
STRIPE_SECRET_KEY_TEST = os.getenv('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET_TEST =os.getenv('STRIPE_WEBHOOK_SECRET_TEST')
PRODUCT_PRICE = {"Pro_Plan":["price_1QBMOrJfcqEyxtJLcRUG8YTj",25],"Premuim_Plan":["price_1QBMPdJfcqEyxtJLC0mi9YcQ",60]}
PRICE_COINS={"price_1QBMOrJfcqEyxtJLcRUG8YTj":[25,"Pro"],"price_1QBMPdJfcqEyxtJLC0mi9YcQ":[60,"Premuim"]}
COINS_PRICE={"Premium":"price_1QDTibJfcqEyxtJLtrxLMEW2","Pro":"price_1QDTk0JfcqEyxtJL2DJARXDH"}

REDIRECT_DOMAIN = 'http://127.0.0.1:8000'