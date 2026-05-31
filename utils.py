"""Utilities for Agents Claw Mini."""

import re
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("AgentsClawMini.Utils")

class Utils:
    """Utility functions untuk Agents Claw Mini."""

    @staticmethod
    def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def clean_html(html: str) -> str:
        """Remove HTML tags."""
        import re
        clean = re.sub(r'<[^>]+>', '', html)
        return clean.strip()

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        return re.findall(url_pattern, text)

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract emails from text."""
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        return re.findall(email_pattern, text)

    @staticmethod
    def hash_text(text: str, algorithm: str = "sha256") -> str:
        """Hash text."""
        if algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def format_json(data: Any, indent: int = 2) -> str:
        """Format data as JSON."""
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

    @staticmethod
    def parse_json(text: str) -> Any:
        """Parse JSON string."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            match = re.search(r'```json
(.*?)
```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            match = re.search(r'```
(.*?)
```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise

    @staticmethod
    def timestamp() -> str:
        """Get current ISO timestamp."""
        return datetime.now().isoformat()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename."""
        return re.sub(r'[^\w\-.]', '_', filename)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: ~4 characters per token
        return len(text) // 4

    @staticmethod
    def mask_api_key(key: str) -> str:
        """Mask API key for display."""
        if len(key) <= 8:
            return "****"
        return key[:4] + "****" + key[-4:]

    @staticmethod
    def retry_async(max_retries: int = 3, delay: float = 1.0):
        """Decorator for async retry."""
        import functools
        import asyncio

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logger.warning("Retry %d/%d after error: %s", attempt + 1, max_retries, e)
                        await asyncio.sleep(delay * (2 ** attempt))
            return wrapper
        return decorator
