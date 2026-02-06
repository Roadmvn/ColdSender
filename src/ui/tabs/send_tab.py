"""
Onglet Envoi - Envoi des emails et resultats.
"""

import io
import time
import threading
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image

from ...config import COLORS
from ...models import AppState, SMTPConfig, SendGridConfig, Recipient, SendStatus
from ...services import EmailService


class SendTab:
    """Onglet d'envoi des emails."""

    def __init__(self, parent: ctk.CTkFrame, app_data: AppState, get_config_func):
        self.parent = parent
        self.app_data = app_data
        self.get_config = get_config_func
        self._build()

    def _build(self):
        """Construit l'interface de l'onglet."""
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_summary_section(container)
        self._build_progress_section(container)
        self._build_results_section(container)

    def _build_summary_section(self, parent: ctk.CTkFrame):
        """Section resume et boutons."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame,
            text="Resume",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.summary_text = ctk.CTkLabel(
            frame,
            text="0 destinataires  |  Image: Non  |  Images perso: 0",
            font=("Segoe UI", 12)
        )
        self.summary_text.pack(anchor="w", padx=20, pady=(0, 15))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Actualiser",
            width=100,
            fg_color=COLORS["gray"],
            hover_color="#4b5563",
            command=self.update_summary
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Preview",
            width=100,
            fg_color=COLORS["primary"],
            command=self._show_preview
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Test",
            width=100,
            command=self._send_test
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="ENVOYER A TOUS",
            width=180,
            fg_color=COLORS["success"],
            hover_color="#047857",
            font=("Segoe UI", 13, "bold"),
            command=self._send_all
        ).pack(side="left")

    def _build_progress_section(self, parent: ctk.CTkFrame):
        """Section progression."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            frame,
            text="Progression",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.progress = ctk.CTkProgressBar(frame, height=20)
        self.progress.pack(fill="x", padx=20, pady=(0, 10))
        self.progress.set(0)

        self.send_status = ctk.CTkLabel(
            frame,
            text="En attente...",
            font=("Segoe UI", 12),
            text_color=COLORS["gray"]
        )
        self.send_status.pack(anchor="w", padx=20, pady=(0, 15))

    def _build_results_section(self, parent: ctk.CTkFrame):
        """Section resultats en deux colonnes."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Resultats",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        columns_frame = ctk.CTkFrame(frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Colonne succes
        success_frame = ctk.CTkFrame(columns_frame)
        success_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            success_frame,
            text="Envoyes",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["success"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.success_list = ctk.CTkTextbox(success_frame, font=("Consolas", 10), state="disabled")
        self.success_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Colonne echecs
        failed_frame = ctk.CTkFrame(columns_frame)
        failed_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            failed_frame,
            text="Echoues",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["error"]
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.failed_list = ctk.CTkTextbox(failed_frame, font=("Consolas", 10), state="disabled")
        self.failed_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def update_summary(self):
        """Met a jour le resume."""
        count = len(self.app_data.recipients)
        has_img = "Oui" if self.app_data.default_image else "Non"
        # Compter les destinataires avec des images personnalisees
        custom_count = sum(1 for r in self.app_data.recipients if r.images)
        # Total d'images perso
        total_images = sum(len(r.images) for r in self.app_data.recipients)

        self.summary_text.configure(
            text=f"{count} destinataires  |  Image defaut: {has_img}  |  {custom_count} avec images perso ({total_images} total)"
        )

    def _show_preview(self):
        """Affiche la preview du mail pour un destinataire."""
        if not self.app_data.recipients:
            messagebox.showwarning("Attention", "Aucun destinataire")
            return

        PreviewDialog(
            self.parent,
            self.app_data,
            self.get_config
        )

    def _log_success(self, text: str):
        """Ajoute une entree dans la liste des succes."""
        self.success_list.configure(state="normal")
        self.success_list.insert("end", text + "\n")
        self.success_list.see("end")
        self.success_list.configure(state="disabled")

    def _log_failed(self, text: str):
        """Ajoute une entree dans la liste des echecs."""
        self.failed_list.configure(state="normal")
        self.failed_list.insert("end", text + "\n")
        self.failed_list.see("end")
        self.failed_list.configure(state="disabled")

    def _clear_logs(self):
        """Vide les logs."""
        self.success_list.configure(state="normal")
        self.success_list.delete("1.0", "end")
        self.success_list.configure(state="disabled")
        self.failed_list.configure(state="normal")
        self.failed_list.delete("1.0", "end")
        self.failed_list.configure(state="disabled")

    def _send_email(self, config, recipient, subject, body, default_image, personal_images):
        """Envoie un email via le bon provider."""
        if isinstance(config, SendGridConfig):
            return EmailService.send_sendgrid(
                config, recipient, subject, body,
                default_image=default_image,
                personal_images=personal_images
            )
        return EmailService.send(
            config, recipient, subject, body,
            default_image=default_image,
            personal_images=personal_images
        )

    def _send_test(self):
        """Envoie un email de test."""
        config = self.get_config()

        if not config.is_valid():
            self.send_status.configure(
                text="Configure l'email (onglet Message)",
                text_color=COLORS["error"]
            )
            return

        self.send_status.configure(text="Envoi du test...", text_color=COLORS["primary"])
        self._clear_logs()
        self.parent.update()

        # Email du test = email de l'expediteur
        test_email = config.from_email if isinstance(config, SendGridConfig) else config.email

        test_recipient = Recipient(
            email=test_email,
            nom="Dupont",
            prenom="Jean",
            numero="12345"
        )

        subject, body = self.get_config(get_message=True)
        success, error = self._send_email(
            config, test_recipient, subject, body,
            default_image=self.app_data.default_image,
            personal_images=None
        )

        if success:
            self.send_status.configure(
                text=f"Test envoye a {test_email}",
                text_color=COLORS["success"]
            )
            self._log_success(f"{test_email} (TEST)")
        else:
            self.send_status.configure(text=f"Erreur: {error}", text_color=COLORS["error"])
            self._log_failed(f"{test_email}: {error}")

    def _send_all(self):
        """Envoie les emails a tous les destinataires."""
        config = self.get_config()

        if not config.is_valid():
            self.send_status.configure(
                text="Configure l'email (onglet Message)",
                text_color=COLORS["error"]
            )
            return

        if not self.app_data.recipients:
            self.send_status.configure(
                text="Importe des destinataires (onglet Donnees)",
                text_color=COLORS["error"]
            )
            return

        def do_send():
            self._clear_logs()
            provider_name = "SendGrid" if isinstance(config, SendGridConfig) else "SMTP"
            self.send_status.configure(
                text=f"Envoi en cours via {provider_name}...",
                text_color=COLORS["primary"]
            )
            self.progress.set(0)

            subject, body = self.get_config(get_message=True)

            success_count = 0
            failed_count = 0
            total = len(self.app_data.recipients)

            for idx, recipient in enumerate(self.app_data.recipients):
                # Image par defaut + images personnalisees du destinataire
                success, error = self._send_email(
                    config,
                    recipient,
                    subject,
                    body,
                    default_image=self.app_data.default_image,
                    personal_images=recipient.images if recipient.images else None
                )

                if success:
                    recipient.status = SendStatus.SUCCESS
                    success_count += 1
                    self._log_success(f"{recipient.prenom} {recipient.nom} <{recipient.email}>")
                else:
                    recipient.status = SendStatus.FAILED
                    recipient.error = error
                    failed_count += 1
                    self._log_failed(f"{recipient.email}: {error}")

                self.progress.set((idx + 1) / total)
                self.parent.update()
                time.sleep(0.5)

            # Resultat final
            if failed_count == 0:
                self.send_status.configure(
                    text=f"Termine ! {success_count} envoyes",
                    text_color=COLORS["success"]
                )
            else:
                self.send_status.configure(
                    text=f"{success_count} envoyes, {failed_count} echoues",
                    text_color=COLORS["warning"]
                )

        threading.Thread(target=do_send, daemon=True).start()


class PreviewDialog(ctk.CTkToplevel):
    """Dialog de preview du mail pour un destinataire."""

    def __init__(self, parent, app_data: AppState, get_config_func):
        super().__init__(parent)
        self.app_data = app_data
        self.get_config = get_config_func

        self.title("Preview du mail")
        self.geometry("800x600")
        self.resizable(True, True)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Construit l'interface."""
        # Selecteur de destinataire
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            top_frame,
            text="Destinataire:",
            font=("Segoe UI", 12)
        ).pack(side="left", padx=(0, 10))

        # Liste des destinataires
        recipients_list = [f"{r.prenom} {r.nom} <{r.email}>" for r in self.app_data.recipients]
        self.recipient_var = ctk.StringVar(value=recipients_list[0] if recipients_list else "")

        self.recipient_combo = ctk.CTkComboBox(
            top_frame,
            values=recipients_list,
            variable=self.recipient_var,
            width=400,
            command=self._on_recipient_change
        )
        self.recipient_combo.pack(side="left", padx=(0, 10))

        # Zone de preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Sujet
        ctk.CTkLabel(
            preview_frame,
            text="Sujet:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.subject_label = ctk.CTkLabel(
            preview_frame,
            text="",
            font=("Segoe UI", 12),
            anchor="w",
            justify="left"
        )
        self.subject_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Corps
        ctk.CTkLabel(
            preview_frame,
            text="Corps du message:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.body_text = ctk.CTkTextbox(
            preview_frame,
            font=("Segoe UI", 11),
            wrap="word",
            height=150
        )
        self.body_text.pack(fill="x", padx=15, pady=(0, 10))

        # Images
        ctk.CTkLabel(
            preview_frame,
            text="Images jointes:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.images_scroll = ctk.CTkScrollableFrame(
            preview_frame,
            fg_color=COLORS["light_gray"],
            corner_radius=8,
            height=200
        )
        self.images_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Afficher la preview du premier destinataire
        if self.app_data.recipients:
            self._update_preview(self.app_data.recipients[0])

    def _on_recipient_change(self, selection):
        """Change le destinataire selectionne."""
        # Trouver l'index du destinataire
        for i, r in enumerate(self.app_data.recipients):
            if f"{r.prenom} {r.nom} <{r.email}>" == selection:
                self._update_preview(r)
                break

    def _update_preview(self, recipient: Recipient):
        """Met a jour la preview pour un destinataire."""
        subject, body = self.get_config(get_message=True)

        # Sujet personnalise
        personalized_subject = EmailService.replace_placeholders(subject, recipient)
        self.subject_label.configure(text=personalized_subject)

        # Corps personnalise
        personalized_body = EmailService.replace_placeholders(body, recipient)
        self.body_text.configure(state="normal")
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", personalized_body)
        self.body_text.configure(state="disabled")

        # Images
        for widget in self.images_scroll.winfo_children():
            widget.destroy()

        # Image par defaut
        if self.app_data.default_image:
            self._add_image_preview("Image par defaut (tous)", self.app_data.default_image, COLORS["primary"])

        # Images personnalisees
        if recipient.images:
            for idx, (img_data, img_name) in enumerate(recipient.images):
                self._add_image_preview(f"Image perso: {img_name}", img_data, COLORS["success"])

        if not self.app_data.default_image and not recipient.images:
            ctk.CTkLabel(
                self.images_scroll,
                text="Aucune image",
                text_color=COLORS["gray"]
            ).pack(pady=20)

    def _add_image_preview(self, title: str, img_data: bytes, color: str):
        """Ajoute une preview d'image."""
        card = ctk.CTkFrame(self.images_scroll, fg_color="white", corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)

        try:
            img = Image.open(io.BytesIO(img_data))
            max_size = 80
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(light_image=img, size=new_size)

            img_label = ctk.CTkLabel(card, image=ctk_image, text="")
            img_label.image = ctk_image
            img_label.pack(side="left", padx=10, pady=10)

        except Exception:
            ctk.CTkLabel(
                card,
                text="[Erreur]",
                text_color=COLORS["error"],
                width=80
            ).pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 11),
            text_color=color
        ).pack(side="left", padx=10, pady=10)
