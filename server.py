"""
Entry point for the Flask application.
This module imports the app and routes, and runs the development server.
"""

# Import app from config
from modules.config import app

# Import routes to register them with the app
import modules.routes  # noqa: F401


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
