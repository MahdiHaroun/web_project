from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import traceback
import sys

# VULNERABLE: Information Disclosure in Error Messages

app = FastAPI(
    title="Product API - Vulnerable",
    debug=True  # VULNERABLE: Debug mode enabled in production
)

class Product(BaseModel):
    id: int
    name: str
    price: float


# Mock product database
products = {
    1: {"id": 1, "name": "Laptop", "price": 999.99},
    2: {"id": 2, "name": "Mouse", "price": 29.99},
    3: {"id": 3, "name": "Keyboard", "price": 79.99}
}


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Product API - Vulnerable</title>
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
            input {
                padding: 10px;
                width: 200px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background: #c82333;
            }
            .result {
                margin-top: 15px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 5px;
                font-family: monospace;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Product API (Vulnerable)</h1>
            
            <div class="vulnerability">
                <h3>Vulnerability: Information Disclosure in Error Messages</h3>
                <p><strong>Description:</strong> Adding unexpected values to the ProductID section gives detailed error messages showing:</p>
                <ul>
                    <li>Web server software version (Uvicorn, Python version)</li>
                    <li>Full stack traces with file paths</li>
                    <li>Internal code structure</li>
                    <li>Database connection details (if present)</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔍 Test the Vulnerability:</h3>
                <p>Try entering invalid product IDs to trigger detailed error messages:</p>
                <input type="text" id="productId" placeholder="Try: abc, -1, 999">
                <button onclick="fetchProduct()">Get Product</button>
                <div id="result" class="result" style="display: none;"></div>
            </div>
            
            <h3>Valid Product IDs:</h3>
            <ul>
                <li>Product 1: Laptop</li>
                <li>Product 2: Mouse</li>
                <li>Product 3: Keyboard</li>
            </ul>
        </div>
        
        <script>
            async function fetchProduct() {
                const productId = document.getElementById('productId').value;
                const resultDiv = document.getElementById('result');
                
                try {
                    const response = await fetch('/api/product/' + productId);
                    const data = await response.text();
                    
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>Response:</strong>\\n' + data;
                } catch (error) {
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<strong>Error:</strong>\\n' + error;
                }
            }
        </script>
    </body>
    </html>
    """


# VULNERABLE ENDPOINT: Exposes detailed error information
@app.get("/api/product/{product_id}")
async def get_product(product_id: str):
    try:
        # VULNERABLE: No input validation, will throw detailed errors
        pid = int(product_id)
        
        # VULNERABLE: Direct database access without error handling
        product = products[pid]
        
        return JSONResponse(content=product)
        
    except ValueError as e:
        # VULNERABLE: Exposes full error details including Python version
        raise HTTPException(
            status_code=400,
            detail=f"Invalid product ID format: {str(e)}\\n"
                   f"Python Version: {sys.version}\\n"
                   f"Server: Uvicorn/FastAPI\\n"
                   f"Traceback: {traceback.format_exc()}"
        )
    except KeyError as e:
        # VULNERABLE: Exposes internal data structure
        raise HTTPException(
            status_code=404,
            detail=f"Product not found: {str(e)}\\n"
                   f"Available product IDs: {list(products.keys())}\\n"
                   f"Database location: /var/db/products.db\\n"
                   f"Traceback: {traceback.format_exc()}"
        )
    except Exception as e:
        # VULNERABLE: Generic catch-all exposing everything
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error\\n"
                   f"Error Type: {type(e).__name__}\\n"
                   f"Error Message: {str(e)}\\n"
                   f"Python: {sys.version}\\n"
                   f"Server: Uvicorn on FastAPI\\n"
                   f"Full Traceback:\\n{traceback.format_exc()}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # VULNERABLE: Global exception handler that exposes everything
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "type": type(exc).__name__,
            "message": str(exc),
            "python_version": sys.version,
            "server": "Uvicorn/FastAPI",
            "request_url": str(request.url),
            "request_method": request.method,
            "traceback": traceback.format_exc()
        }
    )


if __name__ == "__main__":
    import uvicorn
    # VULNERABLE: Debug mode and server info exposed
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        server_header=True  # VULNERABLE: Exposes server header
    )
