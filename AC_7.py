from fastapi import FastAPI , HTTPException , status , Depends , Response , Cookie
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db 
import models
from database import engine

#access control vulnerability - Insecure Direct Object Reference (IDOR) - Access Other User Profiles

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Pydantic model for login
class LoginRequest(BaseModel):
    name: str
    password: str


@app.get("/", response_class=HTMLResponse)
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                width: 300px;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                color: #666;
                margin-bottom: 5px;
            }
            input {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #5568d3;
            }
            .error {
                color: red;
                text-align: center;
                margin-top: 10px;
                display: none;
            }
            .info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 12px;
                color: #1976d2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Login</h1>
            <div class="info">
                <strong>Test Users:</strong><br>
                • mahdi / password (ID: 1)<br>
                • omar / password (ID: 2)
            </div>
            <form id="loginForm">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
                <div class="error" id="error"></div>
            </form>
        </div>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const name = document.getElementById('name').value;
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('error');
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ name, password })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        window.location.href = '/profile/' + data.user_id;
                    } else {
                        const data = await response.json();
                        errorDiv.textContent = data.detail || 'Login failed';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    errorDiv.textContent = 'An error occurred';
                    errorDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/login")
async def login(login_req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(models.user).filter(models.user.name == login_req.name).first()
    
    if not user or user.password != login_req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Store user info in cookies
    response.set_cookie(key="user_id", value=str(user.id))
    response.set_cookie(key="username", value=user.name)
    
    return {"message": "Login successful", "user_id": user.id, "username": user.name}


# VULNERABLE ENDPOINT: No authorization check!
# Anyone can view any profile by just knowing/guessing the user_id in URL
@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def view_profile(
    user_id: int, 
    current_user_id: Optional[str] = Cookie(None), 
    username: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    # VULNERABILITY: No authentication required - anyone can access any profile!
    
    # VULNERABILITY: No check if current_user_id matches user_id
    # Anyone can access anyone's profile by changing the URL
    
    # Get the profile user from database
    profile_user = db.query(models.user).filter(models.user.id == user_id).first()
    
    if not profile_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get current user info if logged in
    current_user = None
    if current_user_id:
        current_user = db.query(models.user).filter(models.user.id == int(current_user_id)).first()
    
    is_own_profile = current_user_id and (int(current_user_id) == user_id)
    logged_in_as = f"{username} (User ID: {current_user_id})" if current_user_id else "Not logged in"
    
    vulnerability_warning = ""
    if not current_user_id:
        vulnerability_warning = f"""
            <div class="vulnerability-warning">
                <h3>⚠️ IDOR Vulnerability Exploited!</h3>
                <p>You are NOT logged in, yet you can view User ID: {user_id}'s profile!</p>
                <p>This endpoint has NO authentication or authorization checks.</p>
            </div>
        """
    elif not is_own_profile:
        vulnerability_warning = f"""
            <div class="vulnerability-warning">
                <h3>⚠️ IDOR Vulnerability Exploited!</h3>
                <p>You (User ID: {current_user_id} - {username}) are viewing someone else's profile!</p>
                <p>You accessed User ID: {user_id} by changing the URL parameter.</p>
            </div>
        """
    
    exploit_section = ""
    if is_own_profile:
        exploit_section = """
            <div class="exploit-section">
                <h3>🔍 Try This Exploit:</h3>
                <p>Change the <strong>user_id</strong> in the URL to view other users' profiles!</p>
                <div class="url-examples">
                    <p><strong>Try these URLs:</strong></p>
                    <a href="/profile/1" class="exploit-link">View User ID: 1 (mahdi's profile)</a><br>
                    <a href="/profile/2" class="exploit-link">View User ID: 2 (omar's profile)</a>
                </div>
                <pre style="text-align: left; background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; margin-top: 15px;">
# You can also try with curl:
curl http://localhost:8000/profile/1 \\
  --cookie "user_id=2; username=omar"
                </pre>
            </div>
        """
    
    admin_badge = ""
    admin_panel_link = ""
    if profile_user.is_admin:
        admin_badge = '<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; margin-left: 10px;">👑 Admin</span>'
        admin_panel_link = '<a href="/admin_panel" style="display: inline-block; margin: 20px 0; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Go to Admin Panel</a><br>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Profile</title>
        
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }}
            .container {{
                background: white;
                padding: 40px 60px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 800px;
            }}
            h1 {{
                color: #333;
                margin: 0 0 20px 0;
            }}
            h3 {{
                color: #dc3545;
            }}
            .profile-info {{
                background: #f5f5f5;
                padding: 25px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .profile-info h2 {{
                color: #333;
                margin: 0 0 15px 0;
            }}
            .profile-field {{
                margin: 10px 0;
                font-size: 16px;
            }}
            .profile-field strong {{
                color: #666;
            }}
            .vulnerability-warning {{
                background: #f8d7da;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #dc3545;
            }}
            .exploit-section {{
                background: #fff3cd;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }}
            .url-examples {{
                margin: 15px 0;
            }}
            .exploit-link {{
                display: inline-block;
                margin: 5px;
                padding: 10px 20px;
                background: #dc3545;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .exploit-link:hover {{
                background: #c82333;
            }}
            .current-user {{
                background: #e3f2fd;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 14px;
            }}
            .logout {{
                margin-top: 20px;
            }}
            .logout a {{
                color: #dc3545;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="current-user">
                <strong>Status:</strong> {logged_in_as}
            </div>
            
            <h1>👤 User Profile</h1>
            
            {vulnerability_warning}
            
            <div class="profile-info">
                <h2>{profile_user.name}'s Profile {admin_badge}</h2>
                <div class="profile-field">
                    <strong>User ID:</strong> {profile_user.id}
                </div>
                <div class="profile-field">
                    <strong>Username:</strong> {profile_user.name}
                </div>
                <div class="profile-field">
                    <strong>Admin Status:</strong> {profile_user.is_admin}
                </div>
                <div class="profile-field" style="background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 15px;">
                    <strong>🔒 Sensitive Info:</strong> This profile contains private data that should only be visible to the profile owner!
                </div>
            </div>
            
            {exploit_section}
            
            {admin_panel_link}
            
            <div class="logout">
                <a href="/logout">Logout</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(user_id: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    # VULNERABILITY: No authentication or authorization required!
    # Anyone can access the admin panel directly via URL
    
    logged_in_info = ""
    if user_id and username:
        logged_in_info = f"<p><em>(Currently logged in as: {username})</em></p>"
    else:
        logged_in_info = "<p><em>(Accessing without login!)</em></p>"
    
    # VULNERABILITY: Sensitive API key exposed in HTML source code (hidden div)
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 800px;
                }}
                h1 {{ color: #28a745; }}
                p {{ color: #666; }}
                .admin-info {{
                    background: #d4edda;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border: 1px solid #c3e6cb;
                }}
                .warning {{
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border: 1px solid #ffc107;
                    text-align: left;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <!-- VULNERABILITY: Sensitive API key exposed in HTML source code -->
            <div style="display: none;">Your password is 123 </div>
            
            <div class="container">
                <h1>👑 Admin Panel</h1>
                <div class="admin-info">
                    <p><strong>Welcome to Admin Panel!</strong></p>
                    {logged_in_info}
                    <p>You have successfully accessed the admin panel!</p>
                    <p style="margin-top: 15px;">
                        Manage users, view analytics, and configure system settings.
                    </p>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Security Vulnerabilities:</strong><br><br>
                    <strong>1. Missing Authentication & Authorization</strong><br>
                    This admin panel can be accessed directly without any login!<br>
                    Just navigate to <code>http://localhost:8000/admin_panel</code><br><br>
                    <strong>2. Information Disclosure in HTML Source Code</strong><br>
                    Sensitive API keys or credentials are exposed in the HTML source code.<br><br>
                    <strong>How to exploit:</strong>
                    <ol style="text-align: left;">
                        <li>Right-click on this page and select "View Page Source" (or press Ctrl+U)</li>
                        <li>Search for "API key" in the source code</li>
                        <li>Find the hidden div containing the API key</li>
                        <li>The key is hidden with <code>display: none;</code> but still visible in source!</li>
                    </ol>
                    <strong>Why it's dangerous:</strong><br>
                    Even though the div is hidden from view, anyone can see it in the page source.
                    Attackers can use browser DevTools or simply view source to extract sensitive data.
                </div>
                
                <a href="/">Back to Home</a>
            </div>
        </body>
        </html>
        """
    )


@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
