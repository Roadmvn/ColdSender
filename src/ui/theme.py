"""
Configuration du thème de l'application.
"""

import customtkinter as ctk

from ..config import COLORS


def setup_theme():
    """Configure le thème global de l'application."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def get_colors():
    """Retourne le dictionnaire des couleurs."""
    return COLORS
