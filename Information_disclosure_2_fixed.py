from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# FIXED: Proper Secret Management Without Debug Pages

app = FastAPI(title="Web Application - Secure")

# FIXED: Load secrets from environment variables, not hardcoded
load_dotenv()
SECRET_API_KEY = os.getenv("SECRET_API_KEY", "")  # Load from environment
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")

# FIXED: Never expose these in responses or debug pages!


@app.get("/", response_class=HTMLResponse)
async def home():
    # FIXED: No HTML comments revealing hidden pages
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company Portal - Secure</title>
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
                margin: 10px 0;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            a:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏢 Company Portal (Secure)</h1>
            
            <div class="security-fix">
                <h3>Security Fixes Applied:</h3>
                <ul>
                    <li>✅ No HTML comments revealing hidden pages</li>
                    <li>✅ Debug pages completely removed</li>
                    <li>✅ Secrets stored in environment variables</li>
                    <li>✅ No configuration exposed to public</li>
                    <li>✅ Proper access control on all endpoints</li>
                    <li>✅ Clean HTML source code</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔒 Verify Security:</h3>
                <ol>
                    <li><strong>View Page Source</strong> - No comments revealing hidden pages!</li>
                    <li>Try to access <code>/debug/phpinfo</code> - Returns 404</li>
                    <li>No sensitive information in HTML source</li>
                    <li>All secrets properly secured in environment variables</li>
                </ol>
            </div>
            
            <h3>Public Pages:</h3>
            <a href="/about">About Us</a>
            <a href="/contact">Contact</a>
        </div>
    </body>
    </html>
    """


# FIXED: Debug page removed or protected with authentication
@app.get("/debug/phpinfo")
async def phpinfo():
    # FIXED: Debug endpoint completely removed or requires admin authentication
    raise HTTPException(
        status_code=404,
        detail="Page not found"
    )


# Alternative FIXED approach: If debug page is needed, protect it with authentication
@app.get("/admin/system-info")
async def system_info_protected():
    
    # return 401 Unauthorized
    raise HTTPException(
        status_code=401,
        detail="Authentication required"
    )
    
    # If authenticated as admin, could return limited, safe information:
    # return {
    #     "status": "operational",
    #     "version": "1.0.0",  # App version only, not system details
    #     "environment": "production"
    # }


@app.get("/about")
async def about():
    return {"message": "About Us page"}


@app.get("/contact")
async def contact():
    return {"message": "Contact page"}


# FIXED: Proper health check endpoint (no sensitive info)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        server_header=False,  # FIXED: Don't expose server info
        log_level="error"
    )
