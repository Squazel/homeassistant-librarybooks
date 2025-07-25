"""Integration test for Libero scraper."""
import pytest
import asyncio
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from custom_components.library_books.scrapers.libero_scraper import LiberoLibraryScraper

# Test configuration
LIBRARY_URL = os.getenv("LIBRARY_URL", "https://your-library-url.com")
USERNAME = os.getenv("LIBRARY_USERNAME", "your_username")
PASSWORD = os.getenv("LIBRARY_PASSWORD", "your_password")

# Skip test if credentials not provided
pytestmark = pytest.mark.skipif(
    LIBRARY_URL == "https://your-library-url.com" or not all([LIBRARY_URL, USERNAME, PASSWORD]),
    reason="Library credentials not provided via environment variables"
)

@pytest.mark.asyncio
async def test_libero_scraper():
    """Test the Libero scraper with real API calls."""
    
    # Create the scraper
    scraper = LiberoLibraryScraper(
        library_url=LIBRARY_URL,
        username=USERNAME,
        password=PASSWORD
    )
    
    try:
        # Test login
        login_success = await scraper.login()
        print(f"Login successful: {login_success}")
        assert login_success is True

        if login_success:
            print("📚 Getting books without force login...")
            books = await scraper.get_outstanding_books(force_login=False)
            print(f"Found {len(books)} books:")
            
            # Validate books structure
            assert isinstance(books, list)
            
            for book in books:
                print(f"  📖 {book.title} by {book.author}")
                print(f"     ISBN: {book.isbn}")
                print(f"     Image URL: {book.image_url}")
                print(f"     Due: {book.due_date}")
                if book.is_overdue:
                    print(f"     ⚠️  OVERDUE by {abs(book.days_until_due)} days")
                else:
                    print(f"     Due in {book.days_until_due} days")
                print()
                
                # Validate book properties
                assert hasattr(book, 'title')
                assert hasattr(book, 'author')
                assert hasattr(book, 'due_date')
                assert isinstance(book.is_overdue, bool)
                assert isinstance(book.days_until_due, int)
        
        # Test with force login
        print("\n🔄 Testing with force login (normal usage)...")
        books_force = await scraper.get_outstanding_books(force_login=True)
        print(f"Found {len(books_force)} books with force login")
        assert isinstance(books_force, list)
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        pytest.fail(f"Scraper test failed: {e}")
    
    finally:
        await scraper.logout()

if __name__ == "__main__":
    # Allow running directly for manual testing
    asyncio.run(test_libero_scraper())