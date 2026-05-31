"""Web scraper for Agents Claw Mini."""

import asyncio
import logging
import aiohttp
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .config import BrowserConfig
from .memory import Memory
from .exceptions import ScrapingException

logger = logging.getLogger("AgentsClawMini.Scraper")

@dataclass
class ScrapedData:
    """Scraped data from a web page."""
    url: str
    title: str
    text: str
    html: str
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    tables: List[List[List[str]]]
    metadata: Dict[str, Any]

class Scraper:
    """
    Web scraper untuk ekstraksi data dari website.

    Features:
    - Static scraping (requests + BeautifulSoup)
    - Dynamic scraping (browser automation)
    - Recursive crawling
    - Data extraction (text, links, images, tables)
    - Rate limiting
    - Proxy support
    """

    def __init__(self, config: Optional[BrowserConfig] = None, memory: Optional[Memory] = None):
        self.config = config or BrowserConfig()
        self.memory = memory
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = asyncio.Semaphore(5)  # Max 5 concurrent requests

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {
                "User-Agent": self.config.user_agent or 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session

    async def scrape(self, url: str, selector: Optional[str] = None) -> ScrapedData:
        """Scrape a single URL."""
        async with self._rate_limiter:
            try:
                async with self.session.get(url, proxy=self.config.proxy) as resp:
                    if resp.status != 200:
                        raise ScrapingException(f"HTTP {resp.status} untuk {url}")

                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extract data
                    data = self._extract_data(soup, url, selector)

                    # Save to memory
                    if self.memory:
                        await self.memory.add("scraped", {
                            "url": url,
                            "title": data.title,
                            "text": data.text[:1000],  # Summary
                        })

                    logger.info("🔍 Scraped: %s | Title: %s", url, data.title)
                    return data

            except Exception as e:
                raise ScrapingException(f"Gagal scrape {url}: {e}")

    def _extract_data(self, soup: BeautifulSoup, url: str, selector: Optional[str] = None) -> ScrapedData:
        """Extract data from BeautifulSoup object."""
        # Apply selector if provided
        if selector:
            soup = soup.select_one(selector) or soup

        # Title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""

        # Text content
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)

        # Links
        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            links.append({
                "url": href,
                "text": a.get_text(strip=True),
                "title": a.get('title', ''),
            })

        # Images
        images = []
        for img in soup.find_all('img', src=True):
            src = urljoin(url, img['src'])
            images.append({
                "url": src,
                "alt": img.get('alt', ''),
                "title": img.get('title', ''),
            })

        # Tables
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)

        # Metadata
        metadata = {
            "charset": soup.meta.get('charset') if soup.meta else None,
            "description": soup.find('meta', attrs={'name': 'description'}),
            "keywords": soup.find('meta', attrs={'name': 'keywords'}),
        }

        return ScrapedData(
            url=url,
            title=title_text,
            text=text,
            html=str(soup),
            links=links,
            images=images,
            tables=tables,
            metadata=metadata,
        )

    async def crawl(self, start_url: str, max_pages: int = 10, 
                    same_domain: bool = True,
                    callback: Optional[Callable] = None) -> List[ScrapedData]:
        """Crawl website recursively."""
        visited = set()
        to_visit = [start_url]
        results = []

        domain = urlparse(start_url).netloc

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue

            visited.add(url)

            try:
                data = await self.scrape(url)
                results.append(data)

                if callback:
                    await callback(data)

                # Add new links to queue
                for link in data.links:
                    link_url = link["url"]
                    if link_url not in visited:
                        if same_domain:
                            if urlparse(link_url).netloc == domain:
                                to_visit.append(link_url)
                        else:
                            to_visit.append(link_url)

            except Exception as e:
                logger.error("Error crawling %s: %s", url, e)
                continue

        logger.info("🕷️ Crawl complete: %d pages scraped", len(results))
        return results

    async def extract_json(self, url: str, json_path: Optional[str] = None) -> Any:
        """Extract JSON data from URL."""
        async with self._rate_limiter:
            try:
                async with self.session.get(url, proxy=self.config.proxy) as resp:
                    data = await resp.json()

                    if json_path:
                        # Navigate JSON path (e.g., "data.items.0.name")
                        parts = json_path.split('.')
                        for part in parts:
                            if part.isdigit():
                                data = data[int(part)]
                            else:
                                data = data.get(part, {})

                    return data

            except Exception as e:
                raise ScrapingException(f"Gagal extract JSON dari {url}: {e}")

    async def search(self, query: str, engine: str = "duckduckgo") -> List[Dict[str, str]]:
        """Search web using search engine."""
        if engine == "duckduckgo":
            return await self._search_duckduckgo(query)
        else:
            raise ScrapingException(f"Search engine '{engine}' tidak didukung")

    async def _search_duckduckgo(self, query: str) -> List[Dict[str, str]]:
        """Search using DuckDuckGo."""
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        async with self.session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")

            results = []
            for result in soup.find_all('div', class_='result'):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get('href', ''),
                        "snippet": snippet_elem.get_text(strip=True),
                    })

            return results

    async def close(self):
        """Close scraper."""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("🔍 Scraper closed")

    def __repr__(self):
        return f"Scraper(proxy={self.config.proxy is not None})"
