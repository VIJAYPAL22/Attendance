from flask import Blueprint, render_template,url_for,redirect,current_app

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    return redirect(url_for('dashboard.website_home'))

@dashboard_bp.route('/website')
def website_home():
    return render_template('website/website_home.html')

@dashboard_bp.route('/download-app')
def download_app():
    return render_template(
        'website/download_app.html',
        android_app_url=current_app.config.get('ANDROID_APP_URL'),
        ios_app_url=current_app.config.get('IOS_APP_URL'),
        windows_app_url=current_app.config.get('WINDOWS_APP_URL')
    )