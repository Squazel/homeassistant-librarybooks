from datetime import datetime
from typing import List
import logging
import json
import aiohttp
from ..library_scraper import BaseLibraryScraper
from ..models import LibraryBook

_LOGGER = logging.getLogger(__name__)

class LiberoLibraryScraper(BaseLibraryScraper):
    """Libero library system scraper."""
    
    # Libero-specific endpoints
    LOGIN_ENDPOINT = "/libero/WebOpac.cls"
    API_ENDPOINT = "/libero/member/self/api.v1.cls"
    
    async def login(self) -> bool:
        """Login to the Libero library system."""
        try:
            login_url = f"{self.library_url.rstrip('/')}{self.LOGIN_ENDPOINT}"
            
            login_params = {
                'ACTION': 'MEMLOGIN',
                'TONEW': '1',
                'usernum': self.username,
                'password': self.password,
            }
            
            _LOGGER.debug(f"Attempting login to: {login_url}")
            
            async with self.session.post(login_url, params=login_params) as response:
                _LOGGER.debug(f"Login response status: {response.status}")
                
                if response.status == 200:
                    self._logged_in = True
                    _LOGGER.info("Login successful")
                    return True
                else:
                    _LOGGER.error(f"Login failed with status: {response.status}")
                    return False
        
        except Exception as e:
            _LOGGER.error(f"Login failed with exception: {e}")
            return False
    
    async def get_outstanding_books(self) -> List[LibraryBook]:
        """Get outstanding books from Libero API."""
        try:
            api_url = f"{self.library_url.rstrip('/')}{self.API_ENDPOINT}"
            
            _LOGGER.debug(f"Requesting API data from: {api_url}")
            
            async with self.session.get(api_url) as response:
                _LOGGER.debug(f"API response status: {response.status}")
                
                if response.status == 200:
                    json_data = await response.json()
                    return self._parse_libero_api_data(json_data)
                else:
                    _LOGGER.error(f"Failed to get API data: HTTP {response.status}")
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
            
            _LOGGER.debug(f"Found {len(loans)} loans, {len(loan_history)} history items, {len(related_barcodes)} related barcodes")
            
            # Create lookup dictionaries for efficiency
            loan_history_by_barcode = {item.get('Barcode'): item for item in loan_history}
            related_barcodes_by_barcode = {item.get('Barcode'): item for item in related_barcodes}
            related_barcodes_by_id = {item.get('ID'): item for item in related_barcodes}
            
            # Process each loan
            for loan in loans:
                try:
                    # Step 2a: Get Barcode
                    barcode = loan.get('Barcode')
                    if not barcode:
                        _LOGGER.warning("Loan missing Barcode, skipping")
                        continue
                    
                    # Step 2b: Get DueDate
                    due_date_str = loan.get('DueDate')
                    if not due_date_str:
                        _LOGGER.warning(f"Loan {barcode} missing DueDate, skipping")
                        continue
                    
                    _LOGGER.debug(f"Processing loan - Barcode: {barcode}, DueDate: {due_date_str}")
                    
                    # Step 2c: Find barcode in loan history
                    history_item = loan_history_by_barcode.get(barcode)
                    if not history_item:
                        _LOGGER.warning(f"Barcode {barcode} not found in loan history, skipping")
                        continue
                    
                    # Step 2d: Find related barcode entry by barcode
                    related_barcode_item = related_barcodes_by_barcode.get(barcode)
                    if not related_barcode_item:
                        _LOGGER.warning(f"Barcode {barcode} not found in related barcodes, skipping")
                        continue
                    
                    # Step 2e: Get RSN
                    rsn = related_barcode_item.get('RSN')
                    if not rsn:
                        _LOGGER.warning(f"RSN not found for barcode {barcode}, skipping")
                        continue
                    
                    # Step 2f: Find related barcode entry by ID = RSN
                    rsn_item = related_barcodes_by_id.get(rsn)
                    if not rsn_item:
                        _LOGGER.warning(f"RSN {rsn} not found in related barcodes by ID, skipping")
                        continue
                    
                    # Step 2g: Get ISBN
                    isbn = rsn_item.get('ISBN')
                    
                    # Step 2h: Log the data
                    _LOGGER.info(f"Found book - Barcode: {barcode}, DueDate: {due_date_str}, ISBN: {isbn}")
                    
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
                    
                    # Create a temporary book object (we'll add more fields later)
                    book = LibraryBook(
                        title=f"Book {barcode}",  # Placeholder - we'll get real title later
                        author="Unknown",  # Placeholder - we'll get real author later
                        due_date=due_date,
                        isbn=isbn,
                        barcode=barcode,
                        renewable=True  # Default for now
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
        # TODO: Implement renewal logic - might use the API endpoint with different parameters
        return False