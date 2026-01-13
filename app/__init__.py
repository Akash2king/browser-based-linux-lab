from quart import Quart


def create_app():
    """Application factory for creating Quart app instance"""
    app = Quart(__name__, template_folder='../templates')
    
    # Register blueprints
    from app.routes import lab_routes
    app.register_blueprint(lab_routes.bp)
    
    return app
