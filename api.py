from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Set
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
from ratelimit import limits, sleep_and_retry

app = FastAPI(
    title="Web Crawler API",
    description="A web crawler service that crawls websites to a specified depth",
    version="1.0.0"
)

class CrawlRequest(BaseModel):
    root_url: HttpUrl
    max_depth: int = 3
    
    class Config:
        json_schema_extra = {
            "example": {
                "root_url": "https://example.com",
                "max_depth": 2
            }
        }

class CrawlResponse(BaseModel):
    root_url: str
    max_depth: int
    total_links: int
    crawl_time_seconds: float
    links_by_depth: Dict[int, List[str]]
    errors: List[str]

@sleep_and_retry
@limits(calls=100, period=60)  # Rate limiting: 100 requests per minute
async def fetch_url(url: str, client: httpx.AsyncClient) -> str:
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching {url}: {str(e)}")

async def extract_links(html: str, base_url: str) -> Set[str]:
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    
    for anchor in soup.find_all('a'):
        href = anchor.get('href')
        if href:
            absolute_url = urljoin(base_url, href)
            # Only include links from the same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.add(absolute_url)
    
    return links

async def crawl_page(url: str, depth: int, max_depth: int, visited: Set[str], 
                    results: Dict[int, List[str]], client: httpx.AsyncClient) -> None:
    if depth > max_depth or url in visited:
        return
    
    visited.add(url)
    if depth not in results:
        results[depth] = []
    results[depth].append(url)
    
    try:
        html = await fetch_url(url, client)
        links = await extract_links(html, url)
        
        # Crawl all extracted links concurrently
        tasks = []
        for link in links:
            if link not in visited:
                task = crawl_page(link, depth + 1, max_depth, visited, results, client)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
    except Exception as e:
        results['errors'].append(f"Error crawling {url}: {str(e)}")

@app.post("/api/v1/crawl", response_model=CrawlResponse)
async def crawl(request: CrawlRequest):
   
    import time
    start_time = time.time()
    
    # Input validation
    if request.max_depth < 0 or request.max_depth > 5:
        raise HTTPException(
            status_code=400, 
            detail="max_depth must be between 0 and 5"
        )
    
    visited = set()
    results = {
        'errors': []
    }
    
    # Use connection pooling and keep-alive
    timeout = httpx.Timeout(10.0)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        await crawl_page(
            str(request.root_url), 
            0, 
            request.max_depth, 
            visited, 
            results, 
            client
        )
    
    # Calculate total links
    total_links = sum(len(links) for depth, links in results.items() 
                     if depth != 'errors')
    
    return CrawlResponse(
        root_url=str(request.root_url),
        max_depth=request.max_depth,
        total_links=total_links,
        crawl_time_seconds=round(time.time() - start_time, 2),
        links_by_depth={k: v for k, v in results.items() if k != 'errors'},
        errors=results['errors']
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)