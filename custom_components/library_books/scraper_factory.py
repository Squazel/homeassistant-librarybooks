import aiohttp
from .library_scraper import BaseLibraryScraper
from .scrapers.libero_scraper import LiberoLibraryScraper
# Import other scrapers as they're implemented

def create_scraper(library_type: str, library_url: str, username: str, password: str, session: aiohttp.ClientSession) -> BaseLibraryScraper:
    """Factory function to create the appropriate scraper based on library type."""
    
    scrapers = {
        "libero": LiberoLibraryScraper,
        # Add other scrapers here
    }
    
    scraper_class = scrapers.get(library_type)
    if not scraper_class:
        raise ValueError(f"Unsupported library type: {library_type}")
    
    return scraper_class(library_url, username, password, session)