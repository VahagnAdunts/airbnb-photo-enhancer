from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # Google OAuth ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images_processed = db.Column(db.Integer, default=0)
    has_free_access = db.Column(db.Boolean, default=False, nullable=False)  # Allows free downloads without payment
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # Admin access flag
    
    # Relationship to enhanced images
    enhanced_images = db.relationship('EnhancedImage', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class EnhancedImage(db.Model):
    """Model to store metadata for both original and enhanced photos"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Original image information
    original_filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(500), nullable=False)
    original_file_size = db.Column(db.Integer)  # in bytes
    
    # Enhanced image information
    enhanced_filename = db.Column(db.String(255), nullable=False)
    enhanced_path = db.Column(db.String(500), nullable=False)
    enhanced_file_size = db.Column(db.Integer)  # in bytes
    
    # Store images as base64 in database for persistence across deployments
    # These columns are nullable to support existing databases
    original_image_data = db.Column(db.Text, nullable=True)  # Base64 encoded original image
    enhanced_image_data = db.Column(db.Text, nullable=True)  # Base64 encoded enhanced image
    
    # Enhancement settings and metadata
    conversion_type = db.Column(db.String(20), default='enhancement')  # 'enhancement' or 'night_conversion'
    change_intensity = db.Column(db.String(20), default='moderate')  # minimal, moderate, extensive
    detail_level = db.Column(db.String(20), default='moderate')  # minimal, moderate, extensive
    enhancement_settings = db.Column(db.Text)  # JSON string of enhancement details
    ai_analysis = db.Column(db.Text)  # AI analysis/response from AI service
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'original_path': self.original_path,
            'original_file_size': self.original_file_size,
            'enhanced_filename': self.enhanced_filename,
            'enhanced_path': self.enhanced_path,
            'enhanced_file_size': self.enhanced_file_size,
            'conversion_type': self.conversion_type,
            'change_intensity': self.change_intensity,
            'detail_level': self.detail_level,
            'enhancement_settings': json.loads(self.enhancement_settings) if self.enhancement_settings else None,
            'ai_analysis': self.ai_analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<EnhancedImage {self.original_filename} -> {self.enhanced_filename}>'


class Payment(db.Model):
    """Model to track Stripe payments for photo downloads"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    stripe_session_id = db.Column(db.String(255), unique=True, nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, cancelled
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    currency = db.Column(db.String(3), default='usd')
    photo_count = db.Column(db.Integer, nullable=False)
    photo_ids = db.Column(db.Text)  # JSON array of photo IDs included in payment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='payments')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stripe_session_id': self.stripe_session_id,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'status': self.status,
            'amount': self.amount,
            'currency': self.currency,
            'photo_count': self.photo_count,
            'photo_ids': json.loads(self.photo_ids) if self.photo_ids else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.stripe_session_id} - {self.status}>'


