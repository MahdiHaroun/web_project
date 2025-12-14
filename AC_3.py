from fastapi import FastAPI , HTTPException , status , Depends , Response , Cookie , Request
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from jinja2 import Environment , FileSystemLoader
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db 
import models
from database import engine

#access control vernublities 

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
    
    # VULNERABLE: Setting admin status in cookie (can be manipulated by user)
    response.set_cookie(
        key="username",
        value=user.name,
        httponly=False  # VULNERABLE: Allows JavaScript access
    )
    response.set_cookie(
        key="is_admin",
        value=str(user.is_admin),  # VULNERABLE: Storing as plain text "True" or "False"
        httponly=False  # VULNERABLE: Allows JavaScript access and modification
    )
    
    return {"message": "Login successful", "username": user.name}


@app.get("/main_page", response_class=HTMLResponse)
async def main_page(username: Optional[str] = Cookie(None), is_admin: Optional[str] = Cookie(None)):
    if not username:
        return RedirectResponse(url="/")
    
    admin_link = ""
    # Check for both "True" and "true" to handle manual cookie manipulation
    if is_admin and is_admin.lower() == "true":
        admin_link = '<a href="/admin_panel" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">Go to Admin Panel</a>'
    
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
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .cookie-info {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 1px solid #ffc107;
            }}
            .cookie-info strong {{
                color: #856404;
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
                <p><strong>Logged in as:</strong> {username}</p>
                <p><strong>Admin Status:</strong> <span id="adminStatus">{is_admin}</span></p>
            </div>
            <div class="cookie-info">
                <strong>🔍 Tip:</strong> Open Developer Tools (F12) → Application/Storage → Cookies<br>
                Try changing the <code>is_admin</code> cookie value!
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


@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("username")
    response.delete_cookie("is_admin")
    return response


@app.get("/admin_panel", response_class=HTMLResponse)
async def admin_panel(username: Optional[str] = Cookie(None), is_admin: Optional[str] = Cookie(None)):
    # VULNERABLE: Only checking cookie value, not database
    if not username:
        return RedirectResponse(url="/")
    
    # Check for both "True" and "true" to handle manual cookie manipulation
    if not is_admin or is_admin.lower() != "true":
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
                    <p><em>Hint: Check your cookies...</em></p>
                    <a href="/main_page">Go Back</a>
                </div>
            </body>
            </html>
            """,
            status_code=403
        )
    
    # VULNERABLE: User reached admin panel by manipulating cookie
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
                        not the actual database. Anyone can change their cookie to gain access!
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