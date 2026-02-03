"""
Service d'envoi d'emails.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional, Tuple

from ..models import SMTPConfig, Recipient


class EmailService:
    """Service d'envoi d'emails."""

    @staticmethod
    def replace_placeholders(text: str, recipient: Recipient) -> str:
        """Remplace les placeholders par les valeurs du destinataire."""
        result = text
        result = result.replace("{{nom}}", recipient.nom)
        result = result.replace("{{prenom}}", recipient.prenom)
        result = result.replace("{{numero}}", recipient.numero)
        result = result.replace("{{email}}", recipient.email)
        return result

    @staticmethod
    def send(
        config: SMTPConfig,
        recipient: Recipient,
        subject: str,
        body: str,
        image_data: Optional[bytes] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email personnalisé.

        Args:
            config: Configuration SMTP
            recipient: Destinataire avec ses informations
            subject: Sujet du mail (peut contenir des placeholders)
            body: Corps du mail (peut contenir des placeholders)
            image_data: Données binaires de l'image (optionnel)

        Returns:
            Tuple (success, error_message)
        """
        try:
            # Personnaliser pour CE destinataire
            personalized_subject = EmailService.replace_placeholders(subject, recipient)
            personalized_body = EmailService.replace_placeholders(body, recipient)

            # Créer le message
            msg = MIMEMultipart('related')
            msg['From'] = config.email
            msg['To'] = recipient.email
            msg['Subject'] = personalized_subject

            # Construire le corps HTML
            img_tag = ""
            if image_data:
                img_tag = "<br><img src='cid:event_image' style='max-width: 600px;'>"

            html_body = f"""
            <html><body>
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            {personalized_body.replace(chr(10), '<br>')}
            </div>
            {img_tag}
            </body></html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # Attacher l'image si présente
            if image_data:
                img = MIMEImage(image_data)
                img.add_header('Content-ID', '<event_image>')
                img.add_header('Content-Disposition', 'inline', filename='image.png')
                msg.attach(img)

            # Envoyer
            with smtplib.SMTP(config.server, config.port) as server:
                server.starttls()
                server.login(config.email, config.password)
                server.send_message(msg)

            return True, None

        except Exception as e:
            return False, str(e)
