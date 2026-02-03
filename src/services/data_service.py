"""
Service de gestion des données (fichiers, templates).
"""

import os
import zipfile
from typing import Optional, Dict, List, Tuple

import pandas as pd

from ..models import Recipient


class DataService:
    """Service de gestion des données."""

    @staticmethod
    def load_file(filepath: str) -> Tuple[List[Recipient], Optional[str]]:
        """
        Charge un fichier Excel ou CSV.

        Args:
            filepath: Chemin du fichier

        Returns:
            Tuple (liste de destinataires, message d'erreur ou None)
        """
        try:
            # Charger selon le format
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            # Vérifier les colonnes requises
            required = ['email', 'nom', 'prenom', 'numero']
            missing = [c for c in required if c not in df.columns]

            if missing:
                return [], f"Colonnes manquantes : {', '.join(missing)}"

            # Créer les destinataires
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
        """
        Crée un fichier template Excel.

        Args:
            filepath: Chemin où sauvegarder le fichier

        Returns:
            Message d'erreur ou None si succès
        """
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
    def load_images_zip(filepath: str) -> Tuple[Dict[str, bytes], Optional[str]]:
        """
        Charge les images depuis un fichier ZIP.
        Les noms de fichiers (sans extension) servent de clés.

        Args:
            filepath: Chemin du fichier ZIP

        Returns:
            Tuple (dictionnaire email->image_bytes, message d'erreur ou None)
        """
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
