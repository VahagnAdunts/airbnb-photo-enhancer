from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
import os
import base64
import json
import logging
import re
import time
from datetime import datetime
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from image_enhancer import ImageEnhancer
from models import db, User, EnhancedImage, Payment
import stripe
from sqlalchemy.exc import OperationalError

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_handlers = [logging.StreamHandler()]
# Only add file handler if not in production (controlled by environment)
if os.getenv('FLASK_DEBUG', 'False').lower() == 'true':
    log_handlers.append(logging.FileHandler('server.log'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Database retry utility for handling transient connection errors
def retry_db_operation(operation, max_retries=3, initial_delay=1, max_delay=10):
    """
    Retry a database operation with exponential backoff.
    Handles recovery mode and connection errors.
    
    Args:
        operation: Callable that performs the database operation
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries in seconds
    
    Returns:
        Result of the operation
    
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except OperationalError as e:
            error_str = str(e).lower()
            # Check if it's a recoverable error
            is_recovery_mode = 'recovery mode' in error_str
            is_connection_error = any(term in error_str for term in [
                'eof detected', 'connection', 'ssl syscall', 'server closed',
                'connection reset', 'broken pipe'
            ])
            
            if (is_recovery_mode or is_connection_error) and attempt < max_retries:
                last_exception = e
                logger.warning(
                    f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
                delay = min(delay * 2, max_delay)  # Exponential backoff
                # Force session refresh to get a new connection
                db.session.rollback()
                continue
            else:
                # Not a recoverable error or max retries reached
                raise
        except Exception as e:
            # For non-OperationalError exceptions, don't retry
            raise
    
    # If we exhausted all retries, raise the last exception
    if last_exception:
        raise last_exception

# Verify Stripe library is properly installed (after logger is initialized)
try:
    # Check if stripe module is actually the Stripe library
    stripe_module_path = getattr(stripe, '__file__', None)
    stripe_version = getattr(stripe, '__version__', None)
    
    logger.info(f"Stripe module path: {stripe_module_path}")
    logger.info(f"Stripe library version: {stripe_version}")
    
    # Try to access checkout directly to see if it exists
    try:
        checkout_attr = getattr(stripe, 'checkout', None)
        logger.info(f"stripe.checkout type: {type(checkout_attr)}")
        logger.info(f"stripe.checkout value: {checkout_attr}")
        
        if checkout_attr is None:
            logger.error("CRITICAL: stripe.checkout is None")
            logger.error("Attempting to diagnose Stripe installation issue...")
            # Try to check if it's a namespace issue
            try:
                import stripe.checkout as checkout_module
                logger.info(f"Direct import of stripe.checkout successful: {checkout_module}")
                # If direct import works, reassign it
                stripe.checkout = checkout_module
                logger.info("Fixed: Reassigned stripe.checkout from direct import")
            except ImportError as ie:
                logger.error(f"Direct import of stripe.checkout failed: {ie}")
            except Exception as fix_error:
                logger.error(f"Error trying to fix checkout: {fix_error}")
        else:
            logger.info("Stripe checkout module is available")
    except AttributeError as ae:
        logger.error(f"CRITICAL: Cannot access stripe.checkout: {ae}")
except Exception as e:
    logger.error(f"CRITICAL: Error verifying Stripe library: {e}", exc_info=True)

app = Flask(__name__, static_folder='static', template_folder='.')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Database configuration - supports both PostgreSQL and SQLite
# Render provides DATABASE_URL with postgres:// but SQLAlchemy needs postgresql://
database_url = os.getenv('DATABASE_URL', 'sqlite:///airbnb_enhancer.db')
# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    logger.info("Converted postgres:// to postgresql:// for SQLAlchemy compatibility")

# Configure PostgreSQL SSL and connection pooling for Render
if database_url.startswith('postgresql://'):
    # Parse the URL to add SSL parameters if not present
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query)
    
    # Add SSL mode if not already present (required for Render PostgreSQL)
    if 'sslmode' not in query_params:
        query_params['sslmode'] = ['require']
        logger.info("Added sslmode=require to PostgreSQL connection")
    
    # Add connection timeout if not present
    if 'connect_timeout' not in query_params:
        query_params['connect_timeout'] = ['10']
    
    # Reconstruct URL with SSL parameters
    new_query = urlencode(query_params, doseq=True)
    database_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    logger.info("Configured PostgreSQL with SSL and connection settings")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connection pool settings for PostgreSQL
if database_url.startswith('postgresql://'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before using (handles connection drops)
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'pool_size': 5,         # Number of connections to maintain
        'max_overflow': 10,     # Additional connections beyond pool_size
    }

# Google Tag Manager Configuration
app.config['GTM_CONTAINER_ID'] = os.getenv('GTM_CONTAINER_ID', '')

# Stripe Configuration
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY', '')
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Initialize Stripe
stripe_secret_key = os.getenv('STRIPE_SECRET_KEY', '')
if stripe_secret_key:
    try:
        # Sanitize the API key - remove whitespace, newlines, etc.
        stripe_secret_key = stripe_secret_key.strip()
        stripe.api_key = stripe_secret_key
        app.config['STRIPE_SECRET_KEY'] = stripe_secret_key
        # Verify Stripe is fully initialized and checkout is available
        # Force access to checkout to ensure it's loaded
        try:
            # Check if checkout exists
            if not hasattr(stripe, 'checkout'):
                logger.error("Stripe module missing 'checkout' attribute - Stripe library may be corrupted")
            elif stripe.checkout is None:
                logger.error("stripe.checkout is None - Stripe library initialization failed")
                logger.error(f"Stripe version: {getattr(stripe, '__version__', 'unknown')}")
                logger.error("This may indicate a problem with the Stripe library installation")
            else:
                # Try to access Session to ensure it's available
                if hasattr(stripe.checkout, 'Session'):
                    logger.info(f"Stripe initialized successfully (key starts with: {stripe_secret_key[:7]}...)")
                    logger.info(f"Stripe version: {getattr(stripe, '__version__', 'unknown')}")
                else:
                    logger.warning("Stripe checkout.Session not available - this may cause payment issues")
        except Exception as init_error:
            logger.error(f"Error verifying Stripe checkout: {init_error}")
            logger.warning("Stripe API key set but checkout verification failed - this may cause payment issues")
    except Exception as e:
        logger.error(f"Error initializing Stripe: {e}")
        app.config['STRIPE_SECRET_KEY'] = ''
else:
    logger.warning("STRIPE_SECRET_KEY not set - payment features will not work")
    app.config['STRIPE_SECRET_KEY'] = ''

# Price per photo in cents ($0.55 = 55 cents)
PHOTO_PRICE_CENTS = 55

CORS(app)

# Make GTM_CONTAINER_ID available to all templates
@app.context_processor
def inject_gtm_container_id():
    return dict(gtm_container_id=app.config['GTM_CONTAINER_ID'])

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configuration
UPLOAD_FOLDER = 'uploads'
ENHANCED_FOLDER = 'enhanced'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENHANCED_FOLDER, exist_ok=True)

# Initialize image enhancer
enhancer = ImageEnhancer()

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_input(text, max_length=255):
    """Sanitize user input by removing dangerous characters and limiting length"""
    if not text:
        return None
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(text))
    # Limit length
    return text[:max_length].strip()

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_username(username):
    """Validate username format (alphanumeric, underscore, hyphen, 3-30 chars)"""
    if not username:
        return False
    pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(pattern, username))

# Create database tables with error handling
with app.app_context():
    try:
        # Log database configuration
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Don't log the full URI (may contain password), just the type
        if db_uri.startswith('sqlite'):
            logger.info("Using SQLite database")
        elif db_uri.startswith('postgresql'):
            logger.info("Using PostgreSQL database")
        else:
            logger.info(f"Using database: {db_uri.split('://')[0] if '://' in db_uri else 'unknown'}")
        
        # Create all tables
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Add new columns to existing tables if they don't exist (for migrations)
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Check if enhanced_image table exists
            if 'enhanced_image' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('enhanced_image')]
                
                if 'original_image_data' not in columns:
                    logger.info("Adding original_image_data column to enhanced_image table...")
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE enhanced_image ADD COLUMN original_image_data TEXT'))
                        conn.commit()
                    logger.info("Added original_image_data column")
                
                if 'enhanced_image_data' not in columns:
                    logger.info("Adding enhanced_image_data column to enhanced_image table...")
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE enhanced_image ADD COLUMN enhanced_image_data TEXT'))
                        conn.commit()
                    logger.info("Added enhanced_image_data column")
                
                if 'conversion_type' not in columns:
                    logger.info("Adding conversion_type column to enhanced_image table...")
                    with db.engine.connect() as conn:
                        # For SQLite
                        if db_uri.startswith('sqlite'):
                            conn.execute(text('ALTER TABLE enhanced_image ADD COLUMN conversion_type VARCHAR(20) DEFAULT "enhancement"'))
                        # For PostgreSQL
                        else:
                            conn.execute(text('ALTER TABLE "enhanced_image" ADD COLUMN conversion_type VARCHAR(20) DEFAULT \'enhancement\''))
                        conn.commit()
                    logger.info("Added conversion_type column")
            
            # Check if user table exists and add has_free_access column if needed
            if 'user' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('user')]
                
                if 'has_free_access' not in columns:
                    logger.info("Adding has_free_access column to user table...")
                    with db.engine.connect() as conn:
                        # For SQLite
                        if db_uri.startswith('sqlite'):
                            conn.execute(text('ALTER TABLE user ADD COLUMN has_free_access BOOLEAN DEFAULT 0'))
                        # For PostgreSQL
                        else:
                            conn.execute(text('ALTER TABLE "user" ADD COLUMN has_free_access BOOLEAN DEFAULT FALSE'))
                        conn.commit()
                    logger.info("Added has_free_access column")
        except Exception as migration_error:
            # Columns might already exist or table might not exist yet - that's okay
            logger.warning(f"Migration check: {migration_error} (columns may already exist or table not created yet)")
        
        # Verify tables exist by trying to query
        try:
            user_count = User.query.count()
            image_count = EnhancedImage.query.count()
            logger.info(f"Database initialized: {user_count} users, {image_count} images")
        except Exception as verify_error:
            logger.warning(f"Database tables created but verification query failed: {verify_error}")
    except Exception as db_init_error:
        logger.error(f"CRITICAL: Failed to initialize database: {db_init_error}", exc_info=True)
        logger.error("The application may not work correctly without a database!")
        # Don't raise - let the app start so we can see the error in logs

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Store return URL in session for OAuth redirect
    return_url = request.args.get('return_url')
    if return_url:
        session['return_url'] = return_url
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = sanitize_input(data.get('username'))
            password = data.get('password')
            
            if not username or not password:
                logger.warning(f"Login attempt with missing credentials from IP: {request.remote_addr}")
                return jsonify({'error': 'Username and password are required'}), 400
            
            if not validate_username(username):
                logger.warning(f"Invalid username format attempted: {username}")
                return jsonify({'error': 'Invalid username format'}), 400
            
            user = User.query.filter_by(username=username).first()
            
            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user, remember=True)
                logger.info(f"User {username} logged in successfully")
                
                # Link any recent photos (created within 1 hour) with user_id=None to this user
                try:
                    from datetime import timedelta
                    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                    unlinked_photos = EnhancedImage.query.filter(
                        EnhancedImage.user_id == None,
                        EnhancedImage.created_at >= one_hour_ago
                    ).all()
                    
                    if unlinked_photos:
                        for photo in unlinked_photos:
                            photo.user_id = user.id
                        db.session.commit()
                        logger.info(f"Linked {len(unlinked_photos)} photos to user {user.id} after login")
                except Exception as link_error:
                    logger.warning(f"Error linking photos after login: {link_error}")
                    db.session.rollback()
                
                # Check if there's a return URL or pending images
                return_url = request.args.get('return_url') or request.form.get('return_url')
                # If coming from home page, redirect to dashboard to show enhanced photos
                if return_url == '/' or return_url == url_for('index'):
                    if request.is_json:
                        return jsonify({'success': True, 'redirect': '/dashboard'})
                    return redirect(url_for('dashboard'))
                elif return_url:
                    if request.is_json:
                        return jsonify({'success': True, 'redirect': return_url})
                    return redirect(return_url)
                if request.is_json:
                    return jsonify({'success': True, 'redirect': '/dashboard'})
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for username: {username} from IP: {request.remote_addr}")
                if request.is_json:
                    return jsonify({'error': 'Invalid username or password'}), 401
                flash('Invalid username or password', 'error')
        except Exception as e:
            logger.error(f"Error in login endpoint: {e}", exc_info=True)
            if request.is_json:
                return jsonify({'error': 'An error occurred during login'}), 500
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Store return URL in session for OAuth redirect
    return_url = request.args.get('return_url')
    if return_url:
        session['return_url'] = return_url
    
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            username = sanitize_input(data.get('username'))
            email = sanitize_input(data.get('email'))
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            if not username or not email or not password:
                return jsonify({'error': 'All fields are required'}), 400
            
            if not validate_username(username):
                return jsonify({'error': 'Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens'}), 400
            
            if not validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            
            # Check for existing username
            if User.query.filter_by(username=username).first():
                logger.warning(f"Signup attempt with existing username: {username}")
                return jsonify({'error': 'Username already exists'}), 400
            
            # Check for existing email
            if User.query.filter_by(email=email).first():
                logger.warning(f"Signup attempt with existing email: {email}")
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create user with transaction
            try:
                password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(username=username, email=email, password_hash=password_hash)
                db.session.add(user)
                db.session.commit()
                logger.info(f"New user registered: {username} ({email})")
            except Exception as db_error:
                db.session.rollback()
                logger.error(f"Database error during signup: {db_error}", exc_info=True)
                return jsonify({'error': 'Failed to create account. Please try again.'}), 500
            
            login_user(user, remember=True)
            
            # Link any recent photos (created within 1 hour) with user_id=None to this user
            try:
                from datetime import timedelta
                one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                unlinked_photos = EnhancedImage.query.filter(
                    EnhancedImage.user_id == None,
                    EnhancedImage.created_at >= one_hour_ago
                ).all()
                
                if unlinked_photos:
                    for photo in unlinked_photos:
                        photo.user_id = user.id
                    db.session.commit()
                    logger.info(f"Linked {len(unlinked_photos)} photos to user {user.id} after signup")
            except Exception as link_error:
                logger.warning(f"Error linking photos after signup: {link_error}")
                db.session.rollback()
            
            # Check if there's a return URL or pending images
            return_url = request.args.get('return_url') or request.form.get('return_url')
            # If coming from home page, redirect to dashboard to show enhanced photos
            if return_url == '/' or return_url == url_for('index'):
                if request.is_json:
                    return jsonify({'success': True, 'redirect': '/dashboard'})
                return redirect(url_for('dashboard'))
            elif return_url:
                if request.is_json:
                    return jsonify({'success': True, 'redirect': return_url})
                return redirect(return_url)
            if request.is_json:
                return jsonify({'success': True, 'redirect': '/dashboard'})
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Error in signup endpoint: {e}", exc_info=True)
            if request.is_json:
                return jsonify({'error': 'An error occurred during signup'}), 500
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    logger.info(f"User logged out")
    return redirect(url_for('index'))

# Google OAuth Routes
@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth login"""
    if not os.getenv('GOOGLE_CLIENT_ID') or not os.getenv('GOOGLE_CLIENT_SECRET'):
        logger.error("Google OAuth credentials not configured")
        flash('Google sign-in is not configured. Please use email/password.', 'error')
        return redirect(url_for('login'))
    
    redirect_uri = url_for('google_callback', _external=True)
    # Normalize to localhost (127.0.0.1 and localhost are the same, but Google requires exact match)
    redirect_uri = redirect_uri.replace('127.0.0.1', 'localhost')
    logger.info(f"OAuth redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get token from Google
        token = google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fetch user info if not in token
            resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
            user_info = resp.json()
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        
        if not google_id or not email:
            logger.error("Google OAuth callback missing required user info")
            flash('Failed to retrieve user information from Google.', 'error')
            return redirect(url_for('login'))
        
        # Database operations with retry logic for connection issues
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check if user exists by Google ID
                user = User.query.filter_by(google_id=google_id).first()
                
                # If not found by Google ID, check by email
                if not user:
                    user = User.query.filter_by(email=email).first()
                    if user:
                        # Link Google account to existing user
                        user.google_id = google_id
                        db.session.commit()
                        logger.info(f"Linked Google account to existing user: {email}")
                        break
                
                # Create new user if doesn't exist
                if not user:
                    # Generate username from email or name
                    username_base = email.split('@')[0] if email else name.lower().replace(' ', '_')
                    username = username_base
                    counter = 1
                    # Ensure username is unique
                    while User.query.filter_by(username=username).first():
                        username = f"{username_base}{counter}"
                        counter += 1
                    
                    user = User(
                        username=username,
                        email=email,
                        google_id=google_id,
                        password_hash=None  # OAuth users don't have passwords
                    )
                    db.session.add(user)
                    db.session.commit()
                    logger.info(f"New Google OAuth user created: {username} ({email})")
                    break
                
                # If we got here, user exists and we're done
                break
                
            except Exception as db_error:
                retry_count += 1
                db.session.rollback()
                logger.warning(f"Database error during Google OAuth (attempt {retry_count}/{max_retries}): {db_error}")
                
                if retry_count >= max_retries:
                    logger.error(f"Failed to complete Google OAuth after {max_retries} attempts: {db_error}", exc_info=True)
                    flash('Database connection error. Please try again.', 'error')
                    return redirect(url_for('login'))
                
                # Wait a bit before retrying
                import time
                time.sleep(0.5 * retry_count)  # Exponential backoff
        
        if not user:
            logger.error("Failed to create or retrieve user after retries")
            flash('Failed to create account. Please try again.', 'error')
            return redirect(url_for('login'))
        
        # Log the user in
        login_user(user, remember=True)
        logger.info(f"User {user.username} logged in via Google OAuth")
        
        # Link any recent photos (created within 1 hour) with user_id=None to this user
        try:
            from datetime import timedelta
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            unlinked_photos = EnhancedImage.query.filter(
                EnhancedImage.user_id == None,
                EnhancedImage.created_at >= one_hour_ago
            ).all()
            
            if unlinked_photos:
                for photo in unlinked_photos:
                    photo.user_id = user.id
                db.session.commit()
                logger.info(f"Linked {len(unlinked_photos)} photos to user {user.id} after Google OAuth login")
        except Exception as link_error:
            logger.warning(f"Error linking photos after Google OAuth login: {link_error}")
            db.session.rollback()
        
        # Check for return URL from session or request
        return_url = session.pop('return_url', None) or request.args.get('return_url')
        if return_url == '/' or return_url == url_for('index'):
            return redirect(url_for('dashboard'))
        elif return_url:
            return redirect(return_url)
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        logger.error(f"Error in Google OAuth callback: {e}", exc_info=True)
        flash('An error occurred during Google sign-in. Please try again.', 'error')
        return redirect(url_for('login'))

@app.route('/')
def index():
    # Redirect authenticated users to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/api/check-auth')
def check_auth():
    """Check if user is authenticated"""
    return jsonify({'authenticated': current_user.is_authenticated})

@app.route('/api/health')
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        # Test database connection
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_type = 'SQLite' if db_uri.startswith('sqlite') else 'PostgreSQL' if db_uri.startswith('postgresql') else 'Unknown'
        
        # Try to query the database
        user_count = User.query.count()
        image_count = EnhancedImage.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': {
                'type': db_type,
                'connected': True,
                'users': user_count,
                'images': image_count
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'database': {
                'connected': False,
                'error': str(e)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    from flask import make_response
    
    # List of all public pages with their priorities and change frequencies
    pages = [
        {
            'loc': 'https://elevance.art/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'daily',
            'priority': '1.0'
        },
        {
            'loc': 'https://elevance.art/pricing',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.9'
        },
        {
            'loc': 'https://elevance.art/features',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.8'
        },
        {
            'loc': 'https://elevance.art/about',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': 'https://elevance.art/contact',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.6'
        },
        {
            'loc': 'https://elevance.art/blog',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        },
        {
            'loc': 'https://elevance.art/blog/10-tips-for-better-airbnb-photos',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': 'https://elevance.art/blog/how-to-increase-bookings-with-professional-photos',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': 'https://elevance.art/blog/before-after-airbnb-photo-transformations',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'monthly',
            'priority': '0.7'
        },
        {
            'loc': 'https://elevance.art/terms',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/privacy',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/refund',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
        {
            'loc': 'https://elevance.art/cookies',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'changefreq': 'yearly',
            'priority': '0.3'
        },
    ]
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for SEO"""
    from flask import make_response
    
    robots_txt = """User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /api/
Disallow: /payment/
Disallow: /auth/
Disallow: /login
Disallow: /signup

Sitemap: https://elevance.art/sitemap.xml
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Clear payment session flag if it exists (downloads already handled on payment success page)
    session.pop('payment_success_session_id', None)
    
    return render_template('dashboard.html', user=current_user)

# Legal and Information Pages
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/refund')
def refund():
    return render_template('refund.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

# Blog Routes
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog/10-tips-for-better-airbnb-photos')
def blog_10_tips():
    return render_template('blog_10_tips.html')

@app.route('/blog/how-to-increase-bookings-with-professional-photos')
def blog_increase_bookings():
    return render_template('blog_increase_bookings.html')

@app.route('/blog/before-after-airbnb-photo-transformations')
def blog_before_after():
    return render_template('blog_before_after.html')

@app.route('/api/convert-to-night', methods=['POST'])
def convert_to_night():
    """Convert a day photo to a night photo"""
    try:
        if 'image' not in request.files:
            logger.warning("Night conversion request without image file")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            logger.warning("Night conversion request with empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type attempted: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save original image
        filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)
        
        # Convert to night
        night_path, conversion_info = enhancer.convert_to_night(original_path, filename)
        
        # Get file sizes
        original_file_size = os.path.getsize(original_path)
        night_file_size = os.path.getsize(night_path)
        
        # Get night filename from path
        night_filename = os.path.basename(night_path)
        
        # Read images as base64 for database storage (persists across deployments)
        original_image_data = None
        night_image_data = None
        try:
            with open(original_path, 'rb') as f:
                original_image_data = base64.b64encode(f.read()).decode('utf-8')
            with open(night_path, 'rb') as f:
                night_image_data = base64.b64encode(f.read()).decode('utf-8')
            logger.info("Images encoded as base64 for database storage")
        except Exception as encode_error:
            logger.error(f"Error encoding images for database storage: {encode_error}")
            # Continue without base64 storage - files will still work if they exist
        
        # Save photo records to database with transaction (with retry logic)
        try:
            # Check if user is authenticated
            user_id = current_user.id if current_user.is_authenticated else None
            logger.info(f"Saving night-converted image to database. User authenticated: {current_user.is_authenticated}, User ID: {user_id}")
            
            enhanced_image_record = EnhancedImage(
                user_id=user_id,
                original_filename=filename,
                original_path=original_path,
                original_file_size=original_file_size,
                enhanced_filename=night_filename,
                enhanced_path=night_path,
                enhanced_file_size=night_file_size,
                original_image_data=original_image_data,
                enhanced_image_data=night_image_data,
                conversion_type='night_conversion',
                change_intensity='moderate',  # Not used for night conversion but required
                detail_level='moderate',  # Not used for night conversion but required
                enhancement_settings=json.dumps(conversion_info) if conversion_info else None,
                ai_analysis=conversion_info.get('response', '') if conversion_info else None
            )
            
            db.session.add(enhanced_image_record)
            
            # Update user's processed images count if logged in
            if current_user.is_authenticated:
                current_user.images_processed += 1
                logger.info(f"Updating user {user_id} processed images count to {current_user.images_processed}")
            
            # Use retry logic for database commit to handle recovery mode and connection errors
            def commit_operation():
                db.session.commit()
                # Refresh the record to ensure we have the ID after commit
                db.session.refresh(enhanced_image_record)
                # Verify the ID was set
                if enhanced_image_record.id is None:
                    raise Exception("Image ID was not set after commit")
                return enhanced_image_record
            
            # Retry commit and get the record back
            enhanced_image_record = retry_db_operation(commit_operation, max_retries=3, initial_delay=2, max_delay=10)
            
            # Double-check the ID is set
            if enhanced_image_record.id is None:
                logger.error(f"Image ID is None after commit for {filename}")
                # Try to query the record again by filename and user_id
                recent_photo = EnhancedImage.query.filter_by(
                    user_id=user_id,
                    original_filename=filename,
                    conversion_type='night_conversion'
                ).order_by(EnhancedImage.created_at.desc()).first()
                if recent_photo and recent_photo.id:
                    enhanced_image_record = recent_photo
                    logger.info(f"Found image record with ID {recent_photo.id} by querying")
                else:
                    raise Exception("Image ID is None and could not be found by query")
            
            logger.info(f"Image converted to night and saved successfully: {filename} (ID: {enhanced_image_record.id}, User ID: {user_id})")
        except Exception as db_error:
            db.session.rollback()
            error_str = str(db_error).lower()
            is_recovery_mode = 'recovery mode' in error_str
            is_connection_error = any(term in error_str for term in [
                'eof detected', 'connection', 'ssl syscall', 'server closed'
            ])
            
            logger.error(f"Database error during image save: {db_error}", exc_info=True)
            logger.error(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")  # Log partial URI
            logger.error(f"User authenticated: {current_user.is_authenticated}")
            if current_user.is_authenticated:
                logger.error(f"User ID: {current_user.id}")
            
            # Clean up files if database save failed
            if os.path.exists(original_path):
                try:
                    os.remove(original_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup original file: {cleanup_error}")
            if os.path.exists(night_path):
                try:
                    os.remove(night_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup night file: {cleanup_error}")
            
            # Provide user-friendly error message
            if is_recovery_mode:
                error_message = 'The database is temporarily unavailable. Please try again in a few moments.'
            elif is_connection_error:
                error_message = 'Database connection error. Please try again.'
            else:
                error_message = 'Failed to save image record. Please try again or contact support if the issue persists.'
            
            return jsonify({
                'error': error_message,
                'details': 'The image was converted but could not be saved. Please try uploading again.'
            }), 500
        
        # Convert to base64 for response
        # Try to read from file first, fallback to database if file doesn't exist
        original_url = None
        night_url = None
        
        try:
            if os.path.exists(original_path):
                with open(original_path, 'rb') as f:
                    original_data = base64.b64encode(f.read()).decode('utf-8')
                    original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{original_data}"
            elif enhanced_image_record.original_image_data:
                # Use database-stored image
                original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{enhanced_image_record.original_image_data}"
                logger.info("Using database-stored original image for response")
        except Exception as e:
            logger.error(f"Error reading original image for response: {e}")
            # Try database fallback
            if enhanced_image_record.original_image_data:
                original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{enhanced_image_record.original_image_data}"
        
        try:
            if os.path.exists(night_path):
                with open(night_path, 'rb') as f:
                    night_data = base64.b64encode(f.read()).decode('utf-8')
                    night_url = f"data:image/jpeg;base64,{night_data}"
            elif enhanced_image_record.enhanced_image_data:
                # Use database-stored image
                night_url = f"data:image/jpeg;base64,{enhanced_image_record.enhanced_image_data}"
                logger.info("Using database-stored night-converted image for response")
        except Exception as e:
            logger.error(f"Error reading night image for response: {e}")
            # Try database fallback
            if enhanced_image_record.enhanced_image_data:
                night_url = f"data:image/jpeg;base64,{enhanced_image_record.enhanced_image_data}"
        
        # If we still don't have URLs, something went wrong
        if not original_url or not night_url:
            logger.error(f"Failed to generate image URLs. Original: {bool(original_url)}, Night: {bool(night_url)}")
            return jsonify({
                'error': 'Failed to process images. Please try again.',
                'details': 'Image files could not be read or encoded.'
            }), 500
        
        return jsonify({
            'success': True,
            'original_image_url': original_url,
            'enhanced_image_url': night_url,  # Using same field name for consistency
            'enhancements': conversion_info,
            'image_id': enhanced_image_record.id,
            'requires_login': not current_user.is_authenticated,
            'conversion_type': 'night_conversion'
        })
    
    except Exception as e:
        logger.error(f"Error in convert_to_night endpoint: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing the image'}), 500

@app.route('/api/enhance', methods=['POST'])
def enhance_image():
    try:
        if 'image' not in request.files:
            logger.warning("Enhance request without image file")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            logger.warning("Enhance request with empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type attempted: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get enhancement settings from form data
        change_intensity = request.form.get('change_intensity', 'moderate')
        detail_level = request.form.get('detail_level', 'moderate')
        
        # Validate settings
        if change_intensity not in ['minimal', 'moderate', 'extensive']:
            change_intensity = 'moderate'
        if detail_level not in ['minimal', 'moderate', 'extensive']:
            detail_level = 'moderate'
        
        # Save original image
        filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)
        
        # Enhance the image with user preferences
        enhanced_path, enhancements = enhancer.enhance_image(
            original_path, 
            filename,
            change_intensity=change_intensity,
            detail_level=detail_level
        )
        
        # Get file sizes
        original_file_size = os.path.getsize(original_path)
        enhanced_file_size = os.path.getsize(enhanced_path)
        
        # Get enhanced filename from path
        enhanced_filename = os.path.basename(enhanced_path)
        
        # Read images as base64 for database storage (persists across deployments)
        original_image_data = None
        enhanced_image_data = None
        try:
            with open(original_path, 'rb') as f:
                original_image_data = base64.b64encode(f.read()).decode('utf-8')
            with open(enhanced_path, 'rb') as f:
                enhanced_image_data = base64.b64encode(f.read()).decode('utf-8')
            logger.info("Images encoded as base64 for database storage")
        except Exception as encode_error:
            logger.error(f"Error encoding images for database storage: {encode_error}")
            # Continue without base64 storage - files will still work if they exist
        
        # Save photo records to database with transaction (with retry logic)
        try:
            # Check if user is authenticated
            user_id = current_user.id if current_user.is_authenticated else None
            logger.info(f"Saving enhanced image to database. User authenticated: {current_user.is_authenticated}, User ID: {user_id}")
            
            enhanced_image_record = EnhancedImage(
                user_id=user_id,
                original_filename=filename,
                original_path=original_path,
                original_file_size=original_file_size,
                enhanced_filename=enhanced_filename,
                enhanced_path=enhanced_path,
                enhanced_file_size=enhanced_file_size,
                original_image_data=original_image_data,
                enhanced_image_data=enhanced_image_data,
                conversion_type='enhancement',
                change_intensity=change_intensity,
                detail_level=detail_level,
                enhancement_settings=json.dumps(enhancements) if enhancements else None,
                ai_analysis=enhancements.get('response', '') if enhancements else None
            )
            
            db.session.add(enhanced_image_record)
            
            # Update user's processed images count if logged in
            if current_user.is_authenticated:
                current_user.images_processed += 1
                logger.info(f"Updating user {user_id} processed images count to {current_user.images_processed}")
            
            # Use retry logic for database commit to handle recovery mode and connection errors
            def commit_operation():
                db.session.commit()
                # Refresh the record to ensure we have the ID after commit
                db.session.refresh(enhanced_image_record)
                # Verify the ID was set
                if enhanced_image_record.id is None:
                    raise Exception("Image ID was not set after commit")
                return enhanced_image_record
            
            # Retry commit and get the record back
            enhanced_image_record = retry_db_operation(commit_operation, max_retries=3, initial_delay=2, max_delay=10)
            
            # Double-check the ID is set
            if enhanced_image_record.id is None:
                logger.error(f"Image ID is None after commit for {filename}")
                # Try to query the record again by filename and user_id
                recent_photo = EnhancedImage.query.filter_by(
                    user_id=user_id,
                    original_filename=filename
                ).order_by(EnhancedImage.created_at.desc()).first()
                if recent_photo and recent_photo.id:
                    enhanced_image_record = recent_photo
                    logger.info(f"Found image record with ID {recent_photo.id} by querying")
                else:
                    raise Exception("Image ID is None and could not be found by query")
            
            logger.info(f"Image enhanced and saved successfully: {filename} (ID: {enhanced_image_record.id}, User ID: {user_id})")
        except Exception as db_error:
            db.session.rollback()
            error_str = str(db_error).lower()
            is_recovery_mode = 'recovery mode' in error_str
            is_connection_error = any(term in error_str for term in [
                'eof detected', 'connection', 'ssl syscall', 'server closed'
            ])
            
            logger.error(f"Database error during image save: {db_error}", exc_info=True)
            logger.error(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")  # Log partial URI
            logger.error(f"User authenticated: {current_user.is_authenticated}")
            if current_user.is_authenticated:
                logger.error(f"User ID: {current_user.id}")
            
            # Clean up files if database save failed
            if os.path.exists(original_path):
                try:
                    os.remove(original_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup original file: {cleanup_error}")
            if os.path.exists(enhanced_path):
                try:
                    os.remove(enhanced_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup enhanced file: {cleanup_error}")
            
            # Provide user-friendly error message
            if is_recovery_mode:
                error_message = 'The database is temporarily unavailable. Please try again in a few moments.'
            elif is_connection_error:
                error_message = 'Database connection error. Please try again.'
            else:
                error_message = 'Failed to save image record. Please try again or contact support if the issue persists.'
            
            return jsonify({
                'error': error_message,
                'details': 'The image was enhanced but could not be saved. Please try uploading again.'
            }), 500
        
        # Convert to base64 for response
        # Try to read from file first, fallback to database if file doesn't exist
        original_url = None
        enhanced_url = None
        
        try:
            if os.path.exists(original_path):
                with open(original_path, 'rb') as f:
                    original_data = base64.b64encode(f.read()).decode('utf-8')
                    original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{original_data}"
            elif enhanced_image_record.original_image_data:
                # Use database-stored image
                original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{enhanced_image_record.original_image_data}"
                logger.info("Using database-stored original image for response")
        except Exception as e:
            logger.error(f"Error reading original image for response: {e}")
            # Try database fallback
            if enhanced_image_record.original_image_data:
                original_url = f"data:image/{filename.rsplit('.', 1)[1] if '.' in filename else 'jpeg'};base64,{enhanced_image_record.original_image_data}"
        
        try:
            if os.path.exists(enhanced_path):
                with open(enhanced_path, 'rb') as f:
                    enhanced_data = base64.b64encode(f.read()).decode('utf-8')
                    enhanced_url = f"data:image/jpeg;base64,{enhanced_data}"
            elif enhanced_image_record.enhanced_image_data:
                # Use database-stored image
                enhanced_url = f"data:image/jpeg;base64,{enhanced_image_record.enhanced_image_data}"
                logger.info("Using database-stored enhanced image for response")
        except Exception as e:
            logger.error(f"Error reading enhanced image for response: {e}")
            # Try database fallback
            if enhanced_image_record.enhanced_image_data:
                enhanced_url = f"data:image/jpeg;base64,{enhanced_image_record.enhanced_image_data}"
        
        # If we still don't have URLs, something went wrong
        if not original_url or not enhanced_url:
            logger.error(f"Failed to generate image URLs. Original: {bool(original_url)}, Enhanced: {bool(enhanced_url)}")
            return jsonify({
                'error': 'Failed to process images. Please try again.',
                'details': 'Image files could not be read or encoded.'
            }), 500
        
        return jsonify({
            'success': True,
            'original_image_url': original_url,
            'enhanced_image_url': enhanced_url,
            'enhancements': enhancements,
            'image_id': enhanced_image_record.id,
            'requires_login': not current_user.is_authenticated
        })
    
    except Exception as e:
        logger.error(f"Error in enhance_image endpoint: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing the image'}), 500

@app.route('/api/user/stats')
@login_required
def user_stats():
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'images_processed': current_user.images_processed,
        'member_since': current_user.created_at.strftime('%B %Y')
    })

# Photo Management Routes
@app.route('/api/photos')
@login_required
def get_user_photos():
    """Get all photos for the current user"""
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Limit to 100 per page
        
        # Query photos for the current user
        photos_query = EnhancedImage.query.filter_by(user_id=current_user.id)
        photos_query = photos_query.order_by(EnhancedImage.created_at.desc())
        
        # Paginate
        pagination = photos_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Filter out photos where files don't exist and no database backup
        valid_photos = []
        for photo in pagination.items:
            # Check if photo is accessible (file exists OR database has backup)
            file_exists = os.path.exists(photo.enhanced_path) or photo.enhanced_image_data is not None
            if file_exists:
                valid_photos.append(photo.to_dict())
            else:
                logger.warning(f"Photo {photo.id} has no file and no database backup - skipping")
        
        return jsonify({
            'success': True,
            'photos': valid_photos,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error in get_user_photos: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve photos'}), 500

@app.route('/api/photos/<int:photo_id>')
@login_required
def get_photo(photo_id):
    """Get a specific photo by ID"""
    try:
        photo = EnhancedImage.query.get_or_404(photo_id)
        
        # Check if the photo belongs to the current user
        if photo.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'photo': photo.to_dict()
        })
    except Exception as e:
        logger.error(f"Error in get_photo: {e}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve photo'}), 500

@app.route('/api/photos/<int:photo_id>/original')
@login_required
def serve_original_photo(photo_id):
    """Serve the original image file"""
    try:
        photo = EnhancedImage.query.get_or_404(photo_id)
        
        # Check if the photo belongs to the current user
        if photo.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Try to serve from file first (if it exists)
        if os.path.exists(photo.original_path):
            return send_file(photo.original_path, mimetype='image/jpeg')
        
        # If file doesn't exist, serve from database (base64)
        if photo.original_image_data:
            try:
                logger.info(f"Serving original image {photo_id} from database (file not found)")
                image_bytes = base64.b64decode(photo.original_image_data)
                if len(image_bytes) == 0:
                    logger.warning(f"Original image {photo_id} has empty base64 data")
                    return jsonify({'error': 'Image data is empty'}), 404
                return send_file(BytesIO(image_bytes), mimetype='image/jpeg', download_name=photo.original_filename)
            except Exception as decode_error:
                logger.error(f"Error decoding original image {photo_id} from base64: {decode_error}")
                return jsonify({'error': 'Failed to decode image data'}), 500
        
        # Neither file nor database data available
        logger.warning(f"Original image {photo_id} not found in file system or database")
        return jsonify({'error': 'Original image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving original photo: {e}", exc_info=True)
        return jsonify({'error': 'Failed to serve photo'}), 500

@app.route('/api/photos/<int:photo_id>/enhanced')
@login_required
def serve_enhanced_photo(photo_id):
    """Serve the enhanced image file"""
    try:
        photo = EnhancedImage.query.get_or_404(photo_id)
        
        # Check if the photo belongs to the current user
        if photo.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Try to serve from file first (if it exists)
        if os.path.exists(photo.enhanced_path):
            return send_file(photo.enhanced_path, mimetype='image/jpeg')
        
        # If file doesn't exist, serve from database (base64)
        if photo.enhanced_image_data:
            try:
                logger.info(f"Serving enhanced image {photo_id} from database (file not found)")
                image_bytes = base64.b64decode(photo.enhanced_image_data)
                if len(image_bytes) == 0:
                    logger.warning(f"Enhanced image {photo_id} has empty base64 data")
                    return jsonify({'error': 'Image data is empty'}), 404
                return send_file(BytesIO(image_bytes), mimetype='image/jpeg', download_name=photo.enhanced_filename)
            except Exception as decode_error:
                logger.error(f"Error decoding enhanced image {photo_id} from base64: {decode_error}")
                return jsonify({'error': 'Failed to decode image data'}), 500
        
        # Neither file nor database data available
        logger.warning(f"Enhanced image {photo_id} not found in file system or database")
        return jsonify({'error': 'Enhanced image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving enhanced photo: {e}", exc_info=True)
        return jsonify({'error': 'Failed to serve photo'}), 500

@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
@login_required
def delete_photo(photo_id):
    """Delete a photo and its files"""
    try:
        photo = EnhancedImage.query.get_or_404(photo_id)
        
        # Check if the photo belongs to the current user
        if photo.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete files if they exist
        file_deletion_errors = []
        if os.path.exists(photo.original_path):
            try:
                os.remove(photo.original_path)
            except Exception as file_error:
                file_deletion_errors.append(f"Failed to delete original: {file_error}")
                logger.warning(f"Failed to delete original file {photo.original_path}: {file_error}")
        
        if os.path.exists(photo.enhanced_path):
            try:
                os.remove(photo.enhanced_path)
            except Exception as file_error:
                file_deletion_errors.append(f"Failed to delete enhanced: {file_error}")
                logger.warning(f"Failed to delete enhanced file {photo.enhanced_path}: {file_error}")
        
        # Delete from database with transaction
        try:
            db.session.delete(photo)
            
            # Update user's processed images count
            if current_user.images_processed > 0:
                current_user.images_processed -= 1
            
            db.session.commit()
            logger.info(f"Photo {photo_id} deleted successfully by user {current_user.id}")
            
            message = 'Photo deleted successfully'
            if file_deletion_errors:
                message += f" (Note: {', '.join(file_deletion_errors)})"
            
            return jsonify({
                'success': True,
                'message': message
            })
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error during photo deletion: {db_error}", exc_info=True)
            return jsonify({'error': 'Failed to delete photo from database'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting photo: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while deleting the photo'}), 500

# Stripe Payment Routes
@app.route('/api/payment/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe Checkout Session for photo downloads"""
    # Check if Stripe is configured BEFORE trying to use it
    stripe_secret = os.getenv('STRIPE_SECRET_KEY', '') or app.config.get('STRIPE_SECRET_KEY', '')
    
    if not stripe_secret:
        logger.error("Stripe not configured - STRIPE_SECRET_KEY missing from environment")
        return jsonify({'error': 'Payment system not configured. Please set STRIPE_SECRET_KEY environment variable.'}), 500
    
    # Sanitize the API key - remove whitespace, newlines, etc.
    stripe_secret = stripe_secret.strip()
    
    # Validate API key format
    if not stripe_secret.startswith(('sk_live_', 'sk_test_')):
        logger.error(f"Invalid Stripe API key format (doesn't start with sk_live_ or sk_test_)")
        return jsonify({'error': 'Payment system error. Invalid API key format. Please contact support.'}), 500
    
    # Ensure Stripe API key is set with sanitized value
    if not stripe.api_key or stripe.api_key != stripe_secret:
        stripe.api_key = stripe_secret
        logger.info(f"Setting Stripe API key (key type: {'live' if stripe_secret.startswith('sk_live_') else 'test'})")
    
    # Verify Stripe module is properly loaded
    if not hasattr(stripe, 'checkout'):
        logger.error("Stripe module missing 'checkout' attribute - Stripe library may not be properly installed")
        return jsonify({'error': 'Payment system error. Please contact support.'}), 500
    
    if stripe.checkout is None:
        logger.error("stripe.checkout is None - Stripe library initialization issue")
        # Try multiple methods to fix the checkout module
        try:
            # Method 1: Try direct import
            try:
                import stripe.checkout as checkout_module
                stripe.checkout = checkout_module
                logger.info("Fixed stripe.checkout using direct import")
            except ImportError:
                # Method 2: Try reloading the module
                import importlib
                importlib.reload(stripe)
                stripe.api_key = stripe_secret
                # Method 3: Try accessing via getattr with default
                if stripe.checkout is None:
                    # Try to manually construct the checkout namespace
                    try:
                        from stripe import resources
                        if hasattr(resources, 'checkout'):
                            stripe.checkout = resources.checkout
                            logger.info("Fixed stripe.checkout using resources module")
                    except:
                        pass
                
            if stripe.checkout is None:
                logger.error("stripe.checkout still None after all fix attempts")
                logger.error("This indicates Stripe library is not properly installed")
                return jsonify({'error': 'Payment system error. Stripe library installation issue. Please contact support.'}), 500
        except Exception as reload_error:
            logger.error(f"Error attempting to fix Stripe checkout: {reload_error}", exc_info=True)
            return jsonify({'error': 'Payment system error. Please contact support.'}), 500
    
    # Verify Session class exists
    if not hasattr(stripe.checkout, 'Session'):
        logger.error("stripe.checkout.Session not available")
        return jsonify({'error': 'Payment system error. Please contact support.'}), 500
    
    try:
        data = request.get_json()
        photo_ids = data.get('photo_ids', [])
        
        if not photo_ids:
            return jsonify({'error': 'No photos selected'}), 400
        
        # Get photo count
        photo_count = len(photo_ids)
        if photo_count == 0:
            return jsonify({'error': 'No photos selected'}), 400
        
        # Calculate total amount in cents
        total_amount = photo_count * PHOTO_PRICE_CENTS
        
        # Verify photos belong to user
        # First, try to find photos that belong to the user
        photos = EnhancedImage.query.filter(
            EnhancedImage.id.in_(photo_ids),
            EnhancedImage.user_id == current_user.id
        ).all()
        
        # If some photos are missing, check for photos with user_id=None (created before login)
        # and link them to the current user if they were created recently (within 1 hour)
        if len(photos) < photo_count:
            missing_ids = set(photo_ids) - {p.id for p in photos}
            from datetime import timedelta
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            # Find unlinked photos created recently
            unlinked_photos = EnhancedImage.query.filter(
                EnhancedImage.id.in_(list(missing_ids)),
                EnhancedImage.user_id == None,
                EnhancedImage.created_at >= one_hour_ago
            ).all()
            
            # Link these photos to the current user
            if unlinked_photos:
                for photo in unlinked_photos:
                    photo.user_id = current_user.id
                    logger.info(f"Linking photo {photo.id} to user {current_user.id} (created before login)")
                db.session.commit()
                
                # Re-query to get all photos including newly linked ones
                photos = EnhancedImage.query.filter(
                    EnhancedImage.id.in_(photo_ids),
                    EnhancedImage.user_id == current_user.id
                ).all()
        
        if len(photos) != photo_count:
            logger.warning(f"Payment attempt: User {current_user.id} requested {photo_count} photos but only {len(photos)} found/authorized. Photo IDs: {photo_ids}")
            return jsonify({'error': 'Some photos not found or unauthorized'}), 403
        
        # Check if user has free access - skip payment if they do
        if current_user.has_free_access:
            logger.info(f"User {current_user.id} has free access - skipping payment for {photo_count} photos")
            # Create a "free" payment record for tracking
            payment = Payment(
                user_id=current_user.id,
                stripe_session_id=f'free_access_{current_user.id}_{datetime.utcnow().timestamp()}',
                amount=0,
                currency='usd',
                photo_count=photo_count,
                photo_ids=json.dumps(photo_ids),
                status='completed'
            )
            payment.completed_at = datetime.utcnow()
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'free_access': True,
                'message': 'Free download granted'
            })
        
        # Create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Enhanced Photo Download ({photo_count} photo{"s" if photo_count > 1 else ""})',
                            'description': f'Download {photo_count} AI-enhanced photo{"s" if photo_count > 1 else ""}',
                        },
                        'unit_amount': PHOTO_PRICE_CENTS,
                    },
                    'quantity': photo_count,
                }],
                mode='payment',
                success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url + 'payment/cancel',
                customer_email=current_user.email,
                metadata={
                    'user_id': str(current_user.id),
                    'photo_count': str(photo_count),
                    'photo_ids': json.dumps(photo_ids)
                }
            )
            
            # Create payment record
            payment = Payment(
                user_id=current_user.id,
                stripe_session_id=checkout_session.id,
                amount=total_amount,
                currency='usd',
                photo_count=photo_count,
                photo_ids=json.dumps(photo_ids),
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            logger.info(f"Created checkout session {checkout_session.id} for user {current_user.id}, {photo_count} photos")
            
            return jsonify({
                'success': True,
                'sessionId': checkout_session.id,
                'url': checkout_session.url
            })
            
        except AttributeError as ae:
            # Handle case where stripe.checkout is None
            logger.error(f"AttributeError creating checkout session: {ae}")
            logger.error(f"stripe.checkout value: {stripe.checkout}")
            logger.error(f"stripe.api_key set: {bool(stripe.api_key)}")
            logger.error(f"Stripe version: {getattr(stripe, '__version__', 'unknown')}")
            return jsonify({'error': 'Payment system error. Stripe checkout module not available. Please contact support.'}), 500
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            return jsonify({'error': f'Payment processing error: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating payment session'}), 500

@app.route('/api/payment/check-status', methods=['POST'])
@login_required
def check_payment_status():
    """Check if payment for photos is completed"""
    try:
        data = request.get_json()
        photo_ids = data.get('photo_ids', [])
        session_id = data.get('session_id')
        
        if not photo_ids:
            return jsonify({'error': 'No photos specified'}), 400
        
        # Check if user has free access - grant access immediately
        if current_user.has_free_access:
            logger.info(f"User {current_user.id} has free access - granting download permission")
            return jsonify({
                'success': True,
                'paid': True,
                'free_access': True
            })
        
        # Check if payment exists and is completed
        if session_id:
            payment = Payment.query.filter_by(
                stripe_session_id=session_id,
                user_id=current_user.id
            ).first()
        else:
            # Find payment by photo IDs
            payment = Payment.query.filter_by(
                user_id=current_user.id,
                status='completed'
            ).order_by(Payment.completed_at.desc()).first()
            
            if payment:
                paid_photo_ids = json.loads(payment.photo_ids) if payment.photo_ids else []
                # Check if all requested photos are in the paid set
                if not all(pid in paid_photo_ids for pid in photo_ids):
                    payment = None
        
        if payment and payment.status == 'completed':
            return jsonify({
                'success': True,
                'paid': True,
                'payment_id': payment.id
            })
        else:
            return jsonify({
                'success': True,
                'paid': False
            })
            
    except Exception as e:
        logger.error(f"Error checking payment status: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while checking payment status'}), 500

@app.route('/payment/success')
@login_required
def payment_success():
    """Handle successful payment redirect"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session from Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            # Update payment status
            payment = Payment.query.filter_by(stripe_session_id=session_id).first()
            if payment and payment.status == 'pending':
                payment.status = 'completed'
                payment.stripe_payment_intent_id = checkout_session.payment_intent
                payment.completed_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Payment {session_id} marked as completed")
            
            # Get photo IDs from payment to pass to template for auto-download
            photo_ids = []
            if payment and payment.photo_ids:
                try:
                    photo_ids = json.loads(payment.photo_ids)
                except:
                    logger.warning(f"Could not parse photo_ids from payment: {payment.photo_ids}")
            
            # Get photo details for download
            photos_data = []
            if photo_ids:
                photos = EnhancedImage.query.filter(
                    EnhancedImage.id.in_(photo_ids),
                    EnhancedImage.user_id == current_user.id
                ).all()
                # Convert to JSON-serializable format
                photos_data = [{
                    'id': photo.id,
                    'enhanced_filename': photo.enhanced_filename
                } for photo in photos]
            
            # Store session_id in session for dashboard to check
            session['payment_success_session_id'] = session_id
            
            return render_template('payment_success.html', 
                                 session_id=session_id,
                                 payment=payment,
                                 photos_data=json.dumps(photos_data),
                                 photo_ids=json.dumps(photo_ids))
        except Exception as e:
            logger.error(f"Error processing payment success: {e}", exc_info=True)
            flash('Payment was successful, but there was an error processing it. Please contact support.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/payment/cancel')
@login_required
def payment_cancel():
    """Handle cancelled payment"""
    flash('Payment was cancelled. You can try again when ready.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/api/payment/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    # Check if Stripe is configured
    if not app.config['STRIPE_SECRET_KEY'] or not stripe.api_key:
        logger.error("Stripe not configured - webhook cannot be processed")
        return jsonify({'error': 'Payment system not configured'}), 500
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    if not app.config['STRIPE_WEBHOOK_SECRET']:
        logger.warning("Stripe webhook secret not configured")
        return jsonify({'error': 'Webhook not configured'}), 400
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        logger.error(f"Invalid payload in webhook: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature in webhook: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Update payment status
        payment = Payment.query.filter_by(stripe_session_id=session['id']).first()
        if payment and payment.status == 'pending':
            payment.status = 'completed'
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.completed_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Payment {session['id']} completed via webhook")
    
    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        payment = Payment.query.filter_by(stripe_session_id=session['id']).first()
        if payment:
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Payment {session['id']} succeeded via webhook")
    
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        payment = Payment.query.filter_by(stripe_session_id=session['id']).first()
        if payment:
            payment.status = 'failed'
            db.session.commit()
            logger.info(f"Payment {session['id']} failed via webhook")
    
    return jsonify({'status': 'success'}), 200

# Admin endpoint to manage free access
@app.route('/api/admin/set-free-access', methods=['POST'])
def set_free_access():
    """Set free access for a user by email or username. Requires ADMIN_SECRET_KEY."""
    try:
        admin_secret = os.getenv('ADMIN_SECRET_KEY', '')
        if not admin_secret:
            return jsonify({'error': 'Admin feature not configured'}), 500
        
        # Check for admin secret in request
        data = request.get_json() or {}
        provided_secret = data.get('admin_secret') or request.headers.get('X-Admin-Secret')
        
        if provided_secret != admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        
        email = data.get('email')
        username = data.get('username')
        has_free_access = data.get('has_free_access', True)
        
        if not email and not username:
            return jsonify({'error': 'Email or username is required'}), 400
        
        # Case-insensitive lookup by email or username
        from sqlalchemy import func
        user = None
        
        if email:
            user = User.query.filter(func.lower(User.email) == func.lower(email)).first()
        
        if not user and username:
            user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
        
        if not user:
            identifier = email or username
            return jsonify({'error': f'User not found: {identifier}'}), 404
        
        user.has_free_access = bool(has_free_access)
        db.session.commit()
        
        identifier = email or username
        logger.info(f"Updated free access for user {user.email} (username: {user.username}, ID: {user.id}) to {has_free_access}")
        
        return jsonify({
            'success': True,
            'message': f'Free access {"enabled" if has_free_access else "disabled"} for {identifier}',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'has_free_access': user.has_free_access
            }
        })
    except Exception as e:
        logger.error(f"Error setting free access: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    # Production: Use environment variable for port, default to 5000
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
