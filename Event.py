from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set


@dataclass(frozen=True)
class EventUser:
    id: int = None
    full_name: str = None


@dataclass
class EventItem:
    name: str = None
    count: int = 1
    allow_more: bool = False
    assigned_user: EventUser = None

    def __post_init__(self):
        # Make sure the that when we load the json data from the disk
        # we convert it correctly from dict to the dataclasses types
        if self.assigned_user:
            self.assigned_user = EventUser(**self.assigned_user)


@dataclass
class EventData:
    name: str = None
    admin: EventUser = None
    users: Set[EventUser] = field(default_factory=set)
    items: List[EventItem] = field(default_factory=list)
    due_date: datetime = None

    def __post_init__(self):
        # Make sure the that when we load the json data from the disk
        # we convert it correctly from dict to the dataclasses types
        for inedx, item in enumerate(self.items):
            self.items[inedx] = EventItem(**item)
        for inedx, user in enumerate(self.users):
            self.users[inedx] = EventUser(**user)
        self.users = set(self.users)
        if self.admin:
            self.admin = EventUser(**self.admin)


@dataclass
class Events:
    events: Dict[str, EventData] = field(default_factory=dict)

    def __post_init__(self):
        # Make sure the that when we load the json data from the disk
        # we convert it correctly from dict to the dataclasses types
        for key in self.events.keys():
            self.events[key] = EventData(**self.events[key])
