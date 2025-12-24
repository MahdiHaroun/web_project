from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from typing import Optional

# VULNERABLE: Information Disclosure via Backup Files and robots.txt

app = FastAPI(title="E-Commerce Site - Vulnerable")

# Simulated user credentials (in real app, would be in database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "SuperSecret123!AdminPass"


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Commerce Site - Vulnerable</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 { color: #333; }
            .vulnerability {
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }
            .test-section {
                background: #f8d7da;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #dc3545;
            }
            a {
                display: inline-block;
                margin: 10px 5px;
                padding: 10px 20px;
                background: #dc3545;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            a:hover {
                background: #c82333;
            }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛒 E-Commerce Site (Vulnerable)</h1>
            
            <div class="vulnerability">
                <h3>Vulnerability: Information Disclosure via Backup Files</h3>
                <p><strong>Description:</strong></p>
                <ul>
                    <li>robots.txt reveals sensitive directories</li>
                    <li>Backup files are publicly accessible</li>
                    <li>Backup files contain passwords and credentials</li>
                    <li>Database dumps exposed</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔍 How to Exploit:</h3>
                <ol>
                    <li>Visit <code>/robots.txt</code> to find disallowed paths</li>
                    <li>Check for backup files mentioned in robots.txt</li>
                    <li>Access backup files to extract credentials</li>
                    <li>Use credentials to access admin panel</li>
                </ol>
                
                <h4>Try these URLs:</h4>
                <a href="/robots.txt" target="_blank">View robots.txt</a>
                <a href="/backup/config.php.bak" target="_blank">config.php.bak</a>
                <a href="/backup/database_backup.sql" target="_blank">database_backup.sql</a>
                <a href="/backup/.env.backup" target="_blank">.env.backup</a>
            </div>
            
            <h3>Public Pages:</h3>
            <a href="/shop" style="background: #667eea;">Shop</a>
            <a href="/products" style="background: #667eea;">Products</a>
        </div>
    </body>
    </html>
    """


# VULNERABLE: robots.txt revealing sensitive files and directories
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return """# robots.txt
User-agent: *
Disallow: /admin/
Disallow: /backup/
Disallow: /config/
Disallow: /database/
Disallow: /.git/
Disallow: /temp/

# VULNERABLE: Comments revealing backup locations
# Backup files location: /backup/
# Database backups: /backup/database_backup.sql
# Config backups: /backup/config.php.bak
# Environment backup: /backup/.env.backup
# Old admin passwords: /backup/passwords.txt

# Note: Remember to remove backup files before going live!
# Admin panel: /admin/login (password in config.php.bak)
"""


# VULNERABLE: Publicly accessible backup file with credentials
@app.get("/backup/config.php.bak", response_class=PlainTextResponse)
async def config_backup():
    return f"""<?php
// Configuration Backup File
// Created: 2024-01-15
// WARNING: This file should be deleted!

// Database Configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'ecommerce_db');
define('DB_USER', 'db_admin');
define('DB_PASS', 'DbP@ssw0rd2024!_SecureDB');

// Admin Credentials
define('ADMIN_USER', '{ADMIN_USERNAME}');
define('ADMIN_PASS', '{ADMIN_PASSWORD}');

// API Keys
define('STRIPE_SECRET_KEY', 'sk_live_51HxKL9vN8pQ3rS5tU6vW7xY8zA9');
define('STRIPE_PUBLIC_KEY', 'pk_live_51HxKL9vN8pQ3rS5tU6vW7xY8zA9');

// AWS Credentials
define('AWS_ACCESS_KEY', 'AKIAIOSFODNN7EXAMPLE');
define('AWS_SECRET_KEY', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY');
define('S3_BUCKET', 'ecommerce-production-bucket');

// Email Configuration
define('SMTP_HOST', 'smtp.company.com');
define('SMTP_USER', 'noreply@company.com');
define('SMTP_PASS', 'EmailP@ss123!');

// Security Keys
define('SESSION_SECRET', 'a8f5f167f44f4964e6c998dee827110c');
define('ENCRYPTION_KEY', '2f0e4c4f-6265-4ad8-94b8-9f2b7f8c4e5d');

// Internal API
define('INTERNAL_API_KEY', 'internal_api_key_9x8c7v6b5n4m3');
define('INTERNAL_API_URL', 'http://api.internal.company.com');

?>
"""


# VULNERABLE: Database backup with user credentials
@app.get("/backup/database_backup.sql", response_class=PlainTextResponse)
async def database_backup():
    return f"""-- Database Backup
-- Date: 2024-01-15 14:30:00
-- Database: ecommerce_db
-- WARNING: Contains sensitive data!

-- Users Table
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    password_hash VARCHAR(255),
    email VARCHAR(100),
    role VARCHAR(20)
);

-- Admin user credentials
INSERT INTO users (id, username, password_hash, email, role) VALUES
(1, '{ADMIN_USERNAME}', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5OwDxUxm.XqKu', 'admin@company.com', 'admin');
-- Password: {ADMIN_PASSWORD}

-- Other users
INSERT INTO users (id, username, password_hash, email, role) VALUES
(2, 'john_doe', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'john@example.com', 'user'),
(3, 'jane_smith', '$2b$12$KIXZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'jane@example.com', 'user');

-- Products Table
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock INT
);

-- API Keys Table
CREATE TABLE api_keys (
    id INT PRIMARY KEY,
    service VARCHAR(50),
    api_key VARCHAR(255)
);

INSERT INTO api_keys (id, service, api_key) VALUES
(1, 'stripe', 'sk_live_51HxKL9vN8pQ3rS5tU6vW7xY8zA9'),
(2, 'sendgrid', 'SG.xxxxxxxxxxxxxxxxxxxxxxxxxxx'),
(3, 'aws', 'AKIAIOSFODNN7EXAMPLE');

-- Session tokens (active sessions)
CREATE TABLE sessions (
    token VARCHAR(255),
    user_id INT,
    expires TIMESTAMP
);

INSERT INTO sessions VALUES
('admin_session_token_abc123xyz', 1, '2024-12-31 23:59:59');

-- End of backup
"""


# VULNERABLE: Environment file backup with all secrets
@app.get("/backup/.env.backup", response_class=PlainTextResponse)
async def env_backup():
    return f"""# Environment Configuration Backup
# WARNING: Contains production secrets!

# Application
APP_NAME=ECommerce
APP_ENV=production
APP_DEBUG=false
APP_URL=https://www.company.com

# Database
DB_CONNECTION=mysql
DB_HOST=db.internal.company.com
DB_PORT=3306
DB_DATABASE=ecommerce_db
DB_USERNAME=db_admin
DB_PASSWORD=DbP@ssw0rd2024!_SecureDB

# Admin Credentials
ADMIN_USERNAME={ADMIN_USERNAME}
ADMIN_PASSWORD={ADMIN_PASSWORD}
ADMIN_EMAIL=admin@company.com

# Redis
REDIS_HOST=redis.internal.company.com
REDIS_PASSWORD=RedisP@ss123!
REDIS_PORT=6379

# Mail
MAIL_MAILER=smtp
MAIL_HOST=smtp.company.com
MAIL_PORT=587
MAIL_USERNAME=noreply@company.com
MAIL_PASSWORD=EmailP@ss123!
MAIL_ENCRYPTION=tls

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=ecommerce-production-bucket

# Stripe
STRIPE_KEY=pk_live_51HxKL9vN8pQ3rS5tU6vW7xY8zA9
STRIPE_SECRET=sk_live_51HxKL9vN8pQ3rS5tU6vW7xY8zA9

# JWT
JWT_SECRET=your-256-bit-secret-key-here-change-in-production
JWT_ALGO=HS256
JWT_EXPIRATION=3600

# Session
SESSION_DRIVER=redis
SESSION_LIFETIME=120
SESSION_SECRET=a8f5f167f44f4964e6c998dee827110c

# OAuth (Google)
GOOGLE_CLIENT_ID=123456789-abc123def456ghi789jkl.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-aBcDeFgHiJkLmNoPqRsTuVwXyZ
"""


@app.get("/shop")
async def shop():
    return {"message": "Shop page - Browse our products"}


@app.get("/products")
async def products():
    return {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999.99},
            {"id": 2, "name": "Mouse", "price": 29.99},
            {"id": 3, "name": "Keyboard", "price": 79.99}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
