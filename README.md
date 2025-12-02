<div align="center">

# Contabiliza.IA

Integrated accounting, financial, tax and legal management system

![Status](https://img.shields.io/badge/status-Production-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-5.1+-green)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

---

## Overview

**Contabiliza.IA** is a comprehensive management system designed for accounting firms, centralizing client management, financial transactions, tax obligations, legal processes, and invoices with real-time metrics and intelligent alerts to reduce repetitive tasks.

### Main Modules

- **Clients** - Individuals/Companies, farms, contracts, status tracking
- **Financial** - Transactions, cash flow, bank accounts, categories, payment methods
- **Invoices** - NFe generation (SEFAZ compliant), XML/PDF download, import
- **Legal** - Legal processes, deadlines, hearings, contracts
- **Stock** - Products, suppliers, warehouses, inventory management
- **Dashboard** - Real-time metrics, charts, financial overview

---

## Architecture

```
Contabiliza.IA/
├── django_backend/           # Django REST API Backend
│   ├── core/                 # Authentication, users (Token + Session)
│   ├── clients/              # Clients and farms management
│   ├── invoices/             # Invoice generation (NFe v4.00)
│   │   └── services/         # XML generator, PDF DANFE, backup
│   ├── financial/            # Transactions, categories, accounts
│   │   └── services/         # Receipt analyzer (PDF/image OCR)
│   ├── legal/                # Legal processes and contracts
│   ├── stock/                # Stock and warehouse management
│   └── contabiliza_backend/  # Settings, URLs, middleware
├── frontend/                 # Frontend (Vanilla JS + React 18)
│   ├── pages/                # HTML pages (dashboard, financeiro, etc.)
│   └── src/
│       ├── js/               # API service, config, React components
│       └── styles/           # CSS and TailwindCSS
├── storage/                  # Media files (attachments, receipts)
├── backups/                  # Automatic backups (invoices XML/PDF)
├── venv/                     # Python virtual environment
├── run.py                    # Quick start script
└── requirements.txt          # Python dependencies
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git

### Installation

```powershell
# Clone repository
git clone https://github.com/JoaovitorSilveira0710/Contabiliza.ia.git
cd Contabiliza.IA

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python run.py
```

**Server will be available at:**
- Frontend: `http://localhost:8000/`
- API: `http://localhost:8000/api/`
- Admin Panel: `http://localhost:8000/admin/`

### First Access

Default credentials (change after first login):
- **Username:** `admin`
- **Password:** `admin123`

---

## Key Features

### Financial Management
- Transaction tracking (revenue/expenses)
- Multiple payment methods (PIX, TED, Cash, Card, Boleto)
- Receipt analysis (PDF/image with OCR)
- Bank account management
- Dynamic category filtering
- Real-time charts and summaries

### Invoice System (NFe)
- SEFAZ-compliant XML generation (NFe v4.00)
- Mod 11 access key calculation
- DANFE PDF generation (layout as per SEFAZ standards)
- Automatic XML/PDF backup
- Import invoices from external sources
- Client auto-registration from XML data

### Client Management
- Individual and company profiles
- Farm registration with specific documentation tracking
- Contract management
- Multi-client support with pagination

### Legal Module
- Process tracking
- Deadline monitoring
- Hearing scheduling
- Contract management

---

## API Endpoints

### Authentication
```
POST /api/auth/login/          # Login (returns token)
POST /api/auth/logout/         # Logout
GET  /api/auth/check/          # Check authentication status
```

### Clients
```
GET    /api/clients/           # List clients (paginated)
POST   /api/clients/           # Create client
GET    /api/clients/{id}/      # Get client details
PUT    /api/clients/{id}/      # Update client
DELETE /api/clients/{id}/      # Delete client
GET    /api/farms/             # List farms
```

### Financial
```
GET  /api/financial-transactions/       # List transactions
POST /api/financial-transactions/       # Create transaction
GET  /api/financial-transactions/{id}/  # Transaction details
PUT  /api/financial-transactions/{id}/  # Update transaction
GET  /api/financial-transactions/summary/ # Financial summary
GET  /api/financial-categories/         # List categories
GET  /api/bank-accounts/                # List bank accounts
```

### Invoices
```
GET    /api/invoices/                   # List invoices
POST   /api/invoices/                   # Create invoice
GET    /api/invoices/{id}/              # Invoice details
POST   /api/invoices/{id}/authorize/    # Authorize invoice
GET    /api/invoices/{id}/download-xml/ # Download XML
GET    /api/invoices/{id}/download-pdf/ # Download DANFE PDF
```

### Legal
```
GET  /api/legal-processes/    # List processes
POST /api/legal-processes/    # Create process
GET  /api/hearings/           # List hearings
GET  /api/legal-contracts/    # List contracts
```

---

## Technology Stack

**Backend:**
- Django 5.1
- Django REST Framework
- SQLite (development) / PostgreSQL (production ready)
- Token Authentication
- BCrypt password hashing

**Frontend:**
- React 18 (via CDN)
- Vanilla JavaScript
- TailwindCSS
- Chart.js for visualizations
- Font Awesome icons

**Document Generation:**
- ReportLab (PDF)
- pdfminer.six (PDF text extraction)
- Pillow (image processing)
- Optional: pytesseract (OCR)

**Infrastructure:**
- File-based storage system
- Automatic backup mechanism
- CORS enabled for development
- Cache-busting for static files

---

## Advanced Usage

### Seed Financial Data
```powershell
cd django_backend
python manage.py seed_financial
```

### Create Superuser
```powershell
cd django_backend
python manage.py createsuperuser
```

### Database Backup
```powershell
cd django_backend
python manage.py backup_database
```

### Start Server on Network
```powershell
.\start_django.ps1
```

### Run Migrations
```powershell
cd django_backend
python manage.py makemigrations
python manage.py migrate
```

---

## Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### CORS Settings
Located in `django_backend/contabiliza_backend/settings.py`:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Development only
CORS_ALLOW_CREDENTIALS = True
```

### Media and Backup Storage
```python
MEDIA_ROOT = BASE_DIR.parent / 'storage'
BACKUP_DIR = BASE_DIR.parent / 'backups'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `Get-Process python \| Stop-Process -Force` |
| Missing dependencies | `pip install -r requirements.txt` |
| Migration errors | `cd django_backend; python manage.py migrate` |
| CORS errors | Clear browser cache / restart server |
| 404 on static files | Check `STATICFILES_DIRS` in settings.py |
| React component not loading | Hard refresh browser (Ctrl+F5) |

---


## Roadmap

**Current Phase:** Production-ready MVP
- ✅ Complete CRUD for all modules
- ✅ SEFAZ-compliant invoice generation
- ✅ Receipt analysis with OCR
- ✅ Real-time financial dashboard
- ✅ Dynamic filtering and search

**Next Steps:**
- JWT authentication
- Multi-tenant support
- External integrations (SEFAZ, Receita Federal)
- Predictive financial analytics
- Mobile responsive improvements
- Docker containerization

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Author

**João Vitor Cruz da Silveira**  
Email: joaovitor2401@gmail.com  
Phone: +55 42 99166-2179  
GitHub: [@JoaovitorSilveira0710](https://github.com/JoaovitorSilveira0710)

---

**Contabiliza.IA** – Operational efficiency for modern accounting firms.
