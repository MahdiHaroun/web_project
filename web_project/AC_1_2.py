from fastapi import FastAPI , HTTPException , status , Depends 
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from database import get_db 
import models
from database import engine



#robots.txt file shows url to admin panel

# source code contains admin panel url

app = FastAPI()
models.Base.metadata.create_all(bind=engine)





@app.get("/main_page", response_class=HTMLResponse)
async def main_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Main Page</title>
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
                padding: 40px 60px;
                border-radius: 10px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
            }
            h1 {
                color: #333;
                margin: 0 0 20px 0;
            }
            p {
                color: #666;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Welcome to the Main Page</h1>
            <script>
            var isAdmin = false;
if (isAdmin) {
    var topLinksTag = document.getElementsByClassName("top-links")[0];
    var adminPanelTag = document.createElement('a');
    adminPanelTag.setAttribute('href', '/admin-ivh6qh');
    adminPanelTag.innerText = 'Admin panel';
    topLinksTag.append(adminPanelTag);
    var pTag = document.createElement('p');
    pTag.innerText = '';
    topLinksTag.appendChild(pTag);
}

            </script>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/admin_panel")
async def admin_panel():
    return {"message": "Welcome to the admin panel"}

@app.get("/main_page/robots.txt")
async def robots_txt():
    return """User-agent: *
Disallow: /admin_panel
"""





















if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)