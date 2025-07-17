#!/usr/bin/env python3

import asyncio
import logging
import re
import os
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT=os.getenv("PORT", 8000)

# Initialize FastMCP server
mcp = FastMCP("CRC Documentation Server", host="0.0.0.0", port=PORT)

# Documentation sources
DOC_SOURCES = {
    "crc": "https://crc.dev/docs",
    "crc-blog": "https://crc.dev/blog", 
    "crc-dev": "https://crc.dev/engineering-docs"
}

# Global cache and session
doc_cache = {}
session = None

async def get_session():
    """Get or create HTTP session"""
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

def extract_text_content(html_content: str) -> str:
    """Extract readable text content from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.decompose()
    
    # Get main content
    main_content = (
        soup.find('main') or 
        soup.find('article') or 
        soup.find('div', class_='content') or
        soup.find('div', class_='documentation') or
        soup.body or
        soup
    )
    
    # Extract and clean text
    text = main_content.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

async def fetch_documentation(source_name: str) -> str:
    """Fetch documentation from a specific source"""
    if source_name not in DOC_SOURCES:
        return f"Unknown source: {source_name}"
    
    url = DOC_SOURCES[source_name]
    session = await get_session()
    
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html_content = await response.text()
                return extract_text_content(html_content)
            else:
                return f"Failed to fetch {url} (Status: {response.status})"
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return f"Error fetching {url}: {str(e)}"

def find_relevant_sections(content: str, query: str) -> List[str]:
    """Find sections relevant to the query"""
    sentences = [s.strip() for s in content.split('.') if s.strip() and len(s.strip()) > 20]
    query_terms = query.lower().split()
    
    relevant_sections = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        score = sum(sentence_lower.count(term) for term in query_terms)
        
        if score > 0:
            relevant_sections.append((sentence, score))
    
    # Sort by relevance and return top sections
    relevant_sections.sort(key=lambda x: x[1], reverse=True)
    return [section[0] for section in relevant_sections[:5]]

@mcp.tool(
    name="crc_doc_query",
    description="Answer questions about CRC (CodeReady Containers) or OpenShift Local using documentation, blogs, and engineering content."
    )
async def crc_doc_query(query: str, sources: List[str] = None) -> str:
    """
    Answer questions about CRC or OpenShift Local

    Args:
        query: query about CRC or OpenShift Local
        sources: Specific doc sources (optional, defaults to all)
    
    Returns:
        Formatted results from CRC documentation
    """
    if not query:
        return "Please provide a query."
    
    if sources is None:
        sources = list(DOC_SOURCES.keys())
    
    results = []
    
    for source_name in sources:
        if source_name not in DOC_SOURCES:
            continue
            
        # Get cached content or fetch new
        if source_name not in doc_cache:
            logger.info(f"Fetching documentation from {source_name}")
            content = await fetch_documentation(source_name)
            doc_cache[source_name] = content
        else:
            content = doc_cache[source_name]
        
        # Find relevant sections
        relevant_sections = find_relevant_sections(content, query)
        
        if relevant_sections:
            results.append({
                "source": source_name,
                "url": DOC_SOURCES[source_name],
                "sections": relevant_sections
            })
    
    # Format response
    if not results:
        return f"No relevant information found for: '{query}'"
    
    response = f"# CRC Documentation Results\n\n**Query:** {query}\n\n"
    
    for result in results:
        source_name = result["source"]
        url = result["url"]
        sections = result["sections"]
        
        response += f"## {source_name.replace('-', ' ').title()}\n"
        response += f"**Source:** {url}\n\n"
        
        for i, section in enumerate(sections, 1):
            response += f"**{i}.** {section}\n\n"
        
        response += "---\n\n"
    
    return response

@mcp.tool()
async def clear_cache() -> str:
    """
    Clear the documentation cache to fetch fresh content
    
    Returns:
        Confirmation message
    """
    global doc_cache
    doc_cache.clear()
    return "Documentation cache cleared. Fresh content will be fetched on next query."

async def cleanup():
    """Clean up resources"""
    global session
    if session:
        await session.close()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")