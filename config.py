import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Admin key
    VALID_KEY = os.getenv('VALID_KEY')

    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Debug
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'

    # App download links and API key for app integration
    ANDROID_APP_URL = os.getenv('ANDROID_APP_URL', 'https://yourdomain.com/downloads/app-android.apk')
    IOS_APP_URL = os.getenv('IOS_APP_URL', 'https://apps.apple.com/your-app-id')
    WINDOWS_APP_URL = os.getenv('WINDOWS_APP_URL', 'https://yourdomain.com/downloads/app-windows.exe')
    APP_API_KEY = os.getenv('APP_API_KEY', 'your-secure-api-key-for-apps')