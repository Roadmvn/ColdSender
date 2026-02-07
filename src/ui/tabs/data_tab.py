"""
Onglet Données - Import et gestion des destinataires avec images personnalisées.
"""

import os
import io
import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
from PIL import Image

from ...config import COLORS
from ...models import AppState, Recipient
from ...services import DataService


class DataTab:
    """Onglet de gestion des données."""

    def __init__(self, parent: ctk.CTkFrame, app_data: AppState):
        self.parent = parent
        self.app_data = app_data
        self.selected_image_index = None
        self._build()

    def _build(self):
        """Construit l'interface de l'onglet."""
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Colonne gauche - Import et liste
        left = ctk.CTkFrame(main_container, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._build_import_section(left)
        self._build_preview_section(left)

        # Colonne droite - Preview images
        right = ctk.CTkFrame(main_container, width=300)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self._build_image_preview_section(right)

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

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="Liste des destinataires",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="+ Ajouter",
            width=80,
            height=28,
            fg_color=COLORS["success"],
            hover_color="#047857",
            command=self._add_recipient
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Modifier",
            width=80,
            height=28,
            fg_color=COLORS["primary"],
            command=self._edit_recipient
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Supprimer",
            width=80,
            height=28,
            fg_color=COLORS["error"],
            hover_color="#b91c1c",
            command=self._delete_recipient
        ).pack(side="left")

        # Treeview
        tree_container = ctk.CTkFrame(frame, fg_color="white", corner_radius=8)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tree = ttk.Treeview(tree_container, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)
        self.tree.bind("<Double-1>", lambda e: self._edit_recipient())

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        columns = ['email', 'nom', 'prenom', 'numero', 'images']
        self.tree["columns"] = columns

        self.tree.heading('email', text='EMAIL')
        self.tree.heading('nom', text='NOM')
        self.tree.heading('prenom', text='PRENOM')
        self.tree.heading('numero', text='NUMERO')
        self.tree.heading('images', text='IMAGES')

        self.tree.column('email', width=180, anchor="w")
        self.tree.column('nom', width=100, anchor="w")
        self.tree.column('prenom', width=100, anchor="w")
        self.tree.column('numero', width=70, anchor="w")
        self.tree.column('images', width=100, anchor="center")

    def _build_image_preview_section(self, parent: ctk.CTkFrame):
        """Section preview des images du destinataire selectionne."""
        ctk.CTkLabel(
            parent,
            text="Images du destinataire",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        self.selected_info = ctk.CTkLabel(
            parent,
            text="Selectionnez un destinataire",
            font=("Segoe UI", 11),
            text_color=COLORS["gray"]
        )
        self.selected_info.pack(anchor="w", padx=15, pady=(0, 10))

        # Zone scrollable pour les images
        self.images_scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=8,
            height=300
        )
        self.images_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.no_image_label = ctk.CTkLabel(
            self.images_scroll,
            text="Aucune image",
            text_color=COLORS["gray"]
        )
        self.no_image_label.pack(expand=True, pady=50)

        # Bouton ajouter
        ctk.CTkButton(
            parent,
            text="+ Ajouter une image",
            width=200,
            height=35,
            fg_color=COLORS["primary"],
            command=self._add_image_to_selected
        ).pack(pady=(0, 15))

    def _on_selection_change(self, event):
        """Met a jour la preview quand la selection change."""
        selected = self.tree.selection()
        if not selected:
            self.selected_info.configure(text="Selectionnez un destinataire", text_color=COLORS["gray"])
            self._clear_images_preview()
            return

        item = selected[0]
        index = self.tree.index(item)
        recipient = self.app_data.recipients[index]

        self.selected_info.configure(
            text=f"{recipient.prenom} {recipient.nom}",
            text_color=COLORS["primary"]
        )

        self._update_images_preview(recipient)

    def _update_images_preview(self, recipient: Recipient):
        """Met a jour la preview des images."""
        # Nettoyer
        for widget in self.images_scroll.winfo_children():
            widget.destroy()

        if not recipient.images:
            ctk.CTkLabel(
                self.images_scroll,
                text="Aucune image\nCliquez sur '+ Ajouter une image'",
                text_color=COLORS["gray"],
                justify="center"
            ).pack(expand=True, pady=50)
            return

        # Afficher chaque image avec son bouton supprimer
        for idx, (img_data, img_name) in enumerate(recipient.images):
            self._create_image_card(idx, img_data, img_name, recipient)

    def _create_image_card(self, idx: int, img_data: bytes, img_name: str, recipient: Recipient):
        """Cree une carte pour une image."""
        card = ctk.CTkFrame(self.images_scroll, fg_color="white", corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)

        # Preview de l'image
        try:
            img = Image.open(io.BytesIO(img_data))
            max_size = 100
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
                width=100
            ).pack(side="left", padx=10, pady=10)

        # Info et bouton supprimer
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            info_frame,
            text=img_name[:20] + "..." if len(img_name) > 20 else img_name,
            font=("Segoe UI", 11),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=f"Image {idx + 1}",
            font=("Segoe UI", 10),
            text_color=COLORS["gray"],
            anchor="w"
        ).pack(anchor="w")

        # Bouton supprimer
        ctk.CTkButton(
            card,
            text="X",
            width=30,
            height=30,
            fg_color=COLORS["error"],
            hover_color="#b91c1c",
            command=lambda i=idx, r=recipient: self._remove_image(r, i)
        ).pack(side="right", padx=10, pady=10)

    def _remove_image(self, recipient: Recipient, index: int):
        """Supprime une image specifique."""
        if 0 <= index < len(recipient.images):
            del recipient.images[index]
            self._update_preview()
            self._update_images_preview(recipient)

    def _clear_images_preview(self):
        """Efface la preview."""
        for widget in self.images_scroll.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.images_scroll,
            text="Aucune image",
            text_color=COLORS["gray"]
        ).pack(expand=True, pady=50)

    def _add_image_to_selected(self):
        """Ajoute une image au destinataire selectionne."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Selectionnez un destinataire")
            return

        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")],
            title="Selectionner une ou plusieurs images"
        )
        if files:
            item = selected[0]
            index = self.tree.index(item)
            recipient = self.app_data.recipients[index]

            for file in files:
                try:
                    with open(file, 'rb') as f:
                        image_data = f.read()
                    image_name = os.path.basename(file)
                    recipient.images.append((image_data, image_name))
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de charger {file}: {e}")

            self._update_preview()
            self._update_images_preview(recipient)

    def _download_template(self):
        """Telecharge le fichier template."""
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
        """Met a jour l'apercu des donnees."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in self.app_data.recipients:
            img_count = len(r.images)
            img_status = f"{img_count} image(s)" if img_count > 0 else "---"
            self.tree.insert("", "end", values=(r.email, r.nom, r.prenom, r.numero, img_status))

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
        """Modifie le destinataire selectionne."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Selectionnez un destinataire a modifier")
            return

        item = selected[0]
        index = self.tree.index(item)
        recipient = self.app_data.recipients[index]

        dialog = RecipientDialog(self.parent, "Modifier le destinataire", recipient)
        if dialog.result:
            self.app_data.recipients[index] = dialog.result
            self._update_preview()
            self._on_selection_change(None)

    def _delete_recipient(self):
        """Supprime le(s) destinataire(s) selectionne(s)."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Selectionnez un destinataire a supprimer")
            return

        if messagebox.askyesno("Confirmer", f"Supprimer {len(selected)} destinataire(s) ?"):
            indices = sorted([self.tree.index(item) for item in selected], reverse=True)
            for idx in indices:
                del self.app_data.recipients[idx]
            self._update_preview()
            self._clear_images_preview()


class RecipientDialog(ctk.CTkToplevel):
    """Dialog pour ajouter/modifier un destinataire."""

    def __init__(self, parent, title: str, recipient: Recipient = None):
        super().__init__(parent)
        self.result = None
        self.recipient = recipient
        # Copier les images existantes ou liste vide
        self.images = list(recipient.images) if recipient and recipient.images else []

        self.title(title)
        self.geometry("450x550")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")

        self.wait_window()

    def _build_ui(self):
        """Construit l'interface du dialog."""
        ctk.CTkLabel(self, text="Email", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(20, 5))
        self.email_entry = ctk.CTkEntry(self, width=410, height=35)
        self.email_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Nom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.nom_entry = ctk.CTkEntry(self, width=410, height=35)
        self.nom_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Prenom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.prenom_entry = ctk.CTkEntry(self, width=410, height=35)
        self.prenom_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Numero", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.numero_entry = ctk.CTkEntry(self, width=410, height=35)
        self.numero_entry.pack(padx=20)

        # Section images
        ctk.CTkLabel(self, text="Images personnalisees", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(15, 5))

        img_frame = ctk.CTkFrame(self, fg_color="transparent")
        img_frame.pack(fill="x", padx=20)

        ctk.CTkButton(
            img_frame,
            text="+ Ajouter images",
            width=140,
            command=self._pick_images
        ).pack(side="left", padx=(0, 10))

        self.image_status = ctk.CTkLabel(
            img_frame,
            text="0 image(s)",
            text_color=COLORS["gray"]
        )
        self.image_status.pack(side="left")

        # Pre-remplir si modification
        if self.recipient:
            self.email_entry.insert(0, self.recipient.email)
            self.nom_entry.insert(0, self.recipient.nom)
            self.prenom_entry.insert(0, self.recipient.prenom)
            self.numero_entry.insert(0, self.recipient.numero)
            self._update_image_status()

        # Boutons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=25)

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

    def _pick_images(self):
        """Selectionne des images."""
        files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")]
        )
        for file in files:
            try:
                with open(file, 'rb') as f:
                    img_data = f.read()
                img_name = os.path.basename(file)
                self.images.append((img_data, img_name))
            except Exception:
                pass
        self._update_image_status()

    def _update_image_status(self):
        """Met a jour le statut des images."""
        count = len(self.images)
        if count > 0:
            self.image_status.configure(
                text=f"{count} image(s)",
                text_color=COLORS["success"]
            )
        else:
            self.image_status.configure(
                text="0 image(s)",
                text_color=COLORS["gray"]
            )

    def _validate(self):
        """Valide et ferme le dialog."""
        email = self.email_entry.get().strip()
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        numero = self.numero_entry.get().strip()

        if not all([email, nom, prenom, numero]):
            messagebox.showwarning("Attention", "Tous les champs sont requis")
            return

        self.result = Recipient(
            email=email,
            nom=nom,
            prenom=prenom,
            numero=numero,
            images=self.images
        )
        self.destroy()
