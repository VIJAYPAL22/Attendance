from flask import Flask
from .extensions import db, mail, migrate
from .scheduler import start_scheduler
from . import routes  # This will register all blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from .routes.attendance import attendance_bp
    from .routes.leaves import leaves_bp
    from .routes.dashboard import dashboard_bp
    from .routes.announcement import announcement_bp
    from .routes.auth import auth_bp
    from .routes.employee import employee_bp
    
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leaves_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    
    # Start scheduler
    start_scheduler()
    
    return app