# app/routes/__init__.py
def init_routes(app):
    from .auth import auth_bp
    from .employee import emp_bp
    from .announcement import ann_bp
    from .leaves import leave_bp
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(emp_bp)
    app.register_blueprint(ann_bp)
    app.register_blueprint(leave_bp)
