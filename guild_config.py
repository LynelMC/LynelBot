from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

@dataclass
class ModuleConfig:
    verification_enabled: bool = False
    rolepanel_enabled: bool = False
    welcome_enabled: bool = False
    logging_enabled: bool = False
    embed_enabled: bool = True
    moderation_enabled: bool = True
    antispam_enabled: bool = False
    botguard_enabled: bool = False
    ticket_enabled: bool = False
    disaster_enabled: bool = False
    security_enabled: bool = False
    backup_enabled: bool = False

@dataclass
class VerificationConfig:
    role_id: Optional[str] = None
    title: str = "サーバー認証"
    desc: str = "下のボタンを押して認証してください。"
    button_label: str = "認証する"
    button_emoji: str = "✅"

@dataclass
class TicketTypeConfig:
    name: str
    description: str
    emoji: Optional[str] = None
    staff_role_id: Optional[str] = None

@dataclass
class GuildConfig:
    guild_id: str
    modules: ModuleConfig = field(default_factory=ModuleConfig)
    verification: VerificationConfig = field(default_factory=VerificationConfig)
    log_channel_id: Optional[str] = None
    ticket_category_id: Optional[str] = None
    ticket_types: Dict[str, TicketTypeConfig] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, guild_id: str, data: dict):
        modules_data = data.get("modules", {})
        verify_data = data.get("verification", {})
        ticket_types_data = data.get("ticket_types", {})
        
        ticket_types = {
            k: TicketTypeConfig(**v) for k, v in ticket_types_data.items()
        }
        
        return cls(
            guild_id=guild_id,
            modules=ModuleConfig(**modules_data),
            verification=VerificationConfig(**verify_data),
            log_channel_id=data.get("log_channel_id"),
            ticket_category_id=data.get("ticket_category_id"),
            ticket_types=ticket_types
        )
