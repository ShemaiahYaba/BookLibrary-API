"""
Data models for the Book Library API
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """
    Book data model
    
    Using a dataclass provides:
    - Type safety
    - Auto-generated __init__, __repr__, __eq__
    - Clear field definitions
    - Prevents key errors from dictionaries
    """
    title: str
    author: str
    isbn: str
    year: int
    id: Optional[int] = None
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert Book to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Create Book instance from dictionary"""
        # Only extract fields that belong to Book
        valid_fields = {
            'title', 'author', 'isbn', 'year', 
            'id', 'created_at', 'updated_at'
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def update(self, **kwargs) -> None:
        """Update book fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
