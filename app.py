"""
Mail Sender - Application d'envoi de mails personnalisés
"""

import customtkinter as ctk
import pandas as pd
import smtplib
import time
import threading
import os
import zipfile
from tkinter import filedialog, ttk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum


# ============================================================
#                       MODELS
# ============================================================

class SendStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Recipient:
    email: str
    nom: str
    prenom: str
    numero: str
    status: SendStatus = SendStatus.PENDING
    error: Optional[str] = None


@dataclass
class SMTPConfig:
    server: str = "smtp.gmail.com"
    port: int = 587
    email: str = ""
    password: str = ""

    def is_valid(self) -> bool:
        return all([self.server, self.email, self.password])


@dataclass
class AppState:
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
    custom_images: Dict[str, bytes] = field(default_factory=dict)


# ============================================================
#                       SERVICES
# ============================================================

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
    def send(config: SMTPConfig, recipient: Recipient, subject: str, body: str,
             image_data: Optional[bytes] = None) -> tuple[bool, Optional[str]]:
        """Envoie un email. Retourne (success, error_message)."""
        try:
            # Personnaliser pour CE destinataire
            personalized_subject = EmailService.replace_placeholders(subject, recipient)
            personalized_body = EmailService.replace_placeholders(body, recipient)

            msg = MIMEMultipart('related')
            msg['From'] = config.email
            msg['To'] = recipient.email
            msg['Subject'] = personalized_subject

            img_tag = "<br><img src='cid:event_image' style='max-width: 600px;'>" if image_data else ""
            html_body = f"""
            <html><body>
            <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            {personalized_body.replace(chr(10), '<br>')}
            </div>
            {img_tag}
            </body></html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            if image_data:
                img = MIMEImage(image_data)
                img.add_header('Content-ID', '<event_image>')
                img.add_header('Content-Disposition', 'inline', filename='image.png')
                msg.attach(img)

            with smtplib.SMTP(config.server, config.port) as server:
                server.starttls()
                server.login(config.email, config.password)
                server.send_message(msg)

            return True, None

        except Exception as e:
            return False, str(e)


class DataService:
    """Service de gestion des données."""

    @staticmethod
    def load_file(filepath: str) -> tuple[List[Recipient], Optional[str]]:
        """Charge un fichier Excel/CSV. Retourne (recipients, error)."""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            required = ['email', 'nom', 'prenom', 'numero']
            missing = [c for c in required if c not in df.columns]

            if missing:
                return [], f"Colonnes manquantes : {', '.join(missing)}"

            recipients = []
            for _, row in df.iterrows():
                recipients.append(Recipient(
                    email=str(row['email']).strip(),
                    nom=str(row['nom']).strip(),
                    prenom=str(row['prenom']).strip(),
                    numero=str(row['numero']).strip()
                ))

            return recipients, None

        except Exception as e:
            return [], str(e)

    @staticmethod
    def create_template(filepath: str) -> Optional[str]:
        """Crée un template Excel. Retourne error si échec."""
        try:
            df = pd.DataFrame({
                'email': ['exemple1@email.com', 'exemple2@email.com'],
                'nom': ['Dupont', 'Martin'],
                'prenom': ['Jean', 'Marie'],
                'numero': ['001', '002']
            })
            df.to_excel(filepath, index=False)
            return None
        except Exception as e:
            return str(e)

    @staticmethod
    def load_images_zip(filepath: str) -> tuple[Dict[str, bytes], Optional[str]]:
        """Charge les images depuis un ZIP. Retourne (images, error)."""
        try:
            images = {}
            with zipfile.ZipFile(filepath, 'r') as z:
                for fname in z.namelist():
                    if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        email_key = os.path.splitext(os.path.basename(fname))[0]
                        images[email_key] = z.read(fname)
            return images, None
        except Exception as e:
            return {}, str(e)


# ============================================================
#                       SMTP PROVIDERS
# ============================================================

SMTP_PROVIDERS = {
    "Gmail": ("smtp.gmail.com", 587),
    "Outlook/Hotmail": ("smtp-mail.outlook.com", 587),
    "Yahoo": ("smtp.mail.yahoo.com", 587),
    "Autre": ("", 587),
}


# ============================================================
#                       UI - THEME
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "primary": "#1e40af",
    "success": "#059669",
    "error": "#dc2626",
    "warning": "#d97706",
    "gray": "#6b7280",
    "light_gray": "#f3f4f6",
}


# ============================================================
#                       APPLICATION
# ============================================================

class MailSenderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mail Sender")
        self.geometry("1250x900")
        self.minsize(1100, 800)

        self.app_data = AppState()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["primary"], corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="✉  Mail Sender", font=("Segoe UI", 22, "bold"),
                    text_color="white").pack(side="left", padx=25, pady=15)

        # Tabs
        self.tabview = ctk.CTkTabview(self, segmented_button_fg_color="#e5e7eb",
                                       segmented_button_selected_color=COLORS["primary"])
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_data = self.tabview.add("1. Données")
        self.tab_template = self.tabview.add("2. Message")
        self.tab_send = self.tabview.add("3. Envoi")

        self._build_data_tab()
        self._build_template_tab()
        self._build_send_tab()

    # ==================== TAB 1: DONNÉES ====================
    def _build_data_tab(self):
        left = ctk.CTkFrame(self.tab_data, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Import section
        import_frame = ctk.CTkFrame(left)
        import_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(import_frame, text="Import des destinataires",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(import_frame, text="Colonnes requises : email, nom, prenom, numero",
                    font=("Segoe UI", 11), text_color=COLORS["gray"]).pack(anchor="w", padx=20, pady=(0, 10))

        btn_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(btn_frame, text="📥 Télécharger template",
                     fg_color=COLORS["success"], hover_color="#047857",
                     command=self._download_template).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="📂 Importer fichier (Excel/CSV)",
                     command=self._import_file).pack(side="left")

        self.import_status = ctk.CTkLabel(import_frame, text="", font=("Segoe UI", 12))
        self.import_status.pack(anchor="w", padx=20, pady=(0, 15))

        # Preview section
        preview_frame = ctk.CTkFrame(left)
        preview_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(preview_frame, text="Aperçu des données",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        tree_container = ctk.CTkFrame(preview_frame, fg_color="white", corner_radius=8)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        self.tree = ttk.Treeview(tree_container, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Right panel: Images
        right = ctk.CTkFrame(self.tab_data, width=350)
        right.pack(side="right", fill="y", padx=(10, 0), pady=10)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Images (optionnel)",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 15))

        img_section1 = ctk.CTkFrame(right, fg_color=COLORS["light_gray"], corner_radius=8)
        img_section1.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(img_section1, text="Image par défaut",
                    font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkButton(img_section1, text="Choisir une image", width=200,
                     command=self._pick_default_image).pack(anchor="w", padx=15, pady=10)

        self.default_img_status = ctk.CTkLabel(img_section1, text="Aucune",
                                               text_color=COLORS["gray"], font=("Segoe UI", 11))
        self.default_img_status.pack(anchor="w", padx=15, pady=(0, 15))

        img_section2 = ctk.CTkFrame(right, fg_color=COLORS["light_gray"], corner_radius=8)
        img_section2.pack(fill="x", padx=20)

        ctk.CTkLabel(img_section2, text="Images personnalisées (ZIP)",
                    font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkButton(img_section2, text="Choisir un ZIP", width=200,
                     command=self._pick_zip).pack(anchor="w", padx=15, pady=10)

        self.custom_img_status = ctk.CTkLabel(img_section2, text="Aucun",
                                              text_color=COLORS["gray"], font=("Segoe UI", 11))
        self.custom_img_status.pack(anchor="w", padx=15, pady=(0, 15))

    def _download_template(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="template_destinataires.xlsx"
        )
        if file:
            error = DataService.create_template(file)
            if error:
                self.import_status.configure(text=f"❌ {error}", text_color=COLORS["error"])
            else:
                self.import_status.configure(text="✅ Template téléchargé !", text_color=COLORS["success"])

    def _import_file(self):
        file = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")]
        )
        if file:
            recipients, error = DataService.load_file(file)
            if error:
                self.import_status.configure(text=f"❌ {error}", text_color=COLORS["error"])
                self.app_data.recipients = []
            else:
                self.app_data.recipients = recipients
                self.import_status.configure(
                    text=f"✅ {len(recipients)} destinataires chargés",
                    text_color=COLORS["success"]
                )
                self._update_preview()

    def _update_preview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        columns = ['email', 'nom', 'prenom', 'numero']
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, anchor="w")

        for r in self.app_data.recipients:
            self.tree.insert("", "end", values=(r.email, r.nom, r.prenom, r.numero))

    def _pick_default_image(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")])
        if file:
            try:
                with open(file, 'rb') as f:
                    self.app_data.default_image = f.read()
                self.default_img_status.configure(
                    text=f"✅ {os.path.basename(file)}",
                    text_color=COLORS["success"]
                )
            except:
                self.default_img_status.configure(text="❌ Erreur", text_color=COLORS["error"])

    def _pick_zip(self):
        file = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
        if file:
            images, error = DataService.load_images_zip(file)
            if error:
                self.custom_img_status.configure(text="❌ Erreur", text_color=COLORS["error"])
            else:
                self.app_data.custom_images = images
                self.custom_img_status.configure(
                    text=f"✅ {len(images)} images",
                    text_color=COLORS["success"]
                )

    # ==================== TAB 2: MESSAGE ====================
    def _build_template_tab(self):
        container = ctk.CTkFrame(self.tab_template, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        left = ctk.CTkFrame(container)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left, text="Rédiger le message",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        info = ctk.CTkFrame(left, fg_color="#fef3c7", corner_radius=8)
        info.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(info, text="Variables : {{nom}}  {{prenom}}  {{numero}}  {{email}}",
                    font=("Segoe UI", 11), text_color="#92400e").pack(padx=15, pady=10)

        ctk.CTkLabel(left, text="Objet du mail", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        self.subject_entry = ctk.CTkEntry(left, height=40, font=("Segoe UI", 12))
        self.subject_entry.pack(fill="x", padx=20, pady=(5, 15))
        self.subject_entry.insert(0, self.app_data.subject)

        ctk.CTkLabel(left, text="Corps du message", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        self.body_text = ctk.CTkTextbox(left, font=("Segoe UI", 12), wrap="word")
        self.body_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.body_text.insert("1.0", self.app_data.body)

        # SMTP Config
        right = ctk.CTkFrame(container, width=380)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Configuration SMTP",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        ctk.CTkLabel(right, text="Fournisseur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.provider_var = ctk.StringVar(value="Gmail")
        self.provider_menu = ctk.CTkOptionMenu(right, values=list(SMTP_PROVIDERS.keys()),
                                               variable=self.provider_var,
                                               command=self._on_provider_change,
                                               width=300, height=35)
        self.provider_menu.pack(anchor="w", padx=20, pady=(5, 15))

        server_frame = ctk.CTkFrame(right, fg_color="transparent")
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

        ctk.CTkLabel(right, text="Email expéditeur", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(right, height=35, width=300,
                                        placeholder_text="votre.email@gmail.com")
        self.email_entry.pack(anchor="w", padx=20, pady=(5, 15))

        ctk.CTkLabel(right, text="App Password", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(right, height=35, width=300, show="•")
        self.password_entry.pack(anchor="w", padx=20, pady=(5, 10))

        self.gmail_info = ctk.CTkLabel(right,
            text="💡 Gmail : myaccount.google.com/apppasswords",
            font=("Segoe UI", 10), text_color=COLORS["primary"], justify="left")
        self.gmail_info.pack(anchor="w", padx=20, pady=(5, 20))

    def _on_provider_change(self, choice):
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
            text="💡 Gmail : myaccount.google.com/apppasswords" if choice == "Gmail" else ""
        )

    # ==================== TAB 3: ENVOI ====================
    def _build_send_tab(self):
        container = ctk.CTkFrame(self.tab_send, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Summary + Buttons
        top_frame = ctk.CTkFrame(container)
        top_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(top_frame, text="Résumé",
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        self.summary_text = ctk.CTkLabel(top_frame,
            text="📋 0 destinataires  |  📎 Image: Non  |  📦 Images perso: 0",
            font=("Segoe UI", 12))
        self.summary_text.pack(anchor="w", padx=20, pady=(0, 15))

        btn_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(btn_frame, text="🔄 Actualiser", width=140,
                     fg_color=COLORS["gray"], hover_color="#4b5563",
                     command=self._update_summary).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="📬 Test", width=140,
                     command=self._send_test).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_frame, text="🚀 ENVOYER À TOUS", width=200,
                     fg_color=COLORS["success"], hover_color="#047857",
                     font=("Segoe UI", 13, "bold"),
                     command=self._send_all).pack(side="left")

        # Progress
        progress_frame = ctk.CTkFrame(container)
        progress_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(progress_frame, text="Progression",
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        self.progress = ctk.CTkProgressBar(progress_frame, height=20)
        self.progress.pack(fill="x", padx=20, pady=(0, 10))
        self.progress.set(0)

        self.send_status = ctk.CTkLabel(progress_frame, text="En attente...",
                                        font=("Segoe UI", 12), text_color=COLORS["gray"])
        self.send_status.pack(anchor="w", padx=20, pady=(0, 15))

        # Results - Two columns
        results_frame = ctk.CTkFrame(container)
        results_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(results_frame, text="Résultats",
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        columns_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Success column
        success_frame = ctk.CTkFrame(columns_frame)
        success_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(success_frame, text="✅ Envoyés",
                    font=("Segoe UI", 12, "bold"), text_color=COLORS["success"]).pack(anchor="w", padx=15, pady=(10, 5))

        self.success_list = ctk.CTkTextbox(success_frame, font=("Consolas", 10), state="disabled")
        self.success_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Failed column
        failed_frame = ctk.CTkFrame(columns_frame)
        failed_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(failed_frame, text="❌ Échoués",
                    font=("Segoe UI", 12, "bold"), text_color=COLORS["error"]).pack(anchor="w", padx=15, pady=(10, 5))

        self.failed_list = ctk.CTkTextbox(failed_frame, font=("Consolas", 10), state="disabled")
        self.failed_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _update_summary(self):
        count = len(self.app_data.recipients)
        has_img = "Oui" if self.app_data.default_image else "Non"
        custom_count = len(self.app_data.custom_images)

        self.summary_text.configure(
            text=f"📋 {count} destinataires  |  📎 Image: {has_img}  |  📦 Images perso: {custom_count}"
        )

    def _get_smtp_config(self) -> SMTPConfig:
        self.server_entry.configure(state="normal")
        server = self.server_entry.get()
        self.port_entry.configure(state="normal")
        port = self.port_entry.get()

        if self.provider_var.get() != "Autre":
            self.server_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")

        return SMTPConfig(
            server=server,
            port=int(port or 587),
            email=self.email_entry.get(),
            password=self.password_entry.get()
        )

    def _log_success(self, text: str):
        self.success_list.configure(state="normal")
        self.success_list.insert("end", text + "\n")
        self.success_list.see("end")
        self.success_list.configure(state="disabled")

    def _log_failed(self, text: str):
        self.failed_list.configure(state="normal")
        self.failed_list.insert("end", text + "\n")
        self.failed_list.see("end")
        self.failed_list.configure(state="disabled")

    def _clear_logs(self):
        self.success_list.configure(state="normal")
        self.success_list.delete("1.0", "end")
        self.success_list.configure(state="disabled")
        self.failed_list.configure(state="normal")
        self.failed_list.delete("1.0", "end")
        self.failed_list.configure(state="disabled")

    def _send_test(self):
        config = self._get_smtp_config()

        if not config.is_valid():
            self.send_status.configure(text="❌ Configure le SMTP (onglet Message)", text_color=COLORS["error"])
            return

        self.send_status.configure(text="📤 Envoi du test...", text_color=COLORS["primary"])
        self._clear_logs()
        self.update()

        # Créer un destinataire test
        test_recipient = Recipient(
            email=config.email,
            nom="Dupont",
            prenom="Jean",
            numero="12345"
        )

        subject = self.subject_entry.get()
        body = self.body_text.get("1.0", "end-1c")

        success, error = EmailService.send(config, test_recipient, subject, body, self.app_data.default_image)

        if success:
            self.send_status.configure(text=f"✅ Test envoyé à {config.email}", text_color=COLORS["success"])
            self._log_success(f"{config.email} (TEST)")
        else:
            self.send_status.configure(text=f"❌ {error}", text_color=COLORS["error"])
            self._log_failed(f"{config.email}: {error}")

    def _send_all(self):
        config = self._get_smtp_config()

        if not config.is_valid():
            self.send_status.configure(text="❌ Configure le SMTP (onglet Message)", text_color=COLORS["error"])
            return

        if not self.app_data.recipients:
            self.send_status.configure(text="❌ Importe des destinataires (onglet Données)", text_color=COLORS["error"])
            return

        def do_send():
            self._clear_logs()
            self.send_status.configure(text="📤 Envoi en cours...", text_color=COLORS["primary"])
            self.progress.set(0)

            subject = self.subject_entry.get()
            body = self.body_text.get("1.0", "end-1c")

            success_count = 0
            failed_count = 0
            total = len(self.app_data.recipients)

            for idx, recipient in enumerate(self.app_data.recipients):
                # Image personnalisée ou par défaut
                img = self.app_data.custom_images.get(recipient.email, self.app_data.default_image)

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
                self.update()
                time.sleep(0.5)

            # Résultat final
            if failed_count == 0:
                self.send_status.configure(
                    text=f"✅ Terminé ! {success_count} envoyés",
                    text_color=COLORS["success"]
                )
            else:
                self.send_status.configure(
                    text=f"⚠️ {success_count} envoyés, {failed_count} échoués",
                    text_color=COLORS["warning"]
                )

        threading.Thread(target=do_send, daemon=True).start()


# ============================================================
#                       MAIN
# ============================================================

if __name__ == "__main__":
    app = MailSenderApp()
    app.mainloop()
