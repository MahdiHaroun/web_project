from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from typing import Optional
import os
from dotenv import load_dotenv

# FIXED: Proper File Management Without Exposed Backups

app = FastAPI(title="E-Commerce Site - Secure")

# FIXED: Load credentials from environment variables
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Commerce Site - Secure</title>
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
            .security-fix {
                background: #d4edda;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #28a745;
            }
            .test-section {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #2196F3;
            }
            a {
                display: inline-block;
                margin: 10px 5px;
                padding: 10px 20px;
                background: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            a:hover {
                background: #218838;
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
            <h1>🛒 E-Commerce Site (Secure)</h1>
            
            <div class="security-fix">
                <h3>Security Fixes Applied:</h3>
                <ul>
                    <li>✅ Backup files removed from web-accessible directories</li>
                    <li>✅ robots.txt doesn't reveal sensitive paths</li>
                    <li>✅ No credentials in publicly accessible files</li>
                    <li>✅ Proper .gitignore and deployment practices</li>
                    <li>✅ Secrets managed via environment variables</li>
                    <li>✅ Backups stored securely (not in web root)</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔒 Verify Security:</h3>
                <ol>
                    <li>View <code>/robots.txt</code> - No sensitive info revealed</li>
                    <li>Try to access backup files - All return 404</li>
                    <li>No credentials exposed in public files</li>
                    <li>All sensitive files properly protected</li>
                </ol>
                
                <h4>Try these URLs (all should return 404):</h4>
                <a href="/robots.txt" target="_blank">View robots.txt</a>
                <a href="/backup/config.php.bak" target="_blank">config.php.bak (404)</a>
                <a href="/backup/database_backup.sql" target="_blank">database backup (404)</a>
                <a href="/backup/.env.backup" target="_blank">.env.backup (404)</a>
            </div>
            
            <h3>Public Pages:</h3>
            <a href="/shop" style="background: #667eea;">Shop</a>
            <a href="/products" style="background: #667eea;">Products</a>
        </div>
    </body>
    </html>
    """


# FIXED: Proper robots.txt without revealing sensitive information
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    # FIXED: Only list necessary disallowed paths, no comments revealing backups
    return """User-agent: *
Disallow: /admin/
Disallow: /api/internal/
Disallow: /user/private/

# Allow public pages
Allow: /
Allow: /shop/
Allow: /products/
Allow: /about/
Allow: /contact/

Sitemap: https://www.company.com/sitemap.xml
"""


# FIXED: Backup files are NOT accessible via web server
@app.get("/backup/{filename:path}")
async def backup_files(filename: str):
    # FIXED: Return 404 for any backup file requests
    # In production, backup directory should not be in web root at all
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not Found")


# FIXED: Config files are NOT accessible
@app.get("/config/{filename:path}")
async def config_files(filename: str):
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not Found")


# FIXED: .env files are NOT accessible
@app.get("/.env")
@app.get("/.env.backup")
@app.get("/.env.production")
async def env_files():
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not Found")


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


"""
ADDITIONAL SECURITY MEASURES FOR DEPLOYMENT:

1. .gitignore file should include:
   *.bak
   *.backup
   *.sql
   .env
   .env.*
   config/*.bak
   /backup/

2. Server configuration (nginx/apache):
   - Deny access to backup directories
   - Deny access to .git directory
   - Deny access to configuration files
   
3. File structure:
   /app/                  (application code - web accessible)
   /config/               (NOT web accessible)
   /backups/              (NOT web accessible, separate partition)
   /logs/                 (NOT web accessible)
   
4. Backup best practices:
   - Store backups outside web root
   - Encrypt backups
   - Use secure file permissions (600 or 400)
   - Automate backup deletion after retention period
   - Store backups on separate server/cloud storage
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        server_header=False,
        log_level="error"
    )
