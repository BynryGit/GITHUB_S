"""
Django settings for DigiSpace project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tz5^n8f9ao9hyj!&yj2!&u94r3)%yl2tysfg7#1f0m_lkz9y2i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'digispaceapp',
    'subscriberapp',
    'crmapp',
    'captcha',
    'push_notifications',
    'digispaceapp.templatetags.my_template_tag',
    'djcelery',
    'kombu.transport.django'
)

import djcelery
djcelery.setup_loader()
BROKER_URL="django://"
CELERY_IMPORTS = ('DigiSpace.tasks')

PUSH_NOTIFICATIONS_SETTINGS = {
    "GCM_API_KEY": "AIzaSyDc3llc1alxNzkeoDgy9YpJnqUu4bQJJ_w",
}


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'subscriberapp.middleware.AutoLogout',
)


CAPTCHA_IMAGE_SIZE=(142,35)
CAPTCHA_FONT_SIZE=30
CAPTCHA_CHALLENGE_FUNCT = 'Admin.captcha_mod.random_digit_challenge'

ROOT_URLCONF = 'DigiSpace.urls'

WSGI_APPLICATION = 'DigiSpace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

'''DATABASES = {
   'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'digispace_db',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'TIME_ZONE': 'Asia/Kolkata',

   }
}'''

DATABASES = {
   'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ss_digispace_new1',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': 'localhost',
            'PORT': '3306',
            'TIME_ZONE': 'Asia/Kolkata',

   }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = False

TEMPLATE_DIRS = (
    BASE_DIR+'/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (BASE_DIR +'/static/',)

MEDIA_ROOT = BASE_DIR+'/media/'
MEDIA_URL ='/media/'

CRONJOBS = [
    ('0 0 * * *', 'digispaceapp.cron_sms_digispace.my_scheduled_job'),
    ('*/5 * * * *', 'digispaceapp.auto_activate.auto_activate_citystar'),
    ('*/5 * * * *', 'digispaceapp.auto_deactivate.auto_deactivate_citystar'),
    ('0 */3 * * *', 'digispaceapp.screen_cron_job.screen_present'),
]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 300 #equivalent to 30 minutes

#SESSION_EXPIRE_AT_BROWSER_CLOSE= True
