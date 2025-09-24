from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import *
from werkzeug.utils import secure_filename
from datetime import datetime
import os

media = Blueprint('media', __name__)

@media.route('/')
def gallery():
    # Use cached media gallery data for better performance
    from utils.cache_utils import get_media_gallery_data
    media_data = get_media_gallery_data()
    return render_template('media/gallery.html', photos=media_data['photos'], videos=media_data['videos'])

@media.route('/manage')
@login_required
def manage():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    media_files = Media.query.order_by(Media.created_at.desc()).all()
    return render_template('media/manage.html', media_files=media_files)

@media.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role_type not in [RoleType.ADMIN, RoleType.EXECUTIVE]:
        flash('Access denied.', 'error')
        return redirect(url_for('core.home'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        file_type = request.form['file_type']
        public = request.form.get('public') == 'on'
        
        # Handle file upload
        uploaded_file = request.files.get('media_file')
        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.filename}")
            
            # Create upload directory
            upload_dir = f"static/uploads/{file_type}s"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)
            
            # Create media record
            media_item = Media(
                title=title,
                description=description,
                file_path=f"uploads/{file_type}s/{filename}",
                file_type=file_type,
                uploaded_by_id=current_user.id,
                public=public
            )
            
            db.session.add(media_item)
            db.session.commit()
            
            flash('Media uploaded successfully.', 'success')
            return redirect(url_for('media.manage'))
        else:
            flash('Please select a file to upload.', 'error')
    
    return render_template('media/upload.html')