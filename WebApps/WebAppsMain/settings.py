"""
Django settings for WebAppsMain project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from WebAppsMain.secret_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: SECRET_KEY is in secrets.py, which is gitignored. It has the following content:
# SECRET_KEY = 'YourSecretKey!'
# It is imported by the line 'from WebAppsMain.secret_settings import *'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_ENV

# ALLOWED_HOSTS takes in a list of strings the host ip addresses
ALLOWED_HOSTS = HostList


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'PerInd.apps.PerindConfig', # Added by Yi Zong Kuang
    'FleetDataCollection.apps.FleetdatacollectionConfig', # Added by Yi Zong Kuang
    'OrgChartPortal.apps.OrgchartportalConfig', # Added by Yi Zong Kuang
    'DailyPothole.apps.DailypotholeConfig', # Added by Yi Zong Kuang
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',  # Added by Yi Zong Kuang, this causes "set_wakeup_fd only works in main thread" in django 3.0.8 but not in 2.2.14
]

# Added by Yi Zong Kuang, the entire AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
)

ROOT_URLCONF = 'WebAppsMain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'PerInd/templates'),
            os.path.join(BASE_DIR, 'MapsApp/templates'),
            os.path.join(BASE_DIR, 'FleetDataCollection/templates'),
            os.path.join(BASE_DIR, 'OrgChartPortal/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                ## Added by Yi Zong Kuang
                'django_settings_export.settings_export',
            ],
        },
    },
]

## Added by Yi Zong Kuang
SETTINGS_EXPORT = [
    ## SERVER_TYPE is only recognized by "Dev", "QA", or "Prod"
    'SERVER_TYPE',
    'PER_IND_VERSION',
    'DAILY_POTHOLE_VERSION',
    'ORG_CHART_PORTAL_VERSION',
    'FLEET_DATA_COLLECTION_VERSION',
    'MAPS_APP_VERSION',
]

WSGI_APPLICATION = 'WebAppsMain.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {}
DATABASES['default'] = {
    ## Default database to create the default tables needed by django.contrib.auth
    # 'ENGINE': 'django.db.backends.sqlite3',
    # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    'ENGINE':       'sql_server.pyodbc',
    'HOST' :        Default_SQLServerHost,
    'NAME' :        Default_SQLServerDbName,
    'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
    'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

    'OPTIONS' : {
        'driver' :      'SQL Server Native Client 11.0',
    },
}

if PerInd_UseWinAuth: # PerInd_UseWinAuth imported from secret_settings.py
    # https://django-mssql.readthedocs.io/en/latest/settings.html, read this doc on trusted connections. TLDR: Remove the line "'USER': '...'," and it will default to trusted connection
    DATABASES['PerInd'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        PerInd_SQLServerHost,
        'NAME' :        PerInd_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['PerInd'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        PerInd_SQLServerHost,
        'NAME' :        PerInd_SQLServerDbName,
        'USER' :        PerInd_SQLServerUID,       # PerInd_SQLServerUID imported from secret_settings.py
        'PASSWORD' :    PerInd_SQLServerPWD,       # PerInd_SQLServerPWD imported from secret_settings.py
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }

if FleetDataCollection_UseWinAuth:
    DATABASES['FleetDataCollection'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        FleetDataCollection_SQLServerHost,
        'NAME' :        FleetDataCollection_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['FleetDataCollection'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        FleetDataCollection_SQLServerHost,
        'NAME' :        FleetDataCollection_SQLServerDbName,
        'USER' :        FleetDataCollection_SQLServerUID,
        'PASSWORD' :    FleetDataCollection_SQLServerPWD,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }

if OrgChartRead_UseWinAuth:
    DATABASES['OrgChartRead'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        OrgChartRead_SQLServerHost,
        'NAME' :        OrgChartRead_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['OrgChartRead'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        OrgChartRead_SQLServerHost,
        'NAME' :        OrgChartRead_SQLServerDbName,
        'USER' :        OrgChartRead_SQLServerUID,
        'PASSWORD' :    OrgChartRead_SQLServerPWD,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }

if M5_UseWinAuth:
    DATABASES['M5'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        M5_SQLServerHost,
        'NAME' :        M5_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['M5'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        M5_SQLServerHost,
        'NAME' :        M5_SQLServerDbName,
        'USER' :        M5_SQLServerUID,
        'PASSWORD' :    M5_SQLServerPWD,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }

if OrgChartWrite_UseWinAuth:
    DATABASES['OrgChartWrite'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        OrgChartWrite_SQLServerHost,
        'NAME' :        OrgChartWrite_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['OrgChartWrite'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        OrgChartWrite_SQLServerHost,
        'NAME' :        OrgChartWrite_SQLServerDbName,
        'USER' :        OrgChartWrite_SQLServerUID,
        'PASSWORD' :    OrgChartWrite_SQLServerPWD,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }

if DailyPothole_UseWinAuth:
    DATABASES['DailyPothole'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        DailyPothole_SQLServerHost,
        'NAME' :        DailyPothole_SQLServerDbName,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }
else:
    DATABASES['DailyPothole'] = {
        'ENGINE':       'sql_server.pyodbc',
        'HOST' :        DailyPothole_SQLServerHost,
        'NAME' :        DailyPothole_SQLServerDbName,
        'USER' :        DailyPothole_SQLServerUID,
        'PASSWORD' :    DailyPothole_SQLServerPWD,
        'AUTOCOMMIT' :  True,               # Set this to False if you want to disable Django's transaction management and implement your own.
        'ATOMIC_REQUESTS' : True,           # All views/request are not wrapped in a transcation on the database, if response is produced without fails, will commit the transaction, else rolls back the transaction, ref: https://docs.djangoproject.com/en/3.0/topics/db/transactions/

        'OPTIONS' : {
            'driver' :      'SQL Server Native Client 11.0',
        },
    }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Take a look at README.md for some info on TIME_ZONE
TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

# Take a look at README.md for some info on USE_TZ
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
# https://docs.djangoproject.com/en/3.0/howto/static-files/deployment/
# https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/modwsgi/#serving-files    Serving with Apache and mod_wsgi

# STATIC_ROOT = BASE_DIR.replace("\\", '/') + '/static/'  # For deploying Django static file to production. Copies django static files to where STATIC_ROOT specifies
STATIC_URL = '/static/' # Where Django template looks for static files, whouls be same as the STATIC_ROOT minus the project root dir.

# STATICFILES_DIRS = [
#     # os.path.join(BASE_DIR, "static"),
#     BASE_DIR.replace("\\", '/'),
# ]


PER_IND_VERSION = '1.1.2'
MAPS_APP_VERSION = '1.1.0'
DAILY_POTHOLE_VERSION = '1.3.1'
ORG_CHART_PORTAL_VERSION = '1.15.0'
FLEET_DATA_COLLECTION_VERSION = '1.1.1'
