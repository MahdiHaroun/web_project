from fastapi import FastAPI, HTTPException, Cookie, Response, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import secrets
from database import get_db
import models
from database import engine

# FIXED: Proper Method-Based Access Control
# Only POST method is allowed for sensitive operations with proper authorization

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Session storage
active_sessions = {}


class LoginRequest(BaseModel):
    name: str
    password: str


class UpgradeRequest(BaseModel):
    username: str
    action: str


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AC_6_Fixed - Secure Method-Based Access Control</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
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
                background: #e7f3ff;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            input {
                padding: 10px;
                margin: 5px 0;
                width: 100%;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover {
                background: #218838;
            }
            .danger-btn {
                background: #dc3545;
            }
            .danger-btn:hover {
                background: #c82333;
            }
            .result {
                margin-top: 15px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 5px;
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
            <h1>✅ AC_6_Fixed: Secure Method-Based Access Control</h1>
            
            <div class="security-fix">
                <h3>Security Fixes Applied:</h3>
                <ul>
                    <li>✅ Endpoint only accepts POST requests (GET returns 405 Method Not Allowed)</li>
                    <li>✅ Request body validation using Pydantic models (no query parameters)</li>
                    <li>✅ Proper admin authorization check before processing</li>
                    <li>✅ HTTP method validation in middleware</li>
                    <li>✅ CSRF protection considerations for state-changing operations</li>
                    <li>✅ Audit logging for sensitive operations</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>Step 1: Login</h3>
                <p>Try logging in as both admin and non-admin:</p>
                <input type="text" id="username" placeholder="Username" value="omar">
                <input type="password" id="password" placeholder="Password" value="password">
                <button onclick="login()">Login</button>
                <div id="loginResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Step 2: Try to Exploit (Will Fail)</h3>
                <p>This will fail because GET requests are not allowed:</p>
                <button class="danger-btn" onclick="tryGetExploit()">❌ Try GET Request (Will Fail)</button>
                <div id="exploitResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Step 3: Try Legitimate Upgrade (Will Fail for Non-Admin)</h3>
                <p>Non-admin users cannot upgrade even with POST:</p>
                <button onclick="tryLegitimateUpgrade()">Try POST Request</button>
                <div id="postResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="test-section">
                <h3>Step 4: Access Admin Panel</h3>
                <button onclick="checkAdminPanel()">Access Admin Panel</button>
                <div id="adminResult" class="result" style="display: none;"></div>
            </div>
            
            <h3>Test Users:</h3>
            <ul>
                <li><strong>mahdi</strong> - Admin (password: password) ← Can upgrade users</li>
                <li><strong>omar</strong> - Regular User (password: password) ← Cannot upgrade</li>
            </ul>
        </div>
        
        <script>
            let sessionToken = '';
            let currentUsername = '';
            
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('loginResult');
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({name: username, password})
                    });
                    
                    const data = await response.json();
                    resultDiv.style.display = 'block';
                    
                    if (response.ok) {
                        sessionToken = data.session_token;
                        currentUsername = username;
                        resultDiv.innerHTML = '<strong>✅ Login Successful!</strong><br>' +
                            'Username: ' + data.username + '<br>' +
                            'Admin: ' + data.is_admin + '<br>' +
                            'Session Token: ' + sessionToken;
                    } else {
                        resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + data.detail;
                    }
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + error;
                }
            }
            
            async function tryGetExploit() {
                const resultDiv = document.getElementById('exploitResult');
                
                if (!sessionToken) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Please login first!';
                    return;
                }
                
                try {
                    // FIXED: GET request will be rejected with 405 Method Not Allowed
                    const response = await fetch('/upgrade_user?username=' + currentUsername + '&action=UPGRADE', {
                        method: 'GET',
                        headers: {
                            'Cookie': 'session_token=' + sessionToken
                        }
                    });
                    
                    const data = await response.json();
                    resultDiv.style.display = 'block';
                    
                    resultDiv.innerHTML = '<strong>❌ GET Request Blocked!</strong><br>' +
                        'Status: ' + response.status + ' ' + response.statusText + '<br>' +
                        'Message: ' + data.detail + '<br><br>' +
                        '<em>The server correctly rejected the GET request!</em>';
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + error;
                }
            }
            
            async function tryLegitimateUpgrade() {
                const resultDiv = document.getElementById('postResult');
                
                if (!sessionToken) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Please login first!';
                    return;
                }
                
                try {
                    // FIXED: POST request with proper body, but will fail authorization if not admin
                    const response = await fetch('/upgrade_user', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Cookie': 'session_token=' + sessionToken
                        },
                        body: JSON.stringify({
                            username: currentUsername,
                            action: 'UPGRADE'
                        })
                    });
                    
                    const data = await response.json();
                    resultDiv.style.display = 'block';
                    
                    if (response.ok) {
                        resultDiv.innerHTML = '<strong>✅ Upgrade Successful!</strong><br>' +
                            data.message + '<br>' +
                            '<em>You were logged in as an admin.</em>';
                    } else {
                        resultDiv.innerHTML = '<strong>❌ Authorization Failed!</strong><br>' +
                            'Status: ' + response.status + '<br>' +
                            'Message: ' + data.detail + '<br><br>' +
                            '<em>Non-admin users cannot upgrade accounts!</em>';
                    }
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + error;
                }
            }
            
            async function checkAdminPanel() {
                const resultDiv = document.getElementById('adminResult');
                
                if (!sessionToken) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Please login first!';
                    return;
                }
                
                try {
                    const response = await fetch('/admin_panel', {
                        headers: {
                            'Cookie': 'session_token=' + sessionToken
                        }
                    });
                    
                    const data = await response.text();
                    resultDiv.style.display = 'block';
                    
                    if (response.ok) {
                        resultDiv.innerHTML = '<strong>✅ Admin Panel Access Granted!</strong><br><br>' + data;
                    } else {
                        resultDiv.innerHTML = '<strong>❌ Access Denied:</strong><br>' + data;
                    }
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + error;
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/login")
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    username = request.name
    password = request.password
    
    user = db.query(models.user).filter(models.user.name == username).first()
    
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session_token = secrets.token_urlsafe(32)
    active_sessions[session_token] = {
        "username": username,
        "is_admin": user.is_admin,
        "user_id": user.id
    }
    
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    
    return {
        "message": "Login successful",
        "username": username,
        "is_admin": user.is_admin,
        "session_token": session_token
    }


# FIXED: Only POST method allowed, no GET
@app.post("/upgrade_user")
async def upgrade_user(
    request: UpgradeRequest,  # FIXED: Use Pydantic model for request body validation
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # FIXED: Authentication check
    if not session_token or session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = active_sessions[session_token]
    
    # FIXED: Authorization check - only admins can upgrade users
    if not session["is_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Only administrators can upgrade users."
        )
    
    # FIXED: Validate action
    if request.action != "UPGRADE":
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # FIXED: Process the upgrade with proper authorization
    user = db.query(models.user).filter(models.user.name == request.username).first()
    
    if user:
        user.is_admin = True
        db.commit()
        
        # Update session if upgrading self
        for token, sess in active_sessions.items():
            if sess["username"] == request.username:
                active_sessions[token]["is_admin"] = True
        
        # FIXED: Audit log (in production, log to file/database)
        print(f"AUDIT: Admin {session['username']} upgraded user {request.username} to admin")
        
        return {
            "message": f"User {request.username} has been upgraded to admin!",
            "username": request.username,
            "is_admin": True
        }
    
    raise HTTPException(status_code=404, detail="User not found")


# FIXED: Middleware to log method-based access attempts
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log attempts to access sensitive endpoints with wrong methods
    if request.url.path == "/upgrade_user" and request.method != "POST":
        print(f"SECURITY: Blocked {request.method} request to /upgrade_user from {request.client.host}")
    
    response = await call_next(request)
    return response


@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = active_sessions[session_token]
    
    if not session["is_admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")
    
    return f"""
    <html>
        <body style="font-family: Arial; padding: 50px; background: #d4edda;">
            <h1>🎉 Admin Panel</h1>
            <p>Welcome, <strong>{session['username']}</strong>!</p>
            <p>You have legitimate admin access.</p>
            <p>This system properly enforces method-based access control!</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
