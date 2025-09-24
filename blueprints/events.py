from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import *
from datetime import datetime

events = Blueprint('events', __name__)

@events.route('/')
@login_required
def list_events():
    """List events based on user's access level"""
    if current_user.role_type == RoleType.GENERAL_MEMBER:
        flash('Access denied. Events are for staff members only.', 'error')
        return redirect(url_for('core.home'))
    
    # Filter events based on user's jurisdiction
    query = Event.query
    
    if current_user.role_type == RoleType.WARD_LEADER:
        query = query.filter(
            (Event.scope == 'state') |
            (Event.zone_id == current_user.zone_id) |
            (Event.lga_id == current_user.lga_id) |
            (Event.ward_id == current_user.ward_id)
        )
    elif current_user.role_type == RoleType.LGA_LEADER:
        query = query.filter(
            (Event.scope == 'state') |
            (Event.zone_id == current_user.zone_id) |
            (Event.lga_id == current_user.lga_id)
        )
    elif current_user.role_type == RoleType.ZONAL_COORDINATOR:
        query = query.filter(
            (Event.scope == 'state') |
            (Event.zone_id == current_user.zone_id)
        )
    
    events = query.order_by(Event.event_date.desc()).all()
    
    # Categorize events
    upcoming_events = [e for e in events if e.event_date >= datetime.utcnow()]
    past_events = [e for e in events if e.event_date < datetime.utcnow()]
    
    return render_template('events/list.html', 
                         upcoming_events=upcoming_events, 
                         past_events=past_events)

@events.route('/manage')
@login_required
def manage():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE, RoleType.ZONAL_COORDINATOR, RoleType.LGA_LEADER, RoleType.WARD_LEADER]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    # Get events based on user's scope
    query = Event.query
    
    if current_user.role_type == RoleType.ZONAL_COORDINATOR:
        query = query.filter_by(zone_id=current_user.zone_id)
    elif current_user.role_type == RoleType.LGA_LEADER:
        query = query.filter_by(lga_id=current_user.lga_id)
    elif current_user.role_type == RoleType.WARD_LEADER:
        query = query.filter_by(ward_id=current_user.ward_id)
    
    events = query.order_by(Event.event_date.desc()).all()
    return render_template('events/manage.html', events=events)

@events.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE, RoleType.ZONAL_COORDINATOR, RoleType.LGA_LEADER, RoleType.WARD_LEADER]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    if request.method == 'POST':
        event = Event(
            title=request.form['title'],
            description=request.form.get('description', ''),
            location=request.form['location'],
            event_date=datetime.strptime(request.form['event_date'], '%Y-%m-%dT%H:%M'),
            created_by_id=current_user.id,
            scope=request.form['scope']
        )
        
        # Set scope-specific IDs based on current user's role and scope
        if event.scope == 'zone' and current_user.zone_id:
            event.zone_id = current_user.zone_id
        elif event.scope == 'lga' and current_user.lga_id:
            event.lga_id = current_user.lga_id
        elif event.scope == 'ward' and current_user.ward_id:
            event.ward_id = current_user.ward_id
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully.', 'success')
        return redirect(url_for('events.manage'))
    
    return render_template('events/create.html')