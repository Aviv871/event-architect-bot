from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set

from telegram import User


@dataclass
class EventItem:
    name: str = None
    count: int = 1
    allow_more: bool = False
    assigned_user: User = None


@dataclass
class EventData:
    name: str = None
    admin: User = None
    users: Set[User] = field(default_factory=set)
    items: List[EventItem] = field(default_factory=list)
    due_date: datetime = None
