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
from datetime import datetime
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from image_enhancer import ImageEnhancer
from models import db, User, EnhancedImage, Payment
import stripe

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

app = Flask(__name__, static_folder='static', template_folder='.')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///airbnb_enhancer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google Tag Manager Configuration
app.config['GTM_CONTAINER_ID'] = os.getenv('GTM_CONTAINER_ID', '')

# Stripe Configuration
app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
app.config['STRIPE_SECRET_KEY'] = os.getenv('STRIPE_SECRET_KEY', '')
app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')

# Initialize Stripe
if app.config['STRIPE_SECRET_KEY']:
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Price per photo in cents ($0.10 = 10 cents)
PHOTO_PRICE_CENTS = 10

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

# Create database tables
with app.app_context():
    db.create_all()

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
        
        # Log the user in
        login_user(user, remember=True)
        logger.info(f"User {user.username} logged in via Google OAuth")
        
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
    # Allow authenticated users to access home page (they might have pending images)
    return render_template('home.html')

@app.route('/api/check-auth')
def check_auth():
    """Check if user is authenticated"""
    return jsonify({'authenticated': current_user.is_authenticated})

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/dashboard')
@login_required
def dashboard():
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
        
        # Save photo records to database with transaction
        try:
            enhanced_image_record = EnhancedImage(
                user_id=current_user.id if current_user.is_authenticated else None,
                original_filename=filename,
                original_path=original_path,
                original_file_size=original_file_size,
                enhanced_filename=enhanced_filename,
                enhanced_path=enhanced_path,
                enhanced_file_size=enhanced_file_size,
                change_intensity=change_intensity,
                detail_level=detail_level,
                enhancement_settings=json.dumps(enhancements) if enhancements else None,
                ai_analysis=enhancements.get('response', '') if enhancements else None
            )
            
            db.session.add(enhanced_image_record)
            
            # Update user's processed images count if logged in
            if current_user.is_authenticated:
                current_user.images_processed += 1
            
            db.session.commit()
            logger.info(f"Image enhanced successfully: {filename} (ID: {enhanced_image_record.id})")
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error during image save: {db_error}", exc_info=True)
            # Clean up files if database save failed
            if os.path.exists(original_path):
                os.remove(original_path)
            if os.path.exists(enhanced_path):
                os.remove(enhanced_path)
            return jsonify({'error': 'Failed to save image record. Please try again.'}), 500
        
        # Convert to base64 for response
        with open(original_path, 'rb') as f:
            original_data = base64.b64encode(f.read()).decode('utf-8')
            original_url = f"data:image/{filename.rsplit('.', 1)[1]};base64,{original_data}"
        
        with open(enhanced_path, 'rb') as f:
            enhanced_data = base64.b64encode(f.read()).decode('utf-8')
            enhanced_url = f"data:image/jpeg;base64,{enhanced_data}"
        
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
        
        photos = [photo.to_dict() for photo in pagination.items]
        
        return jsonify({
            'success': True,
            'photos': photos,
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
        
        # Check if file exists
        if not os.path.exists(photo.original_path):
            return jsonify({'error': 'Original image not found'}), 404
        
        return send_file(photo.original_path, mimetype='image/jpeg')
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
        
        # Check if file exists
        if not os.path.exists(photo.enhanced_path):
            return jsonify({'error': 'Enhanced image not found'}), 404
        
        return send_file(photo.enhanced_path, mimetype='image/jpeg')
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
    try:
        if not app.config['STRIPE_SECRET_KEY']:
            return jsonify({'error': 'Stripe is not configured'}), 500
        
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
        photos = EnhancedImage.query.filter(
            EnhancedImage.id.in_(photo_ids),
            EnhancedImage.user_id == current_user.id
        ).all()
        
        if len(photos) != photo_count:
            return jsonify({'error': 'Some photos not found or unauthorized'}), 403
        
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
            
            return render_template('payment_success.html', 
                                 session_id=session_id,
                                 payment=payment)
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

if __name__ == '__main__':
    # Production: Use environment variable for port, default to 5000
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
