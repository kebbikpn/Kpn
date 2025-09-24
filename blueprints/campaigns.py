from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import *

campaigns = Blueprint('campaigns', __name__)

@campaigns.route('/')
def list_campaigns():
    campaigns = Campaign.query.filter_by(published=True).order_by(Campaign.created_at.desc()).all()
    return render_template('campaigns/list.html', campaigns=campaigns)

@campaigns.route('/<int:campaign_id>')
def view_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if not campaign.published:
        flash('Campaign not found.', 'error')
        return redirect(url_for('campaigns.list_campaigns'))
    
    return render_template('campaigns/view.html', campaign=campaign)

@campaigns.route('/manage')
@login_required
def manage():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template('campaigns/manage.html', campaigns=campaigns)

@campaigns.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    if request.method == 'POST':
        campaign = Campaign(
            title=request.form['title'],
            content=request.form['content'],
            author_id=current_user.id,
            published=request.form.get('published') == 'on',
            featured=request.form.get('featured') == 'on'
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        flash('Campaign created successfully.', 'success')
        return redirect(url_for('campaigns.manage'))
    
    return render_template('campaigns/create.html')