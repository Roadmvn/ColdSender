"""
Configuration de l'application.
"""

# Fournisseurs SMTP supportes
SMTP_PROVIDERS = {
    "Gmail": ("smtp.gmail.com", 587),
    "Outlook/Hotmail": ("smtp-mail.outlook.com", 587),
    "Yahoo": ("smtp.mail.yahoo.com", 587),
    "Autre": ("", 587),
}

# Fournisseurs API (pas de SMTP)
API_PROVIDERS = ["SendGrid"]

# Tous les fournisseurs
ALL_PROVIDERS = list(SMTP_PROVIDERS.keys()) + API_PROVIDERS

# Couleurs du thème
COLORS = {
    "primary": "#1e40af",
    "success": "#059669",
    "error": "#dc2626",
    "warning": "#d97706",
    "gray": "#6b7280",
    "light_gray": "#f3f4f6",
}
