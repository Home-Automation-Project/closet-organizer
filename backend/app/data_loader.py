"""
JSON data loader module - replaces database/ORM for static data
"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "json"


class DataLoader:
    """Load and cache static JSON data files."""
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def load_json(cls, filename: str) -> Dict[str, Any]:
        """Load JSON file from cache or disk."""
        if filename in cls._cache:
            return cls._cache[filename]
        
        file_path = DATA_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        cls._cache[filename] = data
        return data
    
    @classmethod
    def get_closets(cls) -> List[Dict[str, Any]]:
        """Get all closets."""
        data = cls.load_json("closets.json")
        return data.get("closets", [])
    
    @classmethod
    def get_closet(cls, closet_id: str) -> Optional[Dict[str, Any]]:
        """Get a single closet by ID."""
        closets = cls.get_closets()
        for closet in closets:
            if closet["id"] == closet_id:
                return closet
        return None
    
    @classmethod
    def get_family_members(cls) -> List[Dict[str, Any]]:
        """Get all family members."""
        data = cls.load_json("family.json")
        return data.get("members", [])
    
    @classmethod
    def get_family_member(cls, member_id: str) -> Optional[Dict[str, Any]]:
        """Get a single family member by ID."""
        members = cls.get_family_members()
        for member in members:
            if member["id"] == member_id:
                return member
        return None
    
    @classmethod
    def get_first_aid_basic_items(cls) -> List[Dict[str, Any]]:
        """Get basic first aid kit items."""
        data = cls.load_json("firstaid.json")
        return data.get("basicKit", {}).get("items", [])
    
    @classmethod
    def get_first_aid_advanced_bins(cls) -> List[Dict[str, Any]]:
        """Get advanced first aid kit bins."""
        data = cls.load_json("firstaid.json")
        return data.get("advancedKit", {}).get("bins", [])
    
    @classmethod
    def get_first_aid_advanced_items(cls, sub_bin: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get advanced first aid kit items, optionally filtered by sub-bin."""
        data = cls.load_json("firstaid.json")
        items = data.get("advancedKit", {}).get("items", [])
        
        if sub_bin:
            items = [item for item in items if item.get("subBin") == sub_bin]
        
        return items
    
    @classmethod
    def get_cleaning_rooms(cls) -> List[Dict[str, Any]]:
        """Get all cleaning rooms."""
        data = cls.load_json("cleaning.json")
        return data.get("rooms", [])
    
    @classmethod
    def get_cleaning_room(cls, room_id: str) -> Optional[Dict[str, Any]]:
        """Get a single cleaning room by ID."""
        rooms = cls.get_cleaning_rooms()
        for room in rooms:
            if room["id"] == room_id:
                return room
        return None
