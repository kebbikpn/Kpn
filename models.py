from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import enum
import secrets
import hashlib

class RoleType(enum.Enum):
    ADMIN = "admin"
    ICT_ADMIN = "ict_admin"
    EXECUTIVE = "executive"
    AUDITOR_GENERAL = "auditor_general"
    ZONAL_COORDINATOR = "zonal_coordinator"
    LGA_LEADER = "lga_leader"
    WARD_LEADER = "ward_leader"
    GENERAL_MEMBER = "general_member"

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ActionType(enum.Enum):
    WARNING = "warning"
    SUSPENSION = "suspension"
    DISMISSAL = "dismissal"
    REPRIMAND = "reprimand"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(255))
    
    # Role and hierarchy
    role_type = db.Column(db.Enum(RoleType), default=RoleType.GENERAL_MEMBER)
    role_title = db.Column(db.String(100))
    approval_status = db.Column(db.Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    
    # Location assignment
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    lga_id = db.Column(db.Integer, db.ForeignKey('lgas.id'))
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'))
    
    # Facebook integration
    facebook_user_id = db.Column(db.String(100))
    facebook_verified = db.Column(db.Boolean, default=False)
    facebook_follow_date = db.Column(db.DateTime)
    
    # Password reset fields
    reset_token = db.Column(db.String(255))
    reset_token_expires = db.Column(db.DateTime)
    
    # Profile edit tracking
    profile_edit_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    zone = db.relationship('Zone', backref='users')
    lga = db.relationship('LGA', backref='users')
    ward = db.relationship('Ward', backref='users')
    duty_logs = db.relationship('DutyLog', backref='user', lazy='dynamic')
    disciplinary_actions = db.relationship('DisciplinaryAction', foreign_keys='DisciplinaryAction.user_id', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate a secure password reset token"""
        token = secrets.token_urlsafe(32)
        # Hash the token for security
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self.reset_token = token_hash
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return token  # Return unhashed token for email
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash == self.reset_token
    
    def clear_reset_token(self):
        """Clear password reset token after use"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def get_location_hierarchy(self):
        """Get the full location hierarchy for this user"""
        location = []
        if self.ward:
            location.append(f"Ward: {self.ward.name}")
        if self.lga:
            location.append(f"LGA: {self.lga.name}")
        if self.zone:
            location.append(f"Zone: {self.zone.name}")
        return " | ".join(reversed(location))
    
    def can_edit_profile(self):
        """Check if user can still edit their profile (max 3 edits)"""
        return self.profile_edit_count < 3
    
    def increment_edit_count(self):
        """Increment the profile edit count"""
        self.profile_edit_count += 1
    
    def can_approve_user(self, target_user):
        """Check if this user can approve another user"""
        if self.role_type == RoleType.ADMIN:
            return True
        
        # State executives can approve zonal coordinators
        if (self.role_type == RoleType.EXECUTIVE and 
            target_user.role_type == RoleType.ZONAL_COORDINATOR):
            return True
        
        # Zonal coordinators can approve LGA leaders in their zone
        if (self.role_type == RoleType.ZONAL_COORDINATOR and 
            target_user.role_type == RoleType.LGA_LEADER and
            target_user.zone_id == self.zone_id):
            return True
        
        # LGA leaders can approve ward leaders in their LGA
        if (self.role_type == RoleType.LGA_LEADER and 
            target_user.role_type == RoleType.WARD_LEADER and
            target_user.lga_id == self.lga_id):
            return True
        
        return False

class Zone(db.Model):
    __tablename__ = 'zones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    lgas = db.relationship('LGA', backref='zone', lazy='dynamic')
    
    def get_coordinator(self):
        return User.query.filter_by(
            zone_id=self.id, 
            role_type=RoleType.ZONAL_COORDINATOR,
            role_title='Zonal Coordinator',
            approval_status=ApprovalStatus.APPROVED
        ).first()

class LGA(db.Model):
    __tablename__ = 'lgas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    
    # Relationships
    wards = db.relationship('Ward', backref='lga', lazy='dynamic')
    
    def get_coordinator(self):
        return User.query.filter_by(
            lga_id=self.id, 
            role_type=RoleType.LGA_LEADER,
            role_title='LGA Coordinator',
            approval_status=ApprovalStatus.APPROVED
        ).first()

class Ward(db.Model):
    __tablename__ = 'wards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    lga_id = db.Column(db.Integer, db.ForeignKey('lgas.id'), nullable=False)
    
    def get_coordinator(self):
        return User.query.filter_by(
            ward_id=self.id, 
            role_type=RoleType.WARD_LEADER,
            role_title='Ward Coordinator',
            approval_status=ApprovalStatus.APPROVED
        ).first()

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='campaigns')

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    event_date = db.Column(db.DateTime, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Scope (state, zone, lga, ward)
    scope = db.Column(db.String(20), default='state')
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    lga_id = db.Column(db.Integer, db.ForeignKey('lgas.id'))
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', backref='events_created')

class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # photo, video
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_by = db.relationship('User', backref='media_uploads')

class DutyLog(db.Model):
    __tablename__ = 'duty_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duty_description = db.Column(db.Text, nullable=False)
    completion_status = db.Column(db.String(20), default='pending')  # pending, completed, overdue
    due_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DisciplinaryAction(db.Model):
    __tablename__ = 'disciplinary_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # warning, suspension, removal
    reason = db.Column(db.Text, nullable=False)
    issued_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    issued_by = db.relationship('User', foreign_keys=[issued_by_id], backref='disciplinary_actions_issued')

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    """Comprehensive activity tracking for all member actions"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # facebook_like, duty_completed, event_attended, etc.
    activity_description = db.Column(db.Text, nullable=False)
    points_earned = db.Column(db.Integer, default=0)  # Scoring system for activities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional foreign keys for related objects
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'))
    duty_log_id = db.Column(db.Integer, db.ForeignKey('duty_logs.id'))
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    campaign = db.relationship('Campaign', backref='activity_logs')
    event = db.relationship('Event', backref='activity_logs')
    media = db.relationship('Media', backref='activity_logs')
    duty_log = db.relationship('DutyLog', backref='activity_logs')

class FacebookEngagement(db.Model):
    """Track Facebook engagement activities"""
    __tablename__ = 'facebook_engagements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    engagement_type = db.Column(db.String(20), nullable=False)  # like, comment, share, react
    post_id = db.Column(db.String(100))  # Facebook post ID
    post_url = db.Column(db.String(255))
    engagement_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)  # Whether engagement was verified via API
    
    # Relationships
    user = db.relationship('User', backref='facebook_engagements')

class MemberStats(db.Model):
    """Pre-calculated member statistics for performance"""
    __tablename__ = 'member_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, default=0)
    duties_completed = db.Column(db.Integer, default=0)
    duties_overdue = db.Column(db.Integer, default=0)
    facebook_engagements = db.Column(db.Integer, default=0)
    events_attended = db.Column(db.Integer, default=0)
    campaigns_participated = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime)
    activity_score = db.Column(db.Float, default=0.0)  # Overall activity rating
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('member_stats', uselist=False))