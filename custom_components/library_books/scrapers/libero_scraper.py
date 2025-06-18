from datetime import datetime
from typing import List
import logging
import json
import requests
import asyncio
from ..library_scraper import BaseLibraryScraper
from ..models import LibraryBook

_LOGGER = logging.getLogger(__name__)

class LiberoLibraryScraper(BaseLibraryScraper):
    """
    Libero library system scraper.
    Uses requests library internally. Note that attempts to use aiohttp instead of requests were not successful.
    """
    
    # Libero-specific endpoints
    LOGIN_ENDPOINT = "/libero/WebOpac.cls"
    API_ENDPOINT = "/libero/member/self/api.v1.cls"
    
    def __init__(self, library_url: str, username: str, password: str, **kwargs):
        """
        Initialize the Libero scraper.
        
        Note: This scraper uses requests library internally and does not accept
        an external session parameter.
        """
        # Initialize base class with our library parameters and a new requests session
        super().__init__(library_url, username, password, requests.Session())
    
    async def login(self) -> bool:
        """Login to the Libero library system."""
        try:
            def do_login():
                login_url = f"{self.library_url.rstrip('/')}{self.LOGIN_ENDPOINT}"
                login_params = {
                    'ACTION': 'MEMLOGIN',
                    'TONEW': '1',
                    'usernum': self.username,
                    'password': self.password,
                }
                
                _LOGGER.debug(f"Attempting login...")
                response = self.session.post(login_url, params=login_params, allow_redirects=True)
                _LOGGER.debug(f"Login response status: {response.status_code}")
                
                return response.status_code == 200
            
            loop = asyncio.get_running_loop()
            success = await loop.run_in_executor(None, do_login)
            
            if success:
                self._logged_in = True
                _LOGGER.info("Login successful")
            
            return success
            
        except Exception as e:
            _LOGGER.error(f"Login failed with exception: {e}")
            return False
    
    async def get_outstanding_books(self) -> List[LibraryBook]:
        """Get outstanding books from Libero API."""
        try:
            if not self._logged_in:
                login_success = await self.login()
                if not login_success:
                    _LOGGER.error("Not logged in, can't get books")
                    return []
            
            def get_books():
                api_url = f"{self.library_url.rstrip('/')}{self.API_ENDPOINT}"
                _LOGGER.debug(f"Requesting API data from: {api_url}")
                
                response = self.session.get(api_url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    _LOGGER.error(f"Failed to get API data: HTTP {response.status_code}")
                    return None
            
            loop = asyncio.get_running_loop()
            json_data = await loop.run_in_executor(None, get_books)
            
            if json_data:
                return self._parse_libero_api_data(json_data)
            else:
                return []
                
        except Exception as e:
            _LOGGER.error(f"Failed to get outstanding books from API: {e}")
            return []
    
    def _parse_libero_api_data(self, json_data) -> List[LibraryBook]:
        """Parse books from Libero API JSON response."""
        books = []
        
        try:
            _LOGGER.debug(f"Parsing JSON data of type: {type(json_data)}")
            
            # Get the first member's data
            if not isinstance(json_data, dict) or 'members' not in json_data:
                _LOGGER.error("JSON data doesn't contain 'members' key")
                return books
            
            members = json_data.get('members', [])
            if not members:
                _LOGGER.error("No members found in JSON data")
                return books
            
            member = members[0]  # Get first member
            _LOGGER.debug(f"Processing member data with keys: {list(member.keys())}")
            
            # Get loans, loan history, and related barcodes
            loans = member.get('loans', [])
            loan_history = member.get('loanHistory', [])
            related_barcodes = member.get('_related', {}).get('barcodes', [])
            related_rsns = member.get('_related', {}).get('rsns', [])
            
            _LOGGER.debug(f"Found {len(loans)} loans, {len(loan_history)} history items, {len(related_barcodes)} related barcodes")
            
            # Create lookup dictionaries for efficiency
            loan_history_by_barcode = {item.get('Barcode'): item for item in loan_history}
            related_barcodes_by_barcode = {item.get('Barcode'): item for item in related_barcodes}
            related_rsns_by_rsn = {item.get('RSN'): item for item in related_rsns}

            # Process each loan
            for loan in loans:
                try:
                    # Get Barcode
                    barcode = loan.get('Barcode')
                    if not barcode:
                        _LOGGER.warning("Loan missing Barcode, skipping")
                        continue

                    # Get Renewal Count
                    renewal_count = loan.get('RenewalCount', 0)
                    
                    # Get DueDate
                    due_date_str = loan.get('DueDate')
                    if not due_date_str:
                        _LOGGER.warning(f"Loan {barcode} missing DueDate, skipping")
                        continue
                    
                    _LOGGER.debug(f"Processing loan - Barcode: {barcode}, DueDate: {due_date_str}")
                    
                    # Find barcode in loan history
                    #history_item = loan_history_by_barcode.get(barcode)
                    #if not history_item:
                    #    _LOGGER.warning(f"Barcode {barcode} not found in loan history, skipping")
                    #    continue
                    
                    # Find related barcode entry by barcode
                    related_barcode_item = related_barcodes_by_barcode.get(barcode)
                    if not related_barcode_item:
                        _LOGGER.warning(f"Barcode {barcode} not found in related barcodes, skipping")
                        continue
                    
                    # Get RSN
                    rsn = related_barcode_item.get('RSN')
                    if not rsn:
                        _LOGGER.warning(f"RSN not found for barcode {barcode}, skipping")
                        continue
                    
                    # Find related RSN entry to get other metadata
                    rsn_item = related_rsns_by_rsn.get(rsn)
                    if not rsn_item:
                        _LOGGER.warning(f"RSN {rsn} not found in related barcodes by ID, skipping")
                        continue
                    # Get ISBN, Title, Author
                    isbn = rsn_item.get('ISBN').strip()
                    title = rsn_item.get('Title').strip()
                    author = rsn_item.get('AuthorKey', rsn_item.get('MainAuthor', 'Unknown')).strip()
                    # Get image URL
                    image_url = f"{self.library_url}/libero/Cover.cls?type=cover&size=80&isbn={isbn}"

                    # Log the data
                    _LOGGER.info(f"Found book - Barcode: {barcode}, DueDate: {due_date_str}, ISBN: {isbn}, Title: {title}")

                    # Parse due date
                    try:
                        # Try different date formats
                        if 'T' in due_date_str:
                            # ISO format with time
                            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                        else:
                            # Try common date formats
                            try:
                                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                            except ValueError:
                                due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()
                    except ValueError as e:
                        _LOGGER.warning(f"Could not parse due date '{due_date_str}': {e}")
                        continue
                    
                    # Create a temporary book object
                    # TODO: add other fields
                    book = LibraryBook(
                        title=title,
                        author=author,
                        due_date=due_date,
                        isbn=isbn,
                        barcode=barcode,
                        image_url=image_url,
                        renewal_count=renewal_count,
                        renewable=True  # TODO: Implement renewal logic
                    )
                    books.append(book)
                    
                except Exception as e:
                    _LOGGER.error(f"Failed to process loan {barcode}: {e}")
                    continue
        
            _LOGGER.info(f"Successfully parsed {len(books)} books from Libero API")
            
        except Exception as e:
            _LOGGER.error(f"Failed to parse API JSON data: {e}")
        
        return books
    
    async def renew_book(self, book: LibraryBook) -> bool:
        """Attempt to renew a book in Libero system."""
        # TODO: Implement renewal logic using requests
        return False
        
    async def logout(self) -> None:
        """Logout from the library system."""
        self._logged_in = False
        
        def close_session():
            if self.session:
                self.session.close()
            
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, close_session)
        self.session = None