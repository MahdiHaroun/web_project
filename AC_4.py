from fastapi import FastAPI , HTTPException , status , Depends , Response , Cookie
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db 
import models
from database import engine

#access control vulnerability - Insecure Direct Object Reference (IDOR)

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Pydantic models
class LoginRequest(BaseModel):
    name: str
    password: str

class UpdateUserRequest(BaseModel):
    user_id: int
    is_admin: bool


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
                • mahdi / password (admin)<br>
                • omar / password (user)
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


@app.get("/main_page", response_class=HTMLResponse)
async def main_page(user_id: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return RedirectResponse(url="/")
    
    # Get user from database
    user = db.query(models.user).filter(models.user.id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/")
    
    admin_link = ""
    if user.is_admin:
        admin_link = '<a href="/admin_panel" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Go to Admin Panel</a>'
    
    exploit_section = ""
    if not user.is_admin:
        exploit_section = f"""
            <div class="exploit-section">
                <h3>⚠️ Privilege Escalation Vulnerability</h3>
                <p>Try sending this POST request to become admin:</p>
                <button id="exploitBtn">Exploit: Make Myself Admin</button>
                <pre id="curlCommand" style="text-align: left; background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto;">
curl -X POST http://localhost:8000/update_user \\
  -H "Content-Type: application/json" \\
  -d '{{"user_id": {user.id}, "is_admin": true}}'
                </pre>
                <div id="exploitResult" style="margin-top: 10px; display: none;"></div>
            </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Main Page</title>
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
            p {{
                color: #666;
                font-size: 18px;
            }}
            .user-info {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .exploit-section {{
                background: #fff3cd;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }}
            .logout {{
                margin-top: 20px;
            }}
            .logout a {{
                color: #dc3545;
                text-decoration: none;
            }}
            #exploitBtn {{
                background: #dc3545;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 0;
            }}
            #exploitBtn:hover {{
                background: #c82333;
            }}
            .success {{
                color: #28a745;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Welcome to the Main Page</h1>
            <div class="user-info">
                <p><strong>Logged in as:</strong> {username}</p>
                <p><strong>User ID:</strong> {user.id}</p>
                <p><strong>Admin Status:</strong> <span id="adminStatus">{user.is_admin}</span></p>
            </div>
            {exploit_section}
            {admin_link}
            <div class="logout">
                <a href="/logout">Logout</a>
            </div>
        </div>
        <script>
            const exploitBtn = document.getElementById('exploitBtn');
            if (exploitBtn) {{
                exploitBtn.addEventListener('click', async () => {{
                    const resultDiv = document.getElementById('exploitResult');
                    try {{
                        const response = await fetch('/update_user', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                user_id: {user.id},
                                is_admin: true
                            }})
                        }});
                        
                        if (response.ok) {{
                            resultDiv.innerHTML = '<p class="success">✅ Success! Refreshing page...</p>';
                            resultDiv.style.display = 'block';
                            setTimeout(() => {{
                                window.location.reload();
                            }}, 1500);
                        }} else {{
                            const data = await response.json();
                            resultDiv.innerHTML = '<p style="color: red;">❌ ' + data.detail + '</p>';
                            resultDiv.style.display = 'block';
                        }}
                    }} catch (error) {{
                        resultDiv.innerHTML = '<p style="color: red;">❌ Error: ' + error.message + '</p>';
                        resultDiv.style.display = 'block';
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_content


# VULNERABLE ENDPOINT: No authorization check!
# Any user can update any user's admin status
@app.post("/update_user")
async def update_user(update_req: UpdateUserRequest, db: Session = Depends(get_db)):
    # VULNERABILITY: No check if the requester is authorized to make this change
    # No check if the requester is an admin
    # No check if the requester is updating their own account
    
    user = db.query(models.user).filter(models.user.id == update_req.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # VULNERABLE: Directly updating without any authorization
    user.is_admin = update_req.is_admin
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User updated successfully",
        "user_id": user.id,
        "username": user.name,
        "is_admin": user.is_admin
    }


@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    return response


@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(user_id: Optional[str] = Cookie(None), username: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return RedirectResponse(url="/")
    
    # Get user from database to check real admin status
    user = db.query(models.user).filter(models.user.id == int(user_id)).first()
    
    if not user or not user.is_admin:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Access Denied</title>
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
                        text-align: center;
                    }
                    h1 { color: #dc3545; }
                    p { color: #666; }
                    a {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚫 Access Denied</h1>
                    <p>You need admin privileges to access this page.</p>
                    <a href="/main_page">Go Back</a>
                </div>
            </body>
            </html>
            """,
            status_code=403
        )
    
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
                <h1>👑 Admin Panel</h1>
                <div class="admin-info">
                    <p><strong>Welcome, {username}!</strong></p>
                    <p>You have successfully accessed the admin panel!</p>
                    <p style="margin-top: 15px; font-size: 14px; color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px;">
                        ⚠️ <strong>Vulnerability Exploited:</strong> You gained admin access by sending<br>
                        an unauthorized POST request to /update_user endpoint!
                    </p>
                </div>
                <a href="/main_page">Back to Main Page</a>
            </div>
        </body>
        </html>
        """
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
