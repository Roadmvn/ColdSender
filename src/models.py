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
class AppState:
    """État global de l'application."""
    smtp: SMTPConfig = field(default_factory=SMTPConfig)
    recipients: List[Recipient] = field(default_factory=list)
    subject: str = "Information importante"
    body: str = "Bonjour {{prenom}},\n\nJ'espere que vous allez bien.\n\nJe me permets de vous contacter concernant votre dossier.\nN'hesitez pas a revenir vers moi si vous avez des questions.\n\nBien cordialement,\nL'equipe"
    default_image: Optional[bytes] = None
