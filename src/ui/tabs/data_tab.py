"""
Onglet Données - Import des destinataires et images.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, ttk

from ...config import COLORS
from ...models import AppState
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
        """Section d'aperçu des données."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Apercu des donnees",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        tree_container = ctk.CTkFrame(frame, fg_color="white", corner_radius=8)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Style du Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        self.tree = ttk.Treeview(tree_container, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

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

        columns = ['email', 'nom', 'prenom', 'numero']
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, anchor="w")

        for r in self.app_data.recipients:
            self.tree.insert("", "end", values=(r.email, r.nom, r.prenom, r.numero))

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
