"""
Service d'envoi d'emails.
"""

import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional, Tuple, List

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId, Content, MimeType
)

from ..models import SMTPConfig, SendGridConfig, Recipient


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
    def build_html_preview(
        body: str,
        recipient: Recipient,
        has_default_image: bool,
        personal_images_count: int
    ) -> str:
        """
        Construit le HTML du mail pour preview.

        Args:
            body: Corps du mail avec placeholders
            recipient: Destinataire
            has_default_image: True si image par defaut presente
            personal_images_count: Nombre d'images personnalisees

        Returns:
            HTML du mail personnalise
        """
        personalized_body = EmailService.replace_placeholders(body, recipient)

        img_tags = ""
        if has_default_image:
            img_tags += "<br><p style='color: #3b82f6;'><strong>[Image par defaut]</strong></p>"
        if personal_images_count > 0:
            img_tags += f"<br><p style='color: #10b981;'><strong>[{personal_images_count} image(s) personnalisee(s)]</strong></p>"

        return f"""<div style="font-family: Arial, sans-serif; line-height: 1.6;">
{personalized_body.replace(chr(10), '<br>')}
</div>
{img_tags}"""

    @staticmethod
    def send(
        config: SMTPConfig,
        recipient: Recipient,
        subject: str,
        body: str,
        default_image: Optional[bytes] = None,
        personal_images: Optional[List[Tuple[bytes, str]]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email personnalise avec possibilite de plusieurs images.

        Args:
            config: Configuration SMTP
            recipient: Destinataire avec ses informations
            subject: Sujet du mail (peut contenir des placeholders)
            body: Corps du mail (peut contenir des placeholders)
            default_image: Image par defaut pour tous (optionnel)
            personal_images: Liste d'images personnalisees [(data, name), ...] (optionnel)

        Returns:
            Tuple (success, error_message)
        """
        try:
            # Personnaliser pour CE destinataire
            personalized_subject = EmailService.replace_placeholders(subject, recipient)
            personalized_body = EmailService.replace_placeholders(body, recipient)

            # Creer le message
            msg = MIMEMultipart('related')
            msg['From'] = config.email
            msg['To'] = recipient.email
            msg['Subject'] = personalized_subject

            # Construire les tags images
            img_tags = ""
            if default_image:
                img_tags += "<br><img src='cid:default_image' style='max-width: 600px;'>"

            # Ajouter les images personnalisees
            if personal_images:
                for idx, (img_data, img_name) in enumerate(personal_images):
                    img_tags += f"<br><img src='cid:personal_{idx}' style='max-width: 600px;'>"

            html_body = f"""
            <html><body>
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            {personalized_body.replace(chr(10), '<br>')}
            </div>
            {img_tags}
            </body></html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # Attacher l'image par defaut
            if default_image:
                img = MIMEImage(default_image)
                img.add_header('Content-ID', '<default_image>')
                img.add_header('Content-Disposition', 'inline', filename='default.png')
                msg.attach(img)

            # Attacher les images personnalisees
            if personal_images:
                for idx, (img_data, img_name) in enumerate(personal_images):
                    img = MIMEImage(img_data)
                    img.add_header('Content-ID', f'<personal_{idx}>')
                    img.add_header('Content-Disposition', 'inline', filename=img_name)
                    msg.attach(img)

            # Envoyer
            with smtplib.SMTP(config.server, config.port) as server:
                server.starttls()
                server.login(config.email, config.password)
                server.send_message(msg)

            return True, None

        except Exception as e:
            return False, str(e)

    @staticmethod
    def send_sendgrid(
        config: SendGridConfig,
        recipient: Recipient,
        subject: str,
        body: str,
        default_image: Optional[bytes] = None,
        personal_images: Optional[List[Tuple[bytes, str]]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email via SendGrid API.

        Args:
            config: Configuration SendGrid (api_key, from_email)
            recipient: Destinataire
            subject: Sujet du mail
            body: Corps du mail
            default_image: Image par defaut (optionnel)
            personal_images: Liste d'images perso [(data, name), ...] (optionnel)

        Returns:
            Tuple (success, error_message)
        """
        try:
            personalized_subject = EmailService.replace_placeholders(subject, recipient)
            personalized_body = EmailService.replace_placeholders(body, recipient)

            # Construire le HTML
            img_tags = ""
            if default_image:
                img_tags += "<br><img src='cid:default_image' style='max-width: 600px;'>"
            if personal_images:
                for idx, (img_data, img_name) in enumerate(personal_images):
                    img_tags += f"<br><img src='cid:personal_{idx}' style='max-width: 600px;'>"

            html_content = f"""
            <html><body>
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            {personalized_body.replace(chr(10), '<br>')}
            </div>
            {img_tags}
            </body></html>
            """

            message = Mail(
                from_email=config.from_email,
                to_emails=recipient.email,
                subject=personalized_subject,
                html_content=html_content
            )

            # Ajouter image par defaut
            if default_image:
                attachment = Attachment()
                attachment.file_content = FileContent(base64.b64encode(default_image).decode())
                attachment.file_name = FileName("default.png")
                attachment.file_type = FileType("image/png")
                attachment.disposition = Disposition("inline")
                attachment.content_id = ContentId("default_image")
                message.add_attachment(attachment)

            # Ajouter images personnalisees
            if personal_images:
                for idx, (img_data, img_name) in enumerate(personal_images):
                    attachment = Attachment()
                    attachment.file_content = FileContent(base64.b64encode(img_data).decode())
                    attachment.file_name = FileName(img_name)
                    attachment.file_type = FileType("image/png")
                    attachment.disposition = Disposition("inline")
                    attachment.content_id = ContentId(f"personal_{idx}")
                    message.add_attachment(attachment)

            # Envoyer
            sg = SendGridAPIClient(config.api_key)
            response = sg.send(message)

            if response.status_code in (200, 201, 202):
                return True, None
            else:
                return False, f"SendGrid erreur {response.status_code}: {response.body}"

        except Exception as e:
            return False, str(e)
