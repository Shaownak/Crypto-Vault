# 🔐 Crypto Vault

A secure, encrypted messaging platform built with Flask that allows users to share messages with end-to-end encryption. All user data and messages are encrypted before being stored in the database, ensuring maximum privacy and security.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-v3.1.1-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🔒 Security & Privacy
- **End-to-End Encryption**: All messages and user data encrypted using Fernet (AES 128)
- **Secure Password Hashing**: Passwords hashed with bcrypt
- **Session Management**: Secure session handling with Flask sessions
- **Data Protection**: No plain text storage of sensitive information

### 👤 User Management
- **User Registration & Authentication**: Secure account creation and login
- **Profile Management**: Update passwords and view account statistics
- **User Search**: Find and connect with other users on the platform

### 💬 Messaging System
- **Encrypted Posts**: Create and share encrypted messages
- **Like System**: Like and interact with posts from other users
- **Real-time Updates**: Dynamic content loading and updates
- **Message Search**: Search through encrypted messages (when decrypted)

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first, responsive web interface
- **Custom Color Palette**: Beautiful design with custom colors (#F5F7F8, #F4CE14, #495E57, #45474B)
- **Glass Morphism**: Modern glass effect design elements
- **Smooth Animations**: Engaging transitions and hover effects
- **Dark/Light Theme Support**: Clean, modern interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Crypto
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📋 Dependencies

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
cryptography==41.0.7
bcrypt==4.1.2
```

## 🏗️ Project Structure

```
Crypto/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── encryption.key        # Encryption key (auto-generated)
├── database.db           # SQLite database
├── instance/
│   └── database.db       # Instance-specific database
├── migrations/           # Database migration files
├── static/
│   └── css/
│       └── style.css     # Custom CSS with modern design
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # Main dashboard
│   ├── profile.html     # User profile
│   ├── search.html      # Search interface
│   └── ...
└── README.md            # Project documentation
```

## 🔧 Configuration

### Environment Variables
The application uses the following configuration:
- **SECRET_KEY**: Automatically generated random key for session security
- **DATABASE_URI**: SQLite database path (configurable)
- **ENCRYPTION_KEY**: Auto-generated Fernet key for data encryption

### Database Schema
The application uses two main models:

**User Model:**
- `id`: Primary key
- `username`: Unique username
- `password`: Bcrypt hashed password
- `encrypted_info`: Encrypted user information
- `created_at`: Account creation timestamp

**Post Model:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `encrypted_message`: Encrypted message content
- `likes`: Number of likes
- `created_at`: Post creation timestamp

## 🛡️ Security Features

### Encryption Implementation
- **Algorithm**: AES encryption via Fernet (symmetric encryption)
- **Key Management**: Automatic key generation and secure storage
- **Data Protection**: All sensitive data encrypted before database storage

### Password Security
- **Hashing**: bcrypt with salt for password storage
- **Validation**: Strong password requirements
- **Session Security**: Secure session management

### Input Validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping prevents cross-site scripting
- **Input Sanitization**: Server-side validation of all user inputs

## 📱 Features Overview

### Authentication System
- **Registration**: Create new accounts with encrypted user data
- **Login**: Secure authentication with session management
- **Logout**: Proper session cleanup

### Dashboard
- **Post Creation**: Create encrypted messages
- **Feed**: View posts from all users
- **Interaction**: Like posts and view engagement

### Profile Management
- **Statistics**: View account statistics and activity
- **Password Update**: Change account passwords securely
- **Account Info**: View encrypted account information

### Search Functionality
- **User Search**: Find users by username
- **Message Search**: Search through decrypted message content
- **Results Display**: Clean, organized search results

## 🎨 Design System

### Color Palette
- **Primary Background**: #F5F7F8 (Light Gray)
- **Accent Color**: #F4CE14 (Golden Yellow)
- **Secondary**: #495E57 (Dark Green)
- **Text Color**: #45474B (Dark Gray)

### UI Components
- **Cards**: Glass morphism effect with backdrop blur
- **Buttons**: Gradient backgrounds with hover animations
- **Forms**: Modern input styling with focus states
- **Navigation**: Clean, responsive navigation bar

## 🔄 API Endpoints

### Authentication
- `GET /` - Home/Login page
- `POST /login` - User authentication
- `GET /register` - Registration page
- `POST /register` - User registration
- `GET /logout` - Session logout

### Dashboard & Posts
- `GET /dashboard` - Main dashboard
- `POST /dashboard` - Create new post
- `POST /like/<post_id>` - Like/unlike posts
- `POST /delete/<post_id>` - Delete posts

### User Management
- `GET /profile` - User profile page
- `GET /update_password` - Password update page
- `POST /update_password` - Update password
- `GET /search` - Search interface
- `POST /search` - Perform search

## 🧪 Development & Testing

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Database Migrations
```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade if needed
flask db downgrade
```

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set secure SECRET_KEY in production
2. **Database**: Consider PostgreSQL for production use
3. **HTTPS**: Always use HTTPS in production
4. **Key Management**: Secure encryption key storage
5. **Backup**: Regular database backups

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```



**Built with ❤️ using Flask, SQLAlchemy, and modern web technologies.**
