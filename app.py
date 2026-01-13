import asyncio
from app import create_app
from app.utils.terraform_init import initialize_terraform


if __name__ == "__main__":
    # Initialize terraform once at startup
    asyncio.run(initialize_terraform())
    
    # Create and run the app
    app = create_app()
    app.run(debug=True, use_reloader=False)
