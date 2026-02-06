"""
Onglet Message - Redaction du message, image et configuration email.
"""

import os
import io
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

from ...config import COLORS, SMTP_PROVIDERS, API_PROVIDERS, ALL_PROVIDERS
from ...models import AppState, Recipient
from ...services import EmailService


class MessageTab:
    """Onglet de redaction du message."""

    def __init__(self, parent: ctk.CTkFrame, app_data: AppState):
        self.parent = parent
        self.app_data = app_data
        self.preview_image_label = None
        self._build()

    def _build(self):
        """Construit l'interface de l'onglet."""
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Panneau gauche - Message + Image + Preview
        left = ctk.CTkFrame(container)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._build_message_section(left)
        self._build_image_section(left)
        self._build_preview_section(left)

        # Panneau droit - Config email
        right = ctk.CTkFrame(container, width=380)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self._build_config_section(right)

    def _build_message_section(self, parent: ctk.CTkFrame):
        """Section de redaction du message."""
        ctk.CTkLabel(
            parent,
            text="Rediger le message",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 8))

        # Info variables
        info = ctk.CTkFrame(parent, fg_color="#fef3c7", corner_radius=8)
        info.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(
            info,
            text="Variables : {{nom}}  {{prenom}}  {{numero}}  {{email}}",
            font=("Segoe UI", 11),
            text_color="#92400e"
        ).pack(padx=15, pady=6)

        # Objet
        ctk.CTkLabel(
            parent,
            text="Objet du mail",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=20)

        self.subject_entry = ctk.CTkEntry(parent, height=32, font=("Segoe UI", 12))
        self.subject_entry.pack(fill="x", padx=20, pady=(3, 8))
        self.subject_entry.insert(0, self.app_data.subject)

        # Corps
        ctk.CTkLabel(
            parent,
            text="Corps du message",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=20)

        self.body_text = ctk.CTkTextbox(parent, font=("Segoe UI", 12), wrap="word", height=120)
        self.body_text.pack(fill="x", padx=20, pady=(3, 8))
        self.body_text.insert("1.0", self.app_data.body)

    def _build_image_section(self, parent: ctk.CTkFrame):
        """Section de selection d'image."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["light_gray"], corner_radius=8)
        frame.pack(fill="x", padx=20, pady=(0, 8))

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="Image jointe (optionnel)",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Choisir",
            width=80,
            height=28,
            command=self._pick_image
        ).pack(side="right", padx=(5, 0))

        ctk.CTkButton(
            header,
            text="Supprimer",
            width=80,
            height=28,
            fg_color=COLORS["error"],
            hover_color="#b91c1c",
            command=self._remove_image
        ).pack(side="right")

        self.image_status = ctk.CTkLabel(
            frame,
            text="Aucune image",
            font=("Segoe UI", 11),
            text_color=COLORS["gray"]
        )
        self.image_status.pack(anchor="w", padx=15, pady=(0, 10))

    def _pick_image(self):
        """Selectionne une image."""
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if file:
            try:
                with open(file, 'rb') as f:
                    self.app_data.default_image = f.read()
                self.image_status.configure(
                    text=f"Image: {os.path.basename(file)}",
                    text_color=COLORS["success"]
                )
                self._update_preview()
            except Exception:
                self.image_status.configure(text="Erreur", text_color=COLORS["error"])

    def _remove_image(self):
        """Supprime l'image."""
        self.app_data.default_image = None
        self.image_status.configure(text="Aucune image", text_color=COLORS["gray"])
        self._update_preview()

    def _build_preview_section(self, parent: ctk.CTkFrame):
        """Section de preview du mail."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(5, 3))

        ctk.CTkLabel(
            header,
            text="Apercu du mail",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Actualiser",
            width=90,
            height=26,
            fg_color=COLORS["primary"],
            command=self._update_preview
        ).pack(side="right")

        preview_frame = ctk.CTkFrame(parent, fg_color="#f8fafc", corner_radius=8)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.preview_subject = ctk.CTkLabel(
            preview_frame,
            text="Objet: ---",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["primary"],
            anchor="w"
        )
        self.preview_subject.pack(fill="x", padx=12, pady=(10, 3))

        ctk.CTkFrame(preview_frame, height=1, fg_color="#e2e8f0").pack(fill="x", padx=12, pady=3)

        self.preview_scroll = ctk.CTkScrollableFrame(
            preview_frame,
            fg_color="#f8fafc",
            corner_radius=0
        )
        self.preview_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.preview_body = ctk.CTkLabel(
            self.preview_scroll,
            text="",
            font=("Segoe UI", 10),
            anchor="nw",
            justify="left",
            wraplength=500
        )
        self.preview_body.pack(fill="x", padx=8, pady=(5, 10))

        self.preview_image_container = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        self.preview_image_container.pack(fill="x", padx=8, pady=(0, 10))

    def _update_preview(self):
        """Met a jour la preview."""
        if self.app_data.recipients:
            recipient = self.app_data.recipients[0]
        else:
            recipient = Recipient(
                email="exemple@email.com",
                nom="Dupont",
                prenom="Jean",
                numero="12345"
            )

        subject = EmailService.replace_placeholders(self.subject_entry.get(), recipient)
        body = EmailService.replace_placeholders(self.body_text.get("1.0", "end-1c"), recipient)

        self.preview_subject.configure(text=f"Objet: {subject}")
        self.preview_body.configure(text=body)

        for widget in self.preview_image_container.winfo_children():
            widget.destroy()

        if self.app_data.default_image:
            try:
                img = Image.open(io.BytesIO(self.app_data.default_image))
                max_width = 400
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                ctk_image = ctk.CTkImage(light_image=img, size=(img.width, img.height))
                img_label = ctk.CTkLabel(
                    self.preview_image_container,
                    image=ctk_image,
                    text=""
                )
                img_label.image = ctk_image
                img_label.pack(pady=(5, 0))

            except Exception as e:
                ctk.CTkLabel(
                    self.preview_image_container,
                    text=f"Erreur image: {e}",
                    text_color=COLORS["error"]
                ).pack()

    def _build_config_section(self, parent: ctk.CTkFrame):
        """Section de configuration email (SMTP ou SendGrid)."""
        ctk.CTkLabel(
            parent,
            text="Configuration Email",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 15))

        # Fournisseur
        ctk.CTkLabel(parent, text="Fournisseur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.provider_var = ctk.StringVar(value="Gmail")
        self.provider_menu = ctk.CTkOptionMenu(
            parent,
            values=ALL_PROVIDERS,
            variable=self.provider_var,
            command=self._on_provider_change,
            width=300,
            height=35
        )
        self.provider_menu.pack(anchor="w", padx=20, pady=(5, 15))

        # === Section SMTP (Gmail, Outlook, etc.) ===
        self.smtp_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.smtp_frame.pack(fill="x")

        # Serveur et port
        server_frame = ctk.CTkFrame(self.smtp_frame, fg_color="transparent")
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
        ctk.CTkLabel(self.smtp_frame, text="Email expediteur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(
            self.smtp_frame,
            height=35,
            width=300,
            placeholder_text="votre.email@gmail.com"
        )
        self.email_entry.pack(anchor="w", padx=20, pady=(5, 15))

        # Mot de passe
        ctk.CTkLabel(self.smtp_frame, text="App Password", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(self.smtp_frame, height=35, width=300, show="*")
        self.password_entry.pack(anchor="w", padx=20, pady=(5, 10))

        # Info Gmail
        self.smtp_info = ctk.CTkLabel(
            self.smtp_frame,
            text="Gmail : myaccount.google.com/apppasswords",
            font=("Segoe UI", 10),
            text_color=COLORS["primary"],
            justify="left"
        )
        self.smtp_info.pack(anchor="w", padx=20, pady=(5, 20))

        # === Section SendGrid ===
        self.sendgrid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Ne pas pack ici, sera affiche quand SendGrid selectionne

        # API Key
        ctk.CTkLabel(self.sendgrid_frame, text="API Key", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.api_key_entry = ctk.CTkEntry(
            self.sendgrid_frame,
            height=35,
            width=300,
            placeholder_text="SG.xxxxxxxx...",
            show="*"
        )
        self.api_key_entry.pack(anchor="w", padx=20, pady=(5, 15))

        # From Email
        ctk.CTkLabel(self.sendgrid_frame, text="Email expediteur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.sg_email_entry = ctk.CTkEntry(
            self.sendgrid_frame,
            height=35,
            width=300,
            placeholder_text="contact@mondomaine.com"
        )
        self.sg_email_entry.pack(anchor="w", padx=20, pady=(5, 15))

        # Info SendGrid
        self.sg_info = ctk.CTkLabel(
            self.sendgrid_frame,
            text="1. Creer un compte sur sendgrid.com\n2. Settings > API Keys > Create\n3. Coller la cle ici",
            font=("Segoe UI", 10),
            text_color=COLORS["primary"],
            justify="left"
        )
        self.sg_info.pack(anchor="w", padx=20, pady=(5, 20))

    def _on_provider_change(self, choice: str):
        """Gere le changement de fournisseur."""
        if choice in API_PROVIDERS:
            # Mode SendGrid
            self.smtp_frame.pack_forget()
            self.sendgrid_frame.pack(fill="x")
        else:
            # Mode SMTP
            self.sendgrid_frame.pack_forget()
            self.smtp_frame.pack(fill="x")

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

            self.smtp_info.configure(
                text="Gmail : myaccount.google.com/apppasswords" if choice == "Gmail" else ""
            )

    def get_provider_type(self) -> str:
        """Retourne le type de provider selectionne."""
        return self.provider_var.get()

    def is_sendgrid(self) -> bool:
        """True si SendGrid est selectionne."""
        return self.provider_var.get() in API_PROVIDERS

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
        """Retourne l'email expediteur."""
        return self.email_entry.get()

    def get_password(self) -> str:
        """Retourne le mot de passe."""
        return self.password_entry.get()

    def get_api_key(self) -> str:
        """Retourne l'API Key SendGrid."""
        return self.api_key_entry.get()

    def get_sg_email(self) -> str:
        """Retourne l'email expediteur SendGrid."""
        return self.sg_email_entry.get()
