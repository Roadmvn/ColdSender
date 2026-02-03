"""
Onglet Données - Import des destinataires et images.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, ttk, simpledialog, messagebox

from ...config import COLORS
from ...models import AppState, Recipient
from ...services import DataService


class DataTab:
    """Onglet de gestion des données."""

    def __init__(self, parent: ctk.CTkFrame, app_data: AppState):
        self.parent = parent
        self.app_data = app_data
        self._build()

    def _build(self):
        """Construit l'interface de l'onglet."""
        # Panneau gauche
        left = ctk.CTkFrame(self.parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        self._build_import_section(left)
        self._build_preview_section(left)

        # Panneau droit - Images
        right = ctk.CTkFrame(self.parent, width=350)
        right.pack(side="right", fill="y", padx=(10, 0), pady=10)
        right.pack_propagate(False)

        self._build_images_section(right)

    def _build_import_section(self, parent: ctk.CTkFrame):
        """Section d'import des fichiers."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="Import des destinataires",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            frame,
            text="Colonnes requises : email, nom, prenom, numero",
            font=("Segoe UI", 11),
            text_color=COLORS["gray"]
        ).pack(anchor="w", padx=20, pady=(0, 10))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Telecharger template",
            fg_color=COLORS["success"],
            hover_color="#047857",
            command=self._download_template
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Importer fichier (Excel/CSV)",
            command=self._import_file
        ).pack(side="left")

        self.import_status = ctk.CTkLabel(frame, text="", font=("Segoe UI", 12))
        self.import_status.pack(anchor="w", padx=20, pady=(0, 15))

    def _build_preview_section(self, parent: ctk.CTkFrame):
        """Section d'aperçu des données avec gestion manuelle."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True)

        # Header avec titre et boutons
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="Liste des destinataires",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        # Boutons de gestion
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="+ Ajouter",
            width=90,
            height=30,
            fg_color=COLORS["success"],
            hover_color="#047857",
            command=self._add_recipient
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Modifier",
            width=90,
            height=30,
            fg_color=COLORS["primary"],
            command=self._edit_recipient
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Supprimer",
            width=90,
            height=30,
            fg_color=COLORS["error"],
            hover_color="#b91c1c",
            command=self._delete_recipient
        ).pack(side="left")

        # Treeview
        tree_container = ctk.CTkFrame(frame, fg_color="white", corner_radius=8)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Style du Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        self.tree = ttk.Treeview(tree_container, show="headings", height=10)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Double-clic pour editer
        self.tree.bind("<Double-1>", lambda e: self._edit_recipient())

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Initialiser les colonnes
        columns = ['email', 'nom', 'prenom', 'numero']
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, anchor="w")

    def _build_images_section(self, parent: ctk.CTkFrame):
        """Section de gestion des images."""
        ctk.CTkLabel(
            parent,
            text="Images (optionnel)",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 15))

        # Image par défaut
        section1 = ctk.CTkFrame(parent, fg_color=COLORS["light_gray"], corner_radius=8)
        section1.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(
            section1,
            text="Image par defaut",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkButton(
            section1,
            text="Choisir une image",
            width=200,
            command=self._pick_default_image
        ).pack(anchor="w", padx=15, pady=10)

        self.default_img_status = ctk.CTkLabel(
            section1,
            text="Aucune",
            text_color=COLORS["gray"],
            font=("Segoe UI", 11)
        )
        self.default_img_status.pack(anchor="w", padx=15, pady=(0, 15))

        # Images personnalisées
        section2 = ctk.CTkFrame(parent, fg_color=COLORS["light_gray"], corner_radius=8)
        section2.pack(fill="x", padx=20)

        ctk.CTkLabel(
            section2,
            text="Images personnalisees (ZIP)",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkButton(
            section2,
            text="Choisir un ZIP",
            width=200,
            command=self._pick_zip
        ).pack(anchor="w", padx=15, pady=10)

        self.custom_img_status = ctk.CTkLabel(
            section2,
            text="Aucun",
            text_color=COLORS["gray"],
            font=("Segoe UI", 11)
        )
        self.custom_img_status.pack(anchor="w", padx=15, pady=(0, 15))

    def _download_template(self):
        """Télécharge le fichier template."""
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="template_destinataires.xlsx"
        )
        if file:
            error = DataService.create_template(file)
            if error:
                self.import_status.configure(text=f"Erreur: {error}", text_color=COLORS["error"])
            else:
                self.import_status.configure(text="Template telecharge !", text_color=COLORS["success"])

    def _import_file(self):
        """Importe un fichier de destinataires."""
        file = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")]
        )
        if file:
            recipients, error = DataService.load_file(file)
            if error:
                self.import_status.configure(text=f"Erreur: {error}", text_color=COLORS["error"])
                self.app_data.recipients = []
            else:
                self.app_data.recipients = recipients
                self.import_status.configure(
                    text=f"{len(recipients)} destinataires charges",
                    text_color=COLORS["success"]
                )
                self._update_preview()

    def _update_preview(self):
        """Met à jour l'aperçu des données."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in self.app_data.recipients:
            self.tree.insert("", "end", values=(r.email, r.nom, r.prenom, r.numero))

        self.import_status.configure(
            text=f"{len(self.app_data.recipients)} destinataires",
            text_color=COLORS["success"] if self.app_data.recipients else COLORS["gray"]
        )

    def _add_recipient(self):
        """Ajoute un destinataire manuellement."""
        dialog = RecipientDialog(self.parent, "Ajouter un destinataire")
        if dialog.result:
            self.app_data.recipients.append(dialog.result)
            self._update_preview()

    def _edit_recipient(self):
        """Modifie le destinataire sélectionné."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Selectionne un destinataire a modifier")
            return

        # Trouver l'index
        item = selected[0]
        index = self.tree.index(item)
        recipient = self.app_data.recipients[index]

        dialog = RecipientDialog(self.parent, "Modifier le destinataire", recipient)
        if dialog.result:
            self.app_data.recipients[index] = dialog.result
            self._update_preview()

    def _delete_recipient(self):
        """Supprime le(s) destinataire(s) sélectionné(s)."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Selectionne un destinataire a supprimer")
            return

        if messagebox.askyesno("Confirmer", f"Supprimer {len(selected)} destinataire(s) ?"):
            # Supprimer en ordre inverse pour garder les indices valides
            indices = sorted([self.tree.index(item) for item in selected], reverse=True)
            for idx in indices:
                del self.app_data.recipients[idx]
            self._update_preview()

    def _pick_default_image(self):
        """Sélectionne l'image par défaut."""
        file = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        if file:
            try:
                with open(file, 'rb') as f:
                    self.app_data.default_image = f.read()
                self.default_img_status.configure(
                    text=f"OK: {os.path.basename(file)}",
                    text_color=COLORS["success"]
                )
            except Exception:
                self.default_img_status.configure(text="Erreur", text_color=COLORS["error"])

    def _pick_zip(self):
        """Sélectionne un fichier ZIP d'images."""
        file = filedialog.askopenfilename(filetypes=[("ZIP", "*.zip")])
        if file:
            images, error = DataService.load_images_zip(file)
            if error:
                self.custom_img_status.configure(text="Erreur", text_color=COLORS["error"])
            else:
                self.app_data.custom_images = images
                self.custom_img_status.configure(
                    text=f"OK: {len(images)} images",
                    text_color=COLORS["success"]
                )


class RecipientDialog(ctk.CTkToplevel):
    """Dialog pour ajouter/modifier un destinataire."""

    def __init__(self, parent, title: str, recipient: Recipient = None):
        super().__init__(parent)
        self.result = None
        self.recipient = recipient

        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)

        # Rendre modal
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        # Centrer
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")

        self.wait_window()

    def _build_ui(self):
        """Construit l'interface du dialog."""
        # Email
        ctk.CTkLabel(self, text="Email", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(20, 5))
        self.email_entry = ctk.CTkEntry(self, width=360, height=35)
        self.email_entry.pack(padx=20)

        # Nom
        ctk.CTkLabel(self, text="Nom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.nom_entry = ctk.CTkEntry(self, width=360, height=35)
        self.nom_entry.pack(padx=20)

        # Prenom
        ctk.CTkLabel(self, text="Prenom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.prenom_entry = ctk.CTkEntry(self, width=360, height=35)
        self.prenom_entry.pack(padx=20)

        # Numero
        ctk.CTkLabel(self, text="Numero", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.numero_entry = ctk.CTkEntry(self, width=360, height=35)
        self.numero_entry.pack(padx=20)

        # Pré-remplir si modification
        if self.recipient:
            self.email_entry.insert(0, self.recipient.email)
            self.nom_entry.insert(0, self.recipient.nom)
            self.prenom_entry.insert(0, self.recipient.prenom)
            self.numero_entry.insert(0, self.recipient.numero)

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Annuler",
            width=100,
            fg_color=COLORS["gray"],
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="Valider",
            width=100,
            fg_color=COLORS["success"],
            command=self._validate
        ).pack(side="right")

    def _validate(self):
        """Valide et ferme le dialog."""
        email = self.email_entry.get().strip()
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        numero = self.numero_entry.get().strip()

        if not all([email, nom, prenom, numero]):
            messagebox.showwarning("Attention", "Tous les champs sont requis")
            return

        self.result = Recipient(email=email, nom=nom, prenom=prenom, numero=numero)
        self.destroy()
