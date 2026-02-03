"""
Onglet Message - Rédaction du message et configuration SMTP.
"""

import customtkinter as ctk

from ...config import COLORS, SMTP_PROVIDERS
from ...models import AppState, Recipient
from ...services import EmailService


class MessageTab:
    """Onglet de rédaction du message."""

    def __init__(self, parent: ctk.CTkFrame, app_data: AppState):
        self.parent = parent
        self.app_data = app_data
        self._build()

    def _build(self):
        """Construit l'interface de l'onglet."""
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Panneau gauche - Message + Preview
        left = ctk.CTkFrame(container)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._build_message_section(left)
        self._build_preview_section(left)

        # Panneau droit - SMTP
        right = ctk.CTkFrame(container, width=380)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self._build_smtp_section(right)

    def _build_message_section(self, parent: ctk.CTkFrame):
        """Section de rédaction du message."""
        ctk.CTkLabel(
            parent,
            text="Rediger le message",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Info variables
        info = ctk.CTkFrame(parent, fg_color="#fef3c7", corner_radius=8)
        info.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(
            info,
            text="Variables : {{nom}}  {{prenom}}  {{numero}}  {{email}}",
            font=("Segoe UI", 11),
            text_color="#92400e"
        ).pack(padx=15, pady=8)

        # Objet
        ctk.CTkLabel(
            parent,
            text="Objet du mail",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=20)

        self.subject_entry = ctk.CTkEntry(parent, height=35, font=("Segoe UI", 12))
        self.subject_entry.pack(fill="x", padx=20, pady=(5, 10))
        self.subject_entry.insert(0, self.app_data.subject)

        # Corps
        ctk.CTkLabel(
            parent,
            text="Corps du message",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=20)

        self.body_text = ctk.CTkTextbox(parent, font=("Segoe UI", 12), wrap="word", height=200)
        self.body_text.pack(fill="x", padx=20, pady=(5, 10))
        self.body_text.insert("1.0", self.app_data.body)

    def _build_preview_section(self, parent: ctk.CTkFrame):
        """Section de preview du mail."""
        # Header avec bouton
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="Apercu du mail",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Actualiser",
            width=100,
            height=28,
            fg_color=COLORS["primary"],
            command=self._update_preview
        ).pack(side="right")

        # Zone de preview
        preview_frame = ctk.CTkFrame(parent, fg_color="#f8fafc", corner_radius=8)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Objet preview
        self.preview_subject = ctk.CTkLabel(
            preview_frame,
            text="Objet: ---",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["primary"],
            anchor="w"
        )
        self.preview_subject.pack(fill="x", padx=15, pady=(15, 5))

        # Separateur
        ctk.CTkFrame(preview_frame, height=1, fg_color="#e2e8f0").pack(fill="x", padx=15, pady=5)

        # Corps preview
        self.preview_body = ctk.CTkTextbox(
            preview_frame,
            font=("Segoe UI", 11),
            wrap="word",
            fg_color="#f8fafc",
            state="disabled"
        )
        self.preview_body.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def _update_preview(self):
        """Met à jour la preview avec le premier destinataire ou des données exemple."""
        # Utiliser le premier destinataire ou des données exemple
        if self.app_data.recipients:
            recipient = self.app_data.recipients[0]
        else:
            recipient = Recipient(
                email="exemple@email.com",
                nom="Dupont",
                prenom="Jean",
                numero="12345"
            )

        # Remplacer les placeholders
        subject = EmailService.replace_placeholders(self.subject_entry.get(), recipient)
        body = EmailService.replace_placeholders(self.body_text.get("1.0", "end-1c"), recipient)

        # Mettre à jour l'affichage
        self.preview_subject.configure(text=f"Objet: {subject}")

        self.preview_body.configure(state="normal")
        self.preview_body.delete("1.0", "end")
        self.preview_body.insert("1.0", body)
        self.preview_body.configure(state="disabled")

    def _build_smtp_section(self, parent: ctk.CTkFrame):
        """Section de configuration SMTP."""
        ctk.CTkLabel(
            parent,
            text="Configuration SMTP",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 15))

        # Fournisseur
        ctk.CTkLabel(parent, text="Fournisseur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.provider_var = ctk.StringVar(value="Gmail")
        self.provider_menu = ctk.CTkOptionMenu(
            parent,
            values=list(SMTP_PROVIDERS.keys()),
            variable=self.provider_var,
            command=self._on_provider_change,
            width=300,
            height=35
        )
        self.provider_menu.pack(anchor="w", padx=20, pady=(5, 15))

        # Serveur et port
        server_frame = ctk.CTkFrame(parent, fg_color="transparent")
        server_frame.pack(fill="x", padx=20, pady=(0, 15))

        server_left = ctk.CTkFrame(server_frame, fg_color="transparent")
        server_left.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(server_left, text="Serveur", font=("Segoe UI", 11)).pack(anchor="w")
        self.server_entry = ctk.CTkEntry(server_left, height=35)
        self.server_entry.pack(fill="x", pady=(5, 0))
        self.server_entry.insert(0, "smtp.gmail.com")
        self.server_entry.configure(state="disabled")

        server_right = ctk.CTkFrame(server_frame, fg_color="transparent", width=80)
        server_right.pack(side="right")
        server_right.pack_propagate(False)
        ctk.CTkLabel(server_right, text="Port", font=("Segoe UI", 11)).pack(anchor="w")
        self.port_entry = ctk.CTkEntry(server_right, height=35, width=80)
        self.port_entry.pack(fill="x", pady=(5, 0))
        self.port_entry.insert(0, "587")
        self.port_entry.configure(state="disabled")

        # Email
        ctk.CTkLabel(parent, text="Email expediteur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(
            parent,
            height=35,
            width=300,
            placeholder_text="votre.email@gmail.com"
        )
        self.email_entry.pack(anchor="w", padx=20, pady=(5, 15))

        # Mot de passe
        ctk.CTkLabel(parent, text="App Password", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(parent, height=35, width=300, show="*")
        self.password_entry.pack(anchor="w", padx=20, pady=(5, 10))

        # Info Gmail
        self.gmail_info = ctk.CTkLabel(
            parent,
            text="Gmail : myaccount.google.com/apppasswords",
            font=("Segoe UI", 10),
            text_color=COLORS["primary"],
            justify="left"
        )
        self.gmail_info.pack(anchor="w", padx=20, pady=(5, 20))

    def _on_provider_change(self, choice: str):
        """Gère le changement de fournisseur."""
        server, port = SMTP_PROVIDERS.get(choice, ("", 587))

        self.server_entry.configure(state="normal")
        self.port_entry.configure(state="normal")
        self.server_entry.delete(0, "end")
        self.port_entry.delete(0, "end")

        if choice != "Autre":
            self.server_entry.insert(0, server)
            self.port_entry.insert(0, str(port))
            self.server_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")
        else:
            self.port_entry.insert(0, "587")

        self.gmail_info.configure(
            text="Gmail : myaccount.google.com/apppasswords" if choice == "Gmail" else ""
        )

    def get_subject(self) -> str:
        """Retourne l'objet du mail."""
        return self.subject_entry.get()

    def get_body(self) -> str:
        """Retourne le corps du mail."""
        return self.body_text.get("1.0", "end-1c")

    def get_smtp_server(self) -> str:
        """Retourne le serveur SMTP."""
        self.server_entry.configure(state="normal")
        server = self.server_entry.get()
        if self.provider_var.get() != "Autre":
            self.server_entry.configure(state="disabled")
        return server

    def get_smtp_port(self) -> int:
        """Retourne le port SMTP."""
        self.port_entry.configure(state="normal")
        port = self.port_entry.get()
        if self.provider_var.get() != "Autre":
            self.port_entry.configure(state="disabled")
        return int(port or 587)

    def get_email(self) -> str:
        """Retourne l'email expéditeur."""
        return self.email_entry.get()

    def get_password(self) -> str:
        """Retourne le mot de passe."""
        return self.password_entry.get()
