from dataclasses import dataclass, asdict
from typing import Optional, List
import datetime

@dataclass
class PunishmentRecord:
    user_id: str
    action: str
    executor_id: str
    reason: str
    timestamp: str
    duration: Optional[int] = None # minutes
    
    def to_dict(self):
        return asdict(self)

@dataclass
class RoleRestriction:
    member_id: str
    removed_role_ids: List[str]
    until: Optional[str] # ISO format
    reason: str
    status: str = "active" # active, completed, member_left
    
    def to_dict(self):
        return asdict(self)
