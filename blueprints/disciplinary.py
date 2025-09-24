from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, DisciplinaryAction, RoleType
from datetime import datetime

disciplinary = Blueprint('disciplinary', __name__)

def can_manage_action(user, action):
    """Check if user can manage a disciplinary action"""
    if user.role_type == RoleType.ADMIN:
        return True
    elif user.role_type == RoleType.EXECUTIVE:
        return True
    elif user.id == action.issued_by_id:
        return True
    else:
        return False

def determine_scope(user):
    """Determine the scope of disciplinary action based on user role"""
    if user.role_type == RoleType.ADMIN:
        return 'STATE'
    elif user.role_type == RoleType.EXECUTIVE:
        return 'STATE'
    elif user.role_type == RoleType.ZONAL_COORDINATOR:
        return 'ZONE'
    elif user.role_type == RoleType.LGA_LEADER:
        return 'LGA'
    elif user.role_type == RoleType.WARD_LEADER:
        return 'WARD'
    else:
        return 'GENERAL'

@disciplinary.route('/')
@login_required
def view_actions():
    """View disciplinary actions"""
    # Only certain roles can view disciplinary actions
    if current_user.role_type == RoleType.GENERAL_MEMBER:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    # Get actions based on user's role and jurisdiction
    if current_user.role_type == RoleType.ADMIN:
        # Admins see all actions
        actions = DisciplinaryAction.query.order_by(DisciplinaryAction.created_at.desc()).all()
    elif current_user.role_type == RoleType.EXECUTIVE:
        # Executives see state-level actions
        actions = DisciplinaryAction.query.order_by(DisciplinaryAction.created_at.desc()).all()
    elif current_user.role_type == RoleType.ZONAL_COORDINATOR:
        # Zonal coordinators see actions in their zone
        actions = DisciplinaryAction.query.join(User).filter(
            User.zone_id == current_user.zone_id
        ).order_by(DisciplinaryAction.created_at.desc()).all()
    elif current_user.role_type == RoleType.LGA_LEADER:
        # LGA leaders see actions in their LGA
        actions = DisciplinaryAction.query.join(User).filter(
            User.lga_id == current_user.lga_id
        ).order_by(DisciplinaryAction.created_at.desc()).all()
    elif current_user.role_type == RoleType.WARD_LEADER:
        # Ward leaders see actions in their ward
        actions = DisciplinaryAction.query.join(User).filter(
            User.ward_id == current_user.ward_id
        ).order_by(DisciplinaryAction.created_at.desc()).all()
    else:
        actions = []
    
    # Calculate statistics
    stats = {
        'total': len(actions),
        'warnings': len([a for a in actions if a.action_type == 'warning']),
        'suspensions': len([a for a in actions if a.action_type == 'suspension']),
        'dismissals': len([a for a in actions if a.action_type == 'dismissal']),
        'active': len([a for a in actions if a.status == 'active']),
        'resolved': len([a for a in actions if a.status == 'resolved'])
    }
    
    return render_template('disciplinary/list.html', disciplinary_actions=actions, stats=stats)

@disciplinary.route('/create', methods=['GET', 'POST'])
@login_required
def create_action():
    """Create a new disciplinary action"""
    # Only certain roles can create disciplinary actions
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE]:
        flash('You do not have permission to create disciplinary actions.', 'error')
        return redirect(url_for('disciplinary.view_actions'))
    
    if request.method == 'POST':
        user_id = request.form['user_id']
        action_type = request.form['action_type']
        reason = request.form['reason']
        
        # Create disciplinary action  
        action = DisciplinaryAction(
            user_id=user_id,
            issued_by_id=current_user.id,
            action_type=action_type,
            reason=reason,
            status='active'
        )
        
        db.session.add(action)
        db.session.commit()
        
        flash('Disciplinary action created successfully.', 'success')
        return redirect(url_for('disciplinary.view_actions'))
    
    # GET request - show form
    # Get users based on current user's jurisdiction
    if current_user.role_type == RoleType.ADMIN:
        users = User.query.filter(User.role_type != RoleType.ADMIN).all()
    elif current_user.role_type == RoleType.EXECUTIVE:
        users = User.query.filter(User.role_type.in_([
            RoleType.ZONAL_COORDINATOR, RoleType.LGA_LEADER, 
            RoleType.WARD_LEADER, RoleType.GENERAL_MEMBER
        ])).all()
    else:
        users = []
    
    return render_template('disciplinary/create.html', users=users)

@disciplinary.route('/resolve/<int:action_id>', methods=['POST'])
@login_required
def resolve_action(action_id):
    """Mark a disciplinary action as resolved"""
    action = DisciplinaryAction.query.get_or_404(action_id)
    
    # Check if user can resolve this action
    if not can_manage_action(current_user, action):
        flash('You do not have permission to resolve this action.', 'error')
        return redirect(url_for('disciplinary.view_actions'))
    
    action.status = 'resolved'
    action.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Disciplinary action marked as resolved.', 'success')
    return redirect(url_for('disciplinary.view_actions'))