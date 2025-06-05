import os
from flask import current_app

class AppIntegration:
    @staticmethod
    def generate_app_links():
        return {
            'android': current_app.config.get('ANDROID_APP_URL'),
            'ios': current_app.config.get('IOS_APP_URL'),
            'windows': current_app.config.get('WINDOWS_APP_URL')
        }

    @staticmethod
    def validate_app_request(request):
        """Validate requests coming from official apps"""
        app_signature = request.headers.get('X-App-Signature')
        return app_signature == current_app.config.get('APP_API_KEY')
