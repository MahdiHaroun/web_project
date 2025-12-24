from fastapi import FastAPI, HTTPException, Cookie, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import secrets
from database import get_db
import models
from database import engine

# VULNERABLE: Method-Based Access Control Bypass
# The upgrade_user endpoint only checks POST method, but accepts GET too

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Session storage
active_sessions = {}


class LoginRequest(BaseModel):
    name: str
    password: str


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AC_6 - Method-Based Access Control Vulnerability</title>
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
            .vulnerability {
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }
            .exploit-steps {
                background: #f8d7da;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #dc3545;
            }
            .login-section {
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
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover {
                background: #5568d3;
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
            <h1>⚠️ AC_6: Method-Based Access Control Bypass</h1>
            
            <div class="vulnerability">
                <h3>Vulnerability Description:</h3>
                <p>The <code>/upgrade_user</code> endpoint is intended to be used only via POST requests with proper admin authorization. 
                However, it also responds to GET requests and doesn't properly validate the HTTP method, allowing non-admin users 
                to upgrade themselves by simply changing the request method and adding parameters to the URL.</p>
            </div>
            
            <div class="exploit-steps">
                <h3>🔓 Exploitation Steps:</h3>
                <ol>
                    <li>Login as <strong>omar</strong> (non-admin user)</li>
                    <li>Copy your session token from the response</li>
                    <li>Open a new browser tab</li>
                    <li>Navigate to: <code>http://localhost:8000/upgrade_user?username=omar&action=UPGRADE</code></li>
                    <li>Or use curl: <code>curl -b "session_token=YOUR_TOKEN" "http://localhost:8000/upgrade_user?username=omar&action=UPGRADE"</code></li>
                    <li>You're now an admin! Access <code>/admin_panel</code> to verify</li>
                </ol>
            </div>
            
            <div class="login-section">
                <h3>Step 1: Login</h3>
                <input type="text" id="username" placeholder="Username" value="omar">
                <input type="password" id="password" placeholder="Password" value="password">
                <button onclick="login()">Login</button>
                <div id="loginResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="login-section">
                <h3>Step 2: Exploit (After Login)</h3>
                <p>Click this button to exploit the vulnerability by sending a GET request:</p>
                <button class="danger-btn" onclick="exploitVulnerability()">🔓 Upgrade to Admin via GET</button>
                <div id="exploitResult" class="result" style="display: none;"></div>
            </div>
            
            <div class="login-section">
                <h3>Step 3: Verify Admin Access</h3>
                <button onclick="checkAdminPanel()">Access Admin Panel</button>
                <div id="adminResult" class="result" style="display: none;"></div>
            </div>
            
            <h3>Test Users:</h3>
            <ul>
                <li><strong>mahdi</strong> - Admin (password: password)</li>
                <li><strong>omar</strong> - Regular User (password: password) ← Use this to test</li>
            </ul>
        </div>
        
        <script>
            let sessionToken = '';
            
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
                        resultDiv.innerHTML = '<strong>✅ Login Successful!</strong><br>' +
                            'Username: ' + data.username + '<br>' +
                            'Admin: ' + data.is_admin + '<br>' +
                            'Session Token: ' + sessionToken + '<br><br>' +
                            '<em>Now proceed to Step 2 to exploit the vulnerability!</em>';
                    } else {
                        resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + data.detail;
                    }
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + error;
                }
            }
            
            async function exploitVulnerability() {
                const resultDiv = document.getElementById('exploitResult');
                
                if (!sessionToken) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>❌ Error:</strong> Please login first!';
                    return;
                }
                
                const username = document.getElementById('username').value;
                
                try {
                    // VULNERABILITY: Using GET instead of POST with query parameters
                    const response = await fetch('/upgrade_user?username=' + username + '&action=UPGRADE', {
                        method: 'GET',
                        headers: {
                            'Cookie': 'session_token=' + sessionToken
                        }
                    });
                    
                    const data = await response.json();
                    resultDiv.style.display = 'block';
                    
                    if (response.ok) {
                        resultDiv.innerHTML = '<strong>🔓 EXPLOITATION SUCCESSFUL!</strong><br>' +
                            data.message + '<br><br>' +
                            '<em>You have bypassed access control by using GET instead of POST!<br>' +
                            'Now check the Admin Panel in Step 3.</em>';
                    } else {
                        resultDiv.innerHTML = '<strong>❌ Error:</strong> ' + data.detail;
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
                        resultDiv.innerHTML = '<strong>❌ Access Denied:</strong> ' + data;
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


# VULNERABLE ENDPOINT: Responds to both POST and GET requests
@app.post("/upgrade_user")
@app.get("/upgrade_user")
async def upgrade_user(
    username: Optional[str] = None,
    action: Optional[str] = None,
    session_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # VULNERABLE: The endpoint decorator accepts both POST and GET
    # An attacker can bypass intended POST-only access by using GET with query params
    
    if not session_token or session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = active_sessions[session_token]
    
    # VULNERABLE: Only checks if user is admin for POST, but GET bypasses this logic
    # In real scenarios, developers might forget to add the same checks for different methods
    
    if not username or not action:
        raise HTTPException(status_code=400, detail="Missing username or action")
    
    if action != "UPGRADE":
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # VULNERABLE: No check to verify if the requester is an admin
    # The endpoint processes the request regardless of the HTTP method used
    
    user = db.query(models.user).filter(models.user.name == username).first()
    
    if user:
        user.is_admin = True
        db.commit()
        
        # Update the session
        if session["username"] == username:
            active_sessions[session_token]["is_admin"] = True
        
        return {
            "message": f"User {username} has been upgraded to admin!",
            "username": username,
            "is_admin": True
        }
    
    raise HTTPException(status_code=404, detail="User not found")


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
            <p>You have successfully accessed the admin panel.</p>
            <p>This proves that the method-based access control was bypassed!</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
