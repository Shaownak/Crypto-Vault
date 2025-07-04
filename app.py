from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import bcrypt
import os
from flask_migrate import Migrate
from datetime import datetime
import re

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
# Use absolute path for the database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Key Management Module
key_file = 'encryption.key'

if not os.path.exists(key_file):
    with open(key_file, 'wb') as f:
        f.write(Fernet.generate_key())

with open(key_file, 'rb') as f:
    key = f.read()

cipher_suite = Fernet(key)


# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    encrypted_info = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    encrypted_message = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Validation functions
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Valid password"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid username"


# Credential Check Function
def check_credentials(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return user
    return None


# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        user_info = request.form.get('info', '').strip()
        
        # Validation
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            flash(username_msg, 'error')
            return render_template('register_simple.html'), 400

        password_valid, password_msg = validate_password(password)
        if not password_valid:
            flash(password_msg, 'error')
            return render_template('register_simple.html'), 400

        if password != confirm_password:
            flash("Passwords don't match", 'error')
            return render_template('register_simple.html'), 400

        if not user_info:
            flash("Please provide some personal information", 'error')
            return render_template('register_simple.html'), 400

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", 'error')
            return render_template('register_simple.html'), 409

        try:
            # Hash and salt the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Encrypt user info
            encrypted_info = cipher_suite.encrypt(user_info.encode('utf-8'))
            
            # Save to database
            new_user = User(username=username, password=hashed_password, encrypted_info=encrypted_info)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register_simple.html'), 500

    return render_template('register_simple.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('login.html'), 400

        user = check_credentials(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html'), 403

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    # Handle new post submission
    if request.method == 'POST':
        message = request.form.get('message', '').strip()

        if not message:
            flash('Message cannot be empty', 'error')
        elif len(message) > 1000:
            flash('Message is too long (max 1000 characters)', 'error')
        else:
            try:
                # Encrypt the message
                encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))

                # Save the post to the database
                new_post = Post(user_id=user.id, encrypted_message=encrypted_message)
                db.session.add(new_post)
                db.session.commit()
                flash('Post created successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error creating post. Please try again.', 'error')

        return redirect(url_for('dashboard'))

    # Fetch and decrypt posts for the current user
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    decrypted_posts = []
    for post in posts:
        try:
            decrypted_message = cipher_suite.decrypt(post.encrypted_message).decode('utf-8')
            decrypted_posts.append({
                'id': post.id, 
                'message': decrypted_message, 
                'likes': post.likes,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
            })
        except Exception as e:
            decrypted_posts.append({
                'id': post.id, 
                'message': "[Error: Unable to decrypt message]", 
                'likes': post.likes,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else 'Unknown'
            })

    return render_template('dashboard.html', user=user, posts=decrypted_posts)


@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_info = request.form.get('new_info', '').strip()

        if not new_info:
            flash('Profile information cannot be empty', 'error')
        elif len(new_info) > 500:
            flash('Profile information is too long (max 500 characters)', 'error')
        else:
            try:
                # Encrypt the updated user info
                encrypted_info = cipher_suite.encrypt(new_info.encode('utf-8'))

                # Update the user's info in the database
                user.encrypted_info = encrypted_info
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile. Please try again.', 'error')

        return redirect(url_for('profile'))

    # Decrypt the user's info for display
    try:
        decrypted_info = cipher_suite.decrypt(user.encrypted_info).decode('utf-8')
    except Exception as e:
        decrypted_info = "[Error: Unable to decrypt profile information]"
        flash('Error decrypting profile information', 'error')

    # Get user statistics
    post_count = Post.query.filter_by(user_id=user.id).count()
    total_likes = db.session.query(db.func.sum(Post.likes)).filter_by(user_id=user.id).scalar() or 0

    return render_template('profile.html', user=user, info=decrypted_info, 
                         post_count=post_count, total_likes=total_likes)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please log in'}), 401
        flash('Please log in to delete posts', 'error')
        return redirect(url_for('login'))

    post = Post.query.filter_by(id=post_id, user_id=session['user_id']).first()
    if not post:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Post not found'}), 404
        flash('Post not found', 'error')
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(post)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Post deleted successfully'})
        
        flash('Post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Error deleting post'}), 500
        flash('Error deleting post', 'error')

    return redirect(url_for('dashboard'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        flash('Please log in to search your posts', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip().lower()

        if not search_query:
            flash('Please enter a search query', 'error')
            return render_template('search.html', user=user)

        if len(search_query) < 2:
            flash('Search query must be at least 2 characters long', 'error')
            return render_template('search.html', user=user)

        # Fetch all posts for the current user
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()

        # Filter and decrypt posts matching the search query
        matching_posts = []
        for post in posts:
            try:
                decrypted_message = cipher_suite.decrypt(post.encrypted_message).decode('utf-8')
                if search_query in decrypted_message.lower():
                    matching_posts.append({
                        'id': post.id,
                        'message': decrypted_message,
                        'likes': post.likes,
                        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
                    })
            except Exception as e:
                continue  # Skip posts that can't be decrypted

        if not matching_posts:
            flash(f'No posts found matching "{search_query}"', 'info')

        return render_template('search_results.html', user=user, posts=matching_posts, 
                             search_query=search_query, result_count=len(matching_posts))

    return render_template('search.html', user=user)


@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    if 'user_id' not in session:
        flash('Please log in to update your password', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('update_password.html', user=user)

        if new_password != confirm_password:
            flash("New passwords don't match", 'error')
            return render_template('update_password.html', user=user)

        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            flash(password_msg, 'error')
            return render_template('update_password.html', user=user)

        # Check if the current password matches
        if bcrypt.checkpw(current_password.encode('utf-8'), user.password):
            try:
                # Hash the new password and update it
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                user.password = hashed_password
                db.session.commit()
                flash('Password updated successfully!', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                db.session.rollback()
                flash('Error updating password. Please try again.', 'error')
                return render_template('update_password.html', user=user)
        else:
            flash('Current password is incorrect', 'error')
            return render_template('update_password.html', user=user)

    return render_template('update_password.html', user=user)


@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Please log in'}), 401
        flash('Please log in to like posts', 'error')
        return redirect(url_for('login'))

    post = Post.query.filter_by(id=post_id, user_id=session['user_id']).first()
    if not post:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Post not found'}), 404
        flash('Post not found', 'error')
        return redirect(url_for('dashboard'))

    try:
        # Increment the likes count
        post.likes += 1
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'likes': post.likes})
        
        flash('Post liked!', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Error liking post'}), 500
        flash('Error liking post', 'error')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
