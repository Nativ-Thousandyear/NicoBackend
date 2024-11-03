import warnings
import time
import os
import logging
from flask import Flask, render_template
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import openai
from elevenlabs.client import ElevenLabs
from models import User, Election  # Ensure Election is imported for the admin dashboard
from extensions import db
from election_service import ElectionService
import controllers  # Import the controllers package
from routes.election_routes import election_bp  # Import the election routes blueprint
from config import ProductionConfig, TestingConfig  # Import the config classes

# Load environment variables from .env file
load_dotenv()
logging.info("Loaded .env file")

# Set up logging configuration
log_file_path = 'error.log'
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more verbose logging during development
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

# Debug log to check the loaded values
logging.debug("SQLALCHEMY_DATABASE_URI: %s", os.getenv("SQLALCHEMY_DATABASE_URI"))
logging.debug("SECRET_KEY: %s", os.getenv("SECRET_KEY"))


def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    logging.info("Starting application with config: %s", config_name)

    # Set configuration for different environments
    app.config.from_object(ProductionConfig if config_name == 'default' else TestingConfig)

    # Load additional settings from environment variables
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv("SECRET_KEY", 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

    # Log the selected database URI
    logging.info("Using database: %s", app.config['SQLALCHEMY_DATABASE_URI'])

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)

    # Database connection retry logic
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            with app.app_context():
                db.engine.connect()
            logging.info("Database connection successful on attempt %d", attempt + 1)
            break
        except (SQLAlchemyError, OperationalError) as e:
            logging.warning("Database connection attempt %d failed. Retrying in %d seconds...", attempt + 1, retry_delay)
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
            if attempt == max_retries - 1:
                logging.error("Failed to connect to the database after %d attempts. Error: %s", max_retries, str(e))
                raise

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Updated to use blueprint route

    @login_manager.user_loader
    def load_user(user_id):
        """Load a user from the user ID."""
        try:
            user = User.query.get(int(user_id))
            logging.debug("Loaded user: %s", user)
            return user
        except SQLAlchemyError as e:
            logging.error("Failed to load user with ID %s. Error: %s", user_id, str(e))
            return None

    # Initialize API clients
    api_key = os.getenv("OPENAI_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or not elevenlabs_api_key:
        logging.critical("Missing required API keys. OpenAI or ElevenLabs API key not found.")
        raise ValueError("Missing required API keys.")

    try:
        openai_client = openai.OpenAI(api_key=api_key)
        model = ChatOpenAI(model="gpt-4", api_key=api_key)
        app.openai_client = openai_client
        app.elevenclient = ElevenLabs(api_key=elevenlabs_api_key)
        logging.info("API clients initialized successfully.")
    except Exception as e:
        logging.error("Failed to initialize API clients. Error: %s", str(e))
        raise

    # Initialize ElectionService
    try:
        election_service = ElectionService(model=model, db=db)
        app.election_service = election_service
        logging.info("ElectionService initialized successfully.")
    except Exception as e:
        logging.error("Failed to initialize ElectionService. Error: %s", str(e))
        raise

    # Initialize all models within app context
    with app.app_context():
        try:
            from models import Election, Candidate, Vote, User, UserVote
            logging.debug("Models initialized within app context.")
        except ImportError as e:
            logging.error("Failed to import models. Error: %s", str(e))
            raise

    # Register all blueprints from controllers
    try:
        controllers.init_app(app)
        logging.info("Controllers initialized successfully.")
    except Exception as e:
        logging.error("Failed to initialize controllers. Error: %s", str(e))
        raise

    # Register the election routes blueprint
    try:
        app.register_blueprint(election_bp, url_prefix='/elections')
        logging.info("Election routes blueprint registered successfully.")
    except Exception as e:
        logging.error("Failed to register election blueprint. Error: %s", str(e))
        raise

    # Add the admin dashboard route
    @app.route('/admin_dashboard')
    @login_required
    def admin_dashboard():
        """Render the admin dashboard with all elections."""
        elections = Election.query.all()  # Fetch all elections from the database
        return render_template('admin_dashboard.html', elections=elections)

    return app

app = create_app()

if __name__ == "__main__":
    try:
        app.run(debug=True)  # Enable debug mode for direct runs
        logging.info("Application started successfully.")
    except Exception as e:
        logging.critical("Failed to start the application. Error: %s", str(e))
