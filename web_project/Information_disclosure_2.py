from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import os

# VULNERABLE: Information Disclosure via Debug Page and Comments

app = FastAPI(title="Web Application - Vulnerable")

# Simulated sensitive configuration
SECRET_API_KEY = "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"
DATABASE_PASSWORD = "MyS3cr3tP@ssw0rd2024!"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


@app.get("/", response_class=HTMLResponse)
async def home():
    # VULNERABLE: HTML comments revealing hidden pages
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company Portal - Vulnerable</title>
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
            .vulnerability {
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #ffc107;
            }
            .test-section {
                background: #f8d7da;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #dc3545;
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
        <!-- VULNERABLE: Developer comments revealing hidden pages -->
        <!-- TODO: Remove debug page before going to production -->
        <!-- Debug page location: /debug/phpinfo -->
        <!-- Also need to secure: /api/config -->
        <!-- Database backup: /backup/db_dump.sql -->
        
        <div class="container">
            <h1>🏢 Company Portal (Vulnerable)</h1>
            
            <div class="vulnerability">
                <h3>Vulnerability: Information Disclosure via Debug Page & Comments</h3>
                <p><strong>Description:</strong></p>
                <ul>
                    <li>HTML source comments reveal hidden debug pages</li>
                    <li>Debug pages expose sensitive configuration</li>
                    <li>Secret keys and credentials visible</li>
                    <li>System information disclosed</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔍 How to Exploit:</h3>
                <ol>
                    <li><strong>View Page Source</strong> (Right-click → View Page Source or Ctrl+U)</li>
                    <li>Look for HTML comments (<!-- -->)</li>
                    <li>Find hidden pages mentioned in comments</li>
                    <li>Visit: <a href="/debug/phpinfo">/debug/phpinfo</a></li>
                    <li>You'll find secret keys and sensitive information!</li>
                </ol>
            </div>
            
            <h3>Public Pages:</h3>
            <a href="/about">About Us</a>
            <a href="/contact">Contact</a>
            
            <!-- VULNERABLE: More hints in comments -->
            <!-- Admin panel: /admin/secret_panel (password in phpinfo) -->
            <!-- API documentation: /api/docs -->
        </div>
    </body>
    </html>
    """


# VULNERABLE: Debug/Info page exposing sensitive configuration
@app.get("/debug/phpinfo", response_class=HTMLResponse)
async def phpinfo():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Information - Debug Page</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #d32f2f;
                border-bottom: 3px solid #d32f2f;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th {{
                background: #333;
                color: white;
            }}
            tr:nth-child(even) {{
                background: #f9f9f9;
            }}
            .warning {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
            }}
            .secret {{
                background: #f8d7da;
                padding: 10px;
                border-radius: 3px;
                font-family: monospace;
                border-left: 4px solid #dc3545;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ System Information & Debug Page</h1>
            
            <div class="warning">
                <strong>WARNING:</strong> This page should NEVER be publicly accessible!<br>
                It contains sensitive configuration and secret keys.
            </div>
            
            <h2>Environment Variables</h2>
            <table>
                <tr>
                    <th>Variable</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Python Version</td>
                    <td>{os.sys.version}</td>
                </tr>
                <tr>
                    <td>Operating System</td>
                    <td>{os.name} - {os.sys.platform}</td>
                </tr>
                <tr>
                    <td>Current Working Directory</td>
                    <td>{os.getcwd()}</td>
                </tr>
                <tr>
                    <td>Server Software</td>
                    <td>Uvicorn/FastAPI (Production)</td>
                </tr>
            </table>
            
            <h2>🔑 Sensitive Configuration (EXPOSED!)</h2>
            <table>
                <tr>
                    <th>Key</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>API Secret Key</td>
                    <td class="secret">{SECRET_API_KEY}</td>
                </tr>
                <tr>
                    <td>Database Password</td>
                    <td class="secret">{DATABASE_PASSWORD}</td>
                </tr>
                <tr>
                    <td>AWS Secret Key</td>
                    <td class="secret">{AWS_SECRET_KEY}</td>
                </tr>
                <tr>
                    <td>Admin Panel URL</td>
                    <td class="secret">/admin/secret_panel</td>
                </tr>
                <tr>
                    <td>Database Host</td>
                    <td class="secret">db.internal.company.com:5432</td>
                </tr>
                <tr>
                    <td>Redis Cache</td>
                    <td class="secret">redis://10.0.0.5:6379</td>
                </tr>
            </table>
            
            <h2>Path Information</h2>
            <table>
                <tr>
                    <th>Path Type</th>
                    <th>Location</th>
                </tr>
                <tr>
                    <td>Application Root</td>
                    <td>{os.getcwd()}</td>
                </tr>
                <tr>
                    <td>Config Files</td>
                    <td>{os.path.join(os.getcwd(), 'config')}</td>
                </tr>
                <tr>
                    <td>Log Files</td>
                    <td>/var/log/application/</td>
                </tr>
                <tr>
                    <td>Backup Location</td>
                    <td>/var/backups/db/</td>
                </tr>
            </table>
            
            <div style="margin-top: 30px; padding: 15px; background: #f8d7da; border-radius: 5px; border: 2px solid #dc3545;">
                <h3>💀 Critical Vulnerability!</h3>
                <p>An attacker now has:</p>
                <ul>
                    <li>All secret keys and passwords</li>
                    <li>Complete system architecture information</li>
                    <li>Internal network details</li>
                    <li>File system paths</li>
                    <li>Can impersonate services or access databases directly</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/about")
async def about():
    return {"message": "About Us page"}


@app.get("/contact")
async def contact():
    return {"message": "Contact page"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
