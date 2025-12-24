from fastapi import FastAPI , HTTPException , status , Depends , Response , Cookie
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db 
import models
from database import engine
import secrets

# FIXED: Proper authentication and authorization for profile access

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# In-memory session store
active_sessions = {}

# Pydantic model for login
class LoginRequest(BaseModel):
    name: str
    password: str


def create_session_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    active_sessions[token] = user_id
    return token


def get_current_user(session_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not session_token or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = active_sessions[session_token]
    user = db.query(models.user).filter(models.user.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return user


@app.get("/", response_class=HTMLResponse)
async def login_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Fixed</title>
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
                background: #d4edda;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-size: 12px;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Login (Fixed)</h1>
            <div class="info">
                <strong>✅ Security Fixed:</strong><br>
                • Authentication required<br>
                • Users can only view own profile<br>
                • IDOR vulnerability fixed
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
    user = db.query(models.user).filter(models.user.name == login_req.name).first()
    
    if not user or user.password != login_req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    session_token = create_session_token(user.id)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    
    return {"message": "Login successful", "user_id": user.id, "username": user.name}


# FIXED ENDPOINT: Proper authorization checks!
@app.get("/profile/{user_id}", response_class=HTMLResponse)
async def view_profile(
    user_id: int,
    current_user: models.user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # FIXED: Authentication is required (via get_current_user dependency)
    
    # FIXED: Check if user is authorized to view this profile
    # Users can only view their own profile unless they are admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    # Get the profile user from database
    profile_user = db.query(models.user).filter(models.user.id == user_id).first()
    
    if not profile_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    is_own_profile = (current_user.id == user_id)
    
    security_info = ""
    if is_own_profile:
        security_info = """
            <div class="security-info">
                <h3>✅ Security Fixed</h3>
                <p>The profile endpoint now requires:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>User must be authenticated</li>
                    <li>Users can only view their own profile</li>
                    <li>Admins can view any profile</li>
                    <li>Trying to access another profile will be blocked</li>
                </ul>
                <p style="margin-top: 10px;">Try changing the URL to /profile/1 or /profile/2 - you'll get access denied!</p>
            </div>
        """
    else:
        security_info = f"""
            <div class="admin-viewing">
                <p>👑 You are viewing this profile as an administrator</p>
            </div>
        """
    
    admin_badge = ""
    if profile_user.is_admin:
        admin_badge = '<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 3px; margin-left: 10px;">👑 Admin</span>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Profile - Fixed</title>
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
                color: #28a745;
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
            .security-info {{
                background: #d4edda;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #28a745;
            }}
            .admin-viewing {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 1px solid #ffc107;
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
                <strong>Logged in as:</strong> {current_user.name} (User ID: {current_user.id})
            </div>
            
            <h1>👤 User Profile</h1>
            
            {security_info}
            
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
                <div class="profile-field" style="background: #d4edda; padding: 10px; border-radius: 5px; margin-top: 15px; border: 1px solid #c3e6cb;">
                    <strong>🔒 Sensitive Info Protected:</strong> Only authorized users can view this profile!
                </div>
            </div>
            
            <div class="logout">
                <a href="/logout">Logout</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]
    
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
