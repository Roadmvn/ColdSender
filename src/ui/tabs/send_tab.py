"""
Onglet Envoi - Envoi des emails et résultats.
"""

import time
import threading
import customtkinter as ctk

from ...config import COLORS
from ...models import AppState, SMTPConfig, Recipient, SendStatus
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
        """Section résumé et boutons."""
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
            width=140,
            fg_color=COLORS["gray"],
            hover_color="#4b5563",
            command=self.update_summary
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Test",
            width=140,
            command=self._send_test
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="ENVOYER A TOUS",
            width=200,
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
        """Section résultats en deux colonnes."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Resultats",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        columns_frame = ctk.CTkFrame(frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Colonne succès
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

        # Colonne échecs
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
        """Met à jour le résumé."""
        count = len(self.app_data.recipients)
        has_img = "Oui" if self.app_data.default_image else "Non"
        custom_count = len(self.app_data.custom_images)

        self.summary_text.configure(
            text=f"{count} destinataires  |  Image: {has_img}  |  Images perso: {custom_count}"
        )

    def _log_success(self, text: str):
        """Ajoute une entrée dans la liste des succès."""
        self.success_list.configure(state="normal")
        self.success_list.insert("end", text + "\n")
        self.success_list.see("end")
        self.success_list.configure(state="disabled")

    def _log_failed(self, text: str):
        """Ajoute une entrée dans la liste des échecs."""
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

    def _send_test(self):
        """Envoie un email de test."""
        config = self.get_config()

        if not config.is_valid():
            self.send_status.configure(
                text="Configure le SMTP (onglet Message)",
                text_color=COLORS["error"]
            )
            return

        self.send_status.configure(text="Envoi du test...", text_color=COLORS["primary"])
        self._clear_logs()
        self.parent.update()

        test_recipient = Recipient(
            email=config.email,
            nom="Dupont",
            prenom="Jean",
            numero="12345"
        )

        subject, body = self.get_config(get_message=True)
        success, error = EmailService.send(
            config,
            test_recipient,
            subject,
            body,
            self.app_data.default_image
        )

        if success:
            self.send_status.configure(
                text=f"Test envoye a {config.email}",
                text_color=COLORS["success"]
            )
            self._log_success(f"{config.email} (TEST)")
        else:
            self.send_status.configure(text=f"Erreur: {error}", text_color=COLORS["error"])
            self._log_failed(f"{config.email}: {error}")

    def _send_all(self):
        """Envoie les emails à tous les destinataires."""
        config = self.get_config()

        if not config.is_valid():
            self.send_status.configure(
                text="Configure le SMTP (onglet Message)",
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
            self.send_status.configure(text="Envoi en cours...", text_color=COLORS["primary"])
            self.progress.set(0)

            subject, body = self.get_config(get_message=True)

            success_count = 0
            failed_count = 0
            total = len(self.app_data.recipients)

            for idx, recipient in enumerate(self.app_data.recipients):
                # Image personnalisée ou par défaut
                img = self.app_data.custom_images.get(
                    recipient.email,
                    self.app_data.default_image
                )

                success, error = EmailService.send(config, recipient, subject, body, img)

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

            # Résultat final
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
