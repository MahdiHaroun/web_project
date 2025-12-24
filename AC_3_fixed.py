from fastapi import FastAPI , HTTPException , status , Depends , Response , Cookie , Request
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from jinja2 import Environment , FileSystemLoader
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db 
import models
from database import engine
import secrets
import hashlib

# FIXED: Proper session management with secure tokens




'''
code to fix: 
    # FIXED: Store session token in secure httponly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # FIXED: Cannot be accessed by JavaScript
        secure=False,    # Set to True in production with HTTPS
        samesite="lax"
    )
    

'''

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# In-memory session store (use Redis or database in production)
active_sessions = {}

# Pydantic model for login
class LoginRequest(BaseModel):
    name: str
    password: str


def create_session_token(user_id: int) -> str:
    """Generate a secure random session token"""
    token = secrets.token_urlsafe(32)
    active_sessions[token] = user_id
    return token


def get_current_user_from_session(session_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """Validate session and get current user"""
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
        <title>Login - Fixed Version</title>
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
                • Secure session tokens<br>
                • HttpOnly cookies<br>
                • Server-side validation<br>
                • No client-side admin checks
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
                        window.location.href = '/main_page';
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
    
    # FIXED: Create secure session token
    session_token = create_session_token(user.id)
    
    # FIXED: Store session token in secure httponly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # FIXED: Cannot be accessed by JavaScript
        secure=False,    # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {"message": "Login successful"}


@app.get("/main_page", response_class=HTMLResponse)
async def main_page(current_user: models.user = Depends(get_current_user_from_session)):
    admin_link = ""
    if current_user.is_admin:
        admin_link = '<a href="/admin_panel" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Go to Admin Panel</a>'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Main Page - Fixed</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 40px 60px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
            }}
            h1 {{
                color: #333;
                margin: 0 0 20px 0;
            }}
            p {{
                color: #666;
                font-size: 18px;
            }}
            .user-info {{
                background: #d4edda;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 1px solid #c3e6cb;
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
            <h1>🎉 Welcome to the Main Page</h1>
            <div class="user-info">
                <p><strong>Logged in as:</strong> {current_user.name}</p>
                <p><strong>Admin Status:</strong> {current_user.is_admin}</p>
                <p style="font-size: 14px; margin-top: 10px;">
                    ✅ <strong>Security Fixed:</strong><br>
                    Cookies are httpOnly and cannot be manipulated by JavaScript!
                </p>
            </div>
            {admin_link}
            <div class="logout">
                <a href="/logout">Logout</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(current_user: models.user = Depends(get_current_user_from_session)):
    # FIXED: Check authorization from database, not cookies
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Panel - Fixed</title>
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
            <div class="container">
                <h1>👑 Admin Panel (Fixed)</h1>
                <div class="admin-info">
                    <p><strong>Welcome, {current_user.name}!</strong></p>
                    <p>You have successfully accessed the admin panel!</p>
                    <p style="margin-top: 15px; font-size: 14px;">
                        ✅ <strong>Security Fixes Applied:</strong><br><br>
                        • Secure session tokens (random, unpredictable)<br>
                        • HttpOnly cookies (no JavaScript access)<br>
                        • Server-side authorization checks<br>
                        • Admin status verified from database
                    </p>
                </div>
                <a href="/main_page">Back to Main Page</a>
            </div>
        </body>
        </html>
        """
    )


@app.get("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    # FIXED: Remove session from server
    if session_token and session_token in active_sessions:
        del active_sessions[session_token]
    
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
