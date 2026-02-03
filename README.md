# 🥶 ColdSender

Mass email delivery system. Silent. Efficient. Cold.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Features

- 📧 Bulk email sending with SMTP relay
- 📊 Import recipients from Excel/CSV
- ✏️ Personalized templates with placeholders (`{{nom}}`, `{{prenom}}`, `{{numero}}`, `{{email}}`)
- 🖼️ Attach images (default or per-recipient from ZIP)
- 🎨 Modern dark GUI built with CustomTkinter
- 📈 Real-time progress tracking
- ✅ Success/failure logging

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ColdSender.git
cd ColdSender
pip install -r requirements.txt
python app.py
```

## Usage

1. **Import Data** - Load your recipient list (Excel/CSV with columns: `email`, `nom`, `prenom`, `numero`)
2. **Compose Message** - Write your email template using placeholders
3. **Configure SMTP** - Set up your email provider credentials
4. **Send** - Hit the button and watch the magic happen

## SMTP Providers

| Provider | Server | Port |
|----------|--------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

> ⚠️ For Gmail, use an [App Password](https://myaccount.google.com/apppasswords)

## Disclaimer

For educational purposes only. Use responsibly.

## License

MIT
