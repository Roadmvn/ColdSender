"""
Onglet Données - Import et gestion des destinataires.
"""

import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox

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
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_import_section(container)
        self._build_preview_section(container)

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

        self.tree = ttk.Treeview(tree_container, show="headings", height=15)
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
            self.tree.column(col, width=200, anchor="w")

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
            indices = sorted([self.tree.index(item) for item in selected], reverse=True)
            for idx in indices:
                del self.app_data.recipients[idx]
            self._update_preview()


class RecipientDialog(ctk.CTkToplevel):
    """Dialog pour ajouter/modifier un destinataire."""

    def __init__(self, parent, title: str, recipient: Recipient = None):
        super().__init__(parent)
        self.result = None
        self.recipient = recipient

        self.title(title)
        self.geometry("400x380")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 380) // 2
        self.geometry(f"+{x}+{y}")

        self.wait_window()

    def _build_ui(self):
        """Construit l'interface du dialog."""
        ctk.CTkLabel(self, text="Email", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(20, 5))
        self.email_entry = ctk.CTkEntry(self, width=360, height=35)
        self.email_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Nom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.nom_entry = ctk.CTkEntry(self, width=360, height=35)
        self.nom_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Prenom", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.prenom_entry = ctk.CTkEntry(self, width=360, height=35)
        self.prenom_entry.pack(padx=20)

        ctk.CTkLabel(self, text="Numero", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(10, 5))
        self.numero_entry = ctk.CTkEntry(self, width=360, height=35)
        self.numero_entry.pack(padx=20)

        if self.recipient:
            self.email_entry.insert(0, self.recipient.email)
            self.nom_entry.insert(0, self.recipient.nom)
            self.prenom_entry.insert(0, self.recipient.prenom)
            self.numero_entry.insert(0, self.recipient.numero)

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
