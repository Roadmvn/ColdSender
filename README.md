```
   ______      __    ______               __
  / ____/___  / /___/ / ___/__  ____  ____/ /__  _____
 / /   / __ \/ / __  /\__ \/ _ \/ __ \/ __  / _ \/ ___/
/ /___/ /_/ / / /_/ /___/ /  __/ / / / /_/ /  __/ /
\____/\____/_/\__,_//____/\___/_/ /_/\__,_/\___/_/
```

Mass email delivery system. Silent. Efficient. Cold.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Features

- Bulk email sending with SMTP relay
- Import recipients from Excel/CSV
- Personalized templates with placeholders (`{{nom}}`, `{{prenom}}`, `{{numero}}`, `{{email}}`)
- Attach images with live preview
- Modern GUI built with CustomTkinter
- Real-time progress tracking
- Success/failure logging

## Installation

```bash
git clone https://github.com/Roadmvn/ColdSender.git
cd ColdSender
pip install -r requirements.txt
python main.py
```

Or use the batch files:
- `INSTALL.bat` - Install dependencies
- `run.bat` - Launch the app
- `build.bat` - Create standalone .exe

## Usage

1. **Import Data** - Load your recipient list (Excel/CSV with columns: `email`, `nom`, `prenom`, `numero`)
2. **Compose Message** - Write your email template using placeholders
3. **Add Image** - Optionally attach an image (preview included)
4. **Configure SMTP** - Set up your email provider credentials
5. **Send** - Hit the button and watch the magic happen

## SMTP Providers

| Provider | Server | Port |
|----------|--------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

> For Gmail, use an [App Password](https://myaccount.google.com/apppasswords)

## Project Structure

```
ColdSender/
├── main.py              # Entry point
├── src/
│   ├── config.py        # SMTP providers, colors
│   ├── models.py        # Data classes
│   ├── services/
│   │   ├── email_service.py
│   │   └── data_service.py
│   └── ui/
│       ├── app.py
│       └── tabs/
├── requirements.txt
└── *.bat                # Windows scripts
```

## Disclaimer

For educational purposes only. Use responsibly.

## License

MIT
