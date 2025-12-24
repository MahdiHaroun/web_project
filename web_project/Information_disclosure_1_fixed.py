from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

# FIXED: Proper Error Handling Without Information Disclosure

app = FastAPI(
    title="Product API - Secure",
    debug=False  # FIXED: Debug mode disabled in production
)

# Configure logging (logs go to files, not to users)
logging.basicConfig(
    level=logging.ERROR,
    filename='app_errors.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        <title>Product API - Secure</title>
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
            .security-fix {
                background: #d4edda;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #28a745;
            }
            .test-section {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border: 2px solid #2196F3;
            }
            input {
                padding: 10px;
                width: 200px;
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
            }
            button:hover {
                background: #218838;
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
            <h1>✅ Product API (Secure)</h1>
            
            <div class="security-fix">
                <h3>Security Fixes Applied:</h3>
                <ul>
                    <li>✅ Generic error messages (no technical details exposed)</li>
                    <li>✅ No server version information in responses</li>
                    <li>✅ No stack traces sent to clients</li>
                    <li>✅ Detailed errors logged server-side only</li>
                    <li>✅ Input validation before processing</li>
                    <li>✅ Debug mode disabled in production</li>
                </ul>
            </div>
            
            <div class="test-section">
                <h3>🔒 Test the Security:</h3>
                <p>Try entering invalid product IDs - you'll only see generic error messages:</p>
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


# FIXED ENDPOINT: Returns generic error messages without exposing system details
@app.get("/api/product/{product_id}")
async def get_product(product_id: str):
    try:
        # FIXED: Input validation
        try:
            pid = int(product_id)
            if pid < 0:
                raise ValueError("Product ID must be positive")
        except ValueError:
            # FIXED: Generic error message, log details server-side
            logger.warning(f"Invalid product ID format attempted: {product_id}")
            raise HTTPException(
                status_code=400,
                detail="Invalid product ID format. Please provide a valid product ID."
            )
        
        # FIXED: Check existence before accessing
        if pid not in products:
            logger.info(f"Product not found: {pid}")
            raise HTTPException(
                status_code=404,
                detail="Product not found. Please check the product ID and try again."
            )
        
        product = products[pid]
        return JSONResponse(content=product)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # FIXED: Log detailed error server-side, return generic message to client
        logger.error(f"Unexpected error in get_product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred. Please try again later or contact support."
        )


# FIXED: Global exception handler with generic messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # FIXED: Log full details server-side
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "url": str(request.url),
            "method": request.method
        },
        exc_info=True
    )
    
    # FIXED: Return generic error to client
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "support": "If the problem persists, please contact support with timestamp: " + 
                      str(logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None)))
        }
    )


if __name__ == "__main__":
    import uvicorn
    # FIXED: Security headers and no server info exposed
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        server_header=False,  # FIXED: Don't expose server header
        log_level="error"     # FIXED: Minimal logging in production
    )
