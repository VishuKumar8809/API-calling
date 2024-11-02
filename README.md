# API-calling Web Crawler Service
A high-performance, asynchronous web crawler service with a RESTful API interface. The service crawls web pages up to a specified depth and returns a structured JSON response containing all discovered links.
Features

🚀 Asynchronous crawling for high performance
🛡️ Rate limiting to prevent server overload
🌐 Same-domain crawling only
⚡ Concurrent page processing
📊 Depth-based link organization
✅ Input validation and error handling
🔍 Swagger UI documentation
💪 Connection pooling and timeout handling

Prerequisites

Python 3.8+
pip package manager

Installation

Clone the repository:

bashCopygit clone https://github.com/yourusername/web-crawler-service.git
cd web-crawler-service

Create and activate a virtual environment (optional but recommended):

bashCopypython -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

Install dependencies:

bashCopypip install fastapi uvicorn httpx beautifulsoup4 ratelimit
Usage
Starting the Server

Run the server locally:

bashCopyuvicorn crawler:app --host 0.0.0.0 --port 8000

Access the API documentation:


Open your browser and navigate to http://localhost:8000/docs

API Endpoints
POST /api/v1/crawl
Crawls a website starting from the provided URL up to the specified depth.
Request Body:
jsonCopy{
    "root_url": "https://example.com",
    "max_depth": 2
}
Response:
jsonCopy{
    "root_url": "https://example.com",
    "max_depth": 2,
    "total_links": 42,
    "crawl_time_seconds": 3.14,
    "links_by_depth": {
        "0": ["https://example.com"],
        "1": ["https://example.com/page1", "https://example.com/page2"],
        "2": ["https://example.com/page1/subpage"]
    },
    "errors": []
}
GET /health
Health check endpoint to verify service status.
Response:
jsonCopy{
    "status": "healthy"
}
Example Usage
Using curl:
bashCopycurl -X POST "http://localhost:8000/api/v1/crawl" \
     -H "Content-Type: application/json" \
     -d '{"root_url": "https://example.com", "max_depth": 2}'
Using Python:
pythonCopyimport requests

response = requests.post(
    "http://localhost:8000/api/v1/crawl",
    json={
        "root_url": "https://example.com",
        "max_depth": 2
    }
)
print(response.json())
Using JavaScript:
javascriptCopyfetch('http://localhost:8000/api/v1/crawl', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        root_url: 'https://example.com',
        max_depth: 2
    }),
})
.then(response => response.json())
.then(data => console.log(data));
Deployment
Local Development

Clone the repository
Install dependencies
Run the server using uvicorn
Access via localhost:8000

Production Deployment
For production deployment, consider the following:

Use a production-grade ASGI server like Gunicorn:

bashCopygunicorn crawler:app -w 4 -k uvicorn.workers.UvicornWorker

Set up environment variables:

bashCopyexport MAX_CONNECTIONS=10
export RATE_LIMIT_CALLS=100
export RATE_LIMIT_PERIOD=60

Use a reverse proxy (Nginx/Apache)
Set up SSL/TLS certificates
Configure proper security measures

Configuration
The service can be configured using environment variables:

MAX_DEPTH: Maximum allowed crawl depth (default: 5)
RATE_LIMIT_CALLS: Number of allowed calls per period (default: 100)
RATE_LIMIT_PERIOD: Rate limit period in seconds (default: 60)
MAX_CONNECTIONS: Maximum concurrent connections (default: 10)
