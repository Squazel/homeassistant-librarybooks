from dataclasses import dataclass
from datetime import date
from typing import Optional
import re

@dataclass
class LibraryBook:
    """Represents a library book with due date information."""
    title: str
    author: str
    due_date: date
    isbn: Optional[str] = None
    barcode: Optional[str] = None
    image_url: Optional[str] = ""
    renewable: bool = True
    renewal_count: int = 0
    fine_amount: float = 0.0
    library_name: Optional[str] = None
    
    def __post_init__(self):
        """Clean up title and author after initialization."""
        # Remove trailing whitespace and special characters from title
        if self.title:
            self.title = re.sub(r'[\s/]+$', '', self.title.strip())
        
        # Also clean up author for consistency
        if self.author:
            self.author = re.sub(r'[\s/]+$', '', self.author.strip())
    
    def __str__(self) -> str:
        """String representation of the book."""
        return f"{self.title} by {self.author} (Due: {self.due_date})"
    
    @property
    def is_overdue(self) -> bool:
        """Check if the book is overdue."""
        from datetime import date
        return self.due_date < date.today()
    
    @property
    def days_until_due(self) -> int:
        """Get number of days until due (negative if overdue)."""
        from datetime import date
        return (self.due_date - date.today()).days