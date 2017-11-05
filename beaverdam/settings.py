"""
Django settings for beaverdam project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use different key for production
SECRET_KEY = '8pje5%pxibt2c=&j_c+ly5v@x)$r77%h-x3%jluq-@)4^75)ak'
DEBUG = True

HELP_URL = os.environ.get('HELP_URL', 'http://deepait.com')
# this will show in a popup instead of the external HELP_URL
HELP_USE_MARKDOWN = False
HELP_EMBED = False
URL_ROOT = os.environ.get('URL_ROOT', 'url_root')
AWS_ID = os.environ.get('AWS_ID', 'aws_id')
AWS_KEY = os.environ.get('AWS_KEY', 'aws_key')

MTURK_TITLE = "Video annotation"
MTURK_DESCRIPTION = "Draw accurate boxes around every person in the video, we will pay a $0.02 bonus per accurate box drawn. Most of the payment is in the bonus"
MTURK_SANDBOX = True
MTURK_BONUS_MESSAGE = "Thanks for your work"
MTURK_REJECTION_MESSAGE = "Your work has not been accepted. You must follow the instructions of the task precisely to complete this task."
MTURK_BLOCK_MESSAGE = "I'm sorry but we have blocked you from working on our HITs. We have limited time and unfortunately your work accuracy was not up to the standards required."
MTURK_BONUS_PER_BOX = 0.02
MTURK_BASE_PAY = 0.04
MTURK_EMAIL_SUBJECT = "Question about your work"
MTURK_EMAIL_MESSAGE = """Thanks for your submission.

Unfortunately, we're not able to accept this work as it does not meet the standards required.

If you'd like to have another go at it, can you please carefully read the instructions and make sure you enter information for the entire video.

Otherwise, we will reject the task in 24 hours.

Please let us know if you've encountered any problems.

Regards
"""

ALLOWED_HOSTS=["*"]

#assert MTURK_SANDBOX or not DEBUG

# Application definition

INSTALLED_APPS = [
    'annotator',
    'mturk',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beaverdam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'beaverdam.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
]

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

CSRF_COOKIE_SECURE = not DEBUG


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static'
