"""
Application principale Mail Sender.
"""

import customtkinter as ctk

from ..config import COLORS
from ..models import AppState, SMTPConfig
from .theme import setup_theme
from .tabs import DataTab, MessageTab, SendTab


class MailSenderApp(ctk.CTk):
    """Application principale."""

    def __init__(self):
        setup_theme()
        super().__init__()

        self.title("Mail Sender")
        self.geometry("1250x900")
        self.minsize(1100, 800)

        self.app_data = AppState()
        self._build_ui()

    def _build_ui(self):
        """Construit l'interface utilisateur."""
        self._build_header()
        self._build_tabs()

    def _build_header(self):
        """Construit l'en-tête."""
        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Mail Sender",
            font=("Segoe UI", 22, "bold"),
            text_color="white"
        ).pack(side="left", padx=25, pady=15)

        # Toggle dark/light mode
        self.theme_switch = ctk.CTkSwitch(
            header,
            text="Mode sombre",
            font=("Segoe UI", 12),
            text_color="white",
            command=self._toggle_theme,
            onvalue=1,
            offvalue=0
        )
        self.theme_switch.pack(side="right", padx=25, pady=15)

    def _build_tabs(self):
        """Construit les onglets."""
        self.tabview = ctk.CTkTabview(
            self,
            segmented_button_selected_color=COLORS["primary"]
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Créer les onglets
        tab_data = self.tabview.add("1. Donnees")
        tab_message = self.tabview.add("2. Message")
        tab_send = self.tabview.add("3. Envoi")

        # Initialiser les composants
        self.data_tab = DataTab(tab_data, self.app_data)
        self.message_tab = MessageTab(tab_message, self.app_data)
        self.send_tab = SendTab(tab_send, self.app_data, self._get_config)

    def _toggle_theme(self):
        """Bascule entre mode clair et sombre."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def _get_config(self, get_message: bool = False):
        """
        Retourne la configuration email.

        Args:
            get_message: Si True, retourne (subject, body)

        Returns:
            SMTPConfig ou tuple (subject, body)
        """
        if get_message:
            return self.message_tab.get_subject(), self.message_tab.get_body()

        return SMTPConfig(
            server=self.message_tab.get_smtp_server(),
            port=self.message_tab.get_smtp_port(),
            email=self.message_tab.get_email(),
            password=self.message_tab.get_password()
        )

    def run(self):
        """Lance l'application."""
        self.mainloop()
