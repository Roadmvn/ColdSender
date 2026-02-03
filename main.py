"""
Point d'entrée de l'application Mail Sender.
"""

from src.ui import MailSenderApp


def main():
    """Fonction principale."""
    app = MailSenderApp()
    app.run()


if __name__ == "__main__":
    main()
