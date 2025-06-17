import asyncio
from time import sleep
import aiohttp
import logging
import os
from pathlib import Path

# Add the project root to Python path so we can import our modules
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from custom_components.library_books.scrapers.libero_scraper import LiberoLibraryScraper

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def test_libero_scraper():
    """Test the Libero scraper."""
    
    # Get credentials from environment variables for security
    LIBRARY_URL = os.getenv("LIBRARY_URL", "https://your-library-url.com")
    USERNAME = os.getenv("LIBRARY_USERNAME", "your_username")
    PASSWORD = os.getenv("LIBRARY_PASSWORD", "your_password")
    
    if LIBRARY_URL == "https://your-library-url.com":
        print("⚠️  Please set environment variables:")
        print("   LIBRARY_URL=https://your-library.com")
        print("   LIBRARY_USERNAME=your_username")
        print("   LIBRARY_PASSWORD=your_password")
        return
    
    async with aiohttp.ClientSession() as session:
        scraper = LiberoLibraryScraper(
            library_url=LIBRARY_URL,
            username=USERNAME,
            password=PASSWORD,
            session=session
        )
        
        try:
            print("Testing login...")
            login_success = await scraper.login()
            print(f"Login successful: {login_success}")
            
            if login_success:
                print("Getting outstanding books...")
                books = await scraper.get_outstanding_books()
                print(f"Found {len(books)} books:")
                
                for book in books:
                    print(f"  📚 {book.title}")
                    print(f"     Author: {book.author}")
                    print(f"     Due: {book.due_date}")
                    if book.is_overdue:
                        print(f"     ⚠️  OVERDUE by {abs(book.days_until_due)} days")
                    else:
                        print(f"     Due in {book.days_until_due} days")
                    print()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await scraper.logout()

if __name__ == "__main__":
    asyncio.run(test_libero_scraper())