"""
Modèles de données pour l'application Mail Sender.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum


class SendStatus(Enum):
    """Statut d'envoi d'un email."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Recipient:
    """Represente un destinataire."""
    email: str
    nom: str
    prenom: str
    numero: str
    # Liste d'images: [(data, name), ...]
    images: List[Tuple[bytes, str]] = field(default_factory=list)
    status: SendStatus = SendStatus.PENDING
    error: Optional[str] = None


@dataclass
class SMTPConfig:
    """Configuration du serveur SMTP."""
    server: str = "smtp.gmail.com"
    port: int = 587
    email: str = ""
    password: str = ""

    def is_valid(self) -> bool:
        """Verifie si la configuration est complete."""
        return all([self.server, self.email, self.password])


@dataclass
class SendGridConfig:
    """Configuration SendGrid API."""
    api_key: str = ""
    from_email: str = ""

    def is_valid(self) -> bool:
        """Verifie si la configuration est complete."""
        return all([self.api_key, self.from_email])


@dataclass
class GmailAPIConfig:
    """Configuration Gmail API (OAuth2)."""
    email: str = ""
    credentials_path: str = ""

    def is_valid(self) -> bool:
        """Verifie si la configuration est complete."""
        return bool(self.email)


@dataclass
class AppState:
    """État global de l'application."""
    smtp: SMTPConfig = field(default_factory=SMTPConfig)
    recipients: List[Recipient] = field(default_factory=list)
    subject: str = "Invitation - {{prenom}} {{nom}}"
    body: str = """Bonjour {{prenom}} {{nom}},

Vous êtes cordialement invité(e) à notre événement !

Votre numéro d'enregistrement : {{numero}}

Merci de conserver ce numéro, il vous sera demandé à l'entrée.

À très bientôt !

L'équipe organisatrice"""
    default_image: Optional[bytes] = None
