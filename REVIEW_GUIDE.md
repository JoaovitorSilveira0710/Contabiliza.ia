# Contabiliza.IA - Project Review Guide

## Overview
Contabiliza.IA is a comprehensive Brazilian accounting and invoice management system built with Django backend and JavaScript frontend. The system handles NFe (Eletronic Invoice) generation, SEFAZ integration, and financial operations.

## Key Files for Software Engineer Review

### Backend Core Architecture

#### 1. **Django Settings & Configuration**
- `django_backend/contabiliza_backend/settings.py` - Main Django configuration
- `django_backend/contabiliza_backend/middleware.py` - Custom middleware for CSRF handling
- `django_backend/contabiliza_backend/urls.py` - URL routing configuration

#### 2. **Invoice Management System**
- `django_backend/invoices/models.py` - Invoice and InvoiceItem data models
- `django_backend/invoices/views.py` - Invoice API endpoints and business logic
- `django_backend/invoices/serializers.py` - Data serialization for API responses
- `django_backend/invoices/services/nfe_xml_generator.py` - NF-e XML generation
- `django_backend/invoices/services/danfe_sefaz_pr.py` - DANFE PDF generation (SEFAZ-PR standard)
- `django_backend/invoices/services/sefaz_integration.py` - SEFAZ integration service

#### 3. **Legal Case Management**
- `django_backend/legal/models.py` - Legal case data models
- `django_backend/legal/views.py` - Legal API endpoints
- `django_backend/legal/services/court_integration.py` - Court system integration service

#### 4. **Financial Management**
- `django_backend/financial/models.py` - Financial transaction models
- `django_backend/financial/views.py` - Financial API endpoints
- `django_backend/financial/services/receipt_analyzer.py` - Receipt analysis service

#### 5. **Stock Management**
- `django_backend/stock/models.py` - Stock and warehouse models
- `django_backend/stock/views.py` - Stock API endpoints

#### 6. **Client Management**
- `django_backend/clients/models.py` - Client data models
- `django_backend/clients/views.py` - Client API endpoints
- `django_backend/clients/serializers.py` - Client data serialization

#### 7. **Authentication & Core**
- `django_backend/core/models.py` - User and authentication models
- `django_backend/core/auth_views.py` - Authentication endpoints
- `django_backend/core/serializers.py` - Authentication serialization

### Frontend Architecture

#### 1. **API Layer**
- `frontend/src/js/api.js` - Main API client for backend communication
- `frontend/src/js/api-service.js` - Service layer for API calls
- `frontend/src/js/config.js` - Frontend configuration and constants

#### 2. **UI Components**
- `frontend/src/js/react-app.js` - Main React application with all components
- `frontend/src/js/ui-helper.js` - UI helper utilities
- `frontend/src/js/estoque-service.js` - Stock management service

#### 3. **Pages**
- `frontend/pages/dashboard.html` - Main dashboard
- `frontend/pages/notas-fiscais.html` - Invoice management page
- `frontend/pages/clientes.html` - Client management page
- `frontend/pages/financeiro.html` - Financial management page
- `frontend/pages/juridico.html` - Legal case management page
- `frontend/pages/estoque.html` - Stock management page
- `frontend/pages/login.html` - Authentication page

### Documentation

- `docs/SISTEMA_NOTAS_FISCAIS.md` - Complete NFe system documentation
- `docs/INTEGRACAO_SEFAZ.md` - SEFAZ integration guide
- `README.md` - Project overview and setup instructions

### Configuration Files

- `docker-compose.yml` - Docker services configuration
- `Dockerfile` - Docker image definition
- `nginx.conf` - Nginx configuration
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `tailwind.config.js` - Tailwind CSS configuration
- `eslint.config.cjs` - ESLint configuration

## Architecture Overview

### Technology Stack

**Backend:**
- Django REST Framework
- PostgreSQL/SQLite
- Python 3.8+
- SEFAZ integration for Brazilian tax compliance

**Frontend:**
- HTML5 / CSS3 / JavaScript (ES6+)
- React library for components
- Tailwind CSS for styling
- Font Awesome icons

**DevOps:**
- Docker & Docker Compose
- Nginx reverse proxy
- Git version control

### Key Features

1. **NF-e Management**
   - Generate XML in SEFAZ v4.00 standard
   - Create DANFE (PDF) documents
   - SEFAZ integration for authorization
   - Support for rural producer invoices

2. **Financial Operations**
   - Transaction tracking
   - Receipt analysis
   - Financial dashboard

3. **Legal Case Management**
   - Court system integration
   - Process number tracking
   - Legal documentation management

4. **Stock Management**
   - Inventory tracking
   - Warehouse management
   - Stock movements

5. **Client Management**
   - Client registration
   - Contact information
   - Address management

## Data Flow

### Invoice Creation Flow
1. Client creates invoice in frontend
2. Frontend sends data to `invoices/create/` endpoint
3. Backend generates access key
4. XML is generated using SEFAZ standard
5. PDF (DANFE) is generated
6. Files are backed up to storage

### SEFAZ Integration Flow
1. XML is validated against schema
2. Digital certificate is applied
3. Request is sent to SEFAZ
4. Authorization status is received
5. Invoice status is updated

## Testing

- `django_backend/invoices/tests.py` - Invoice generation tests
- `django_backend/legal/tests.py` - Legal module tests
- `django_backend/clients/tests.py` - Client management tests

## Deployment

- Run with: `python django_backend/manage.py runserver`
- Docker deployment: `docker-compose up`
- Frontend accessible at: `http://localhost/pages/dashboard.html`

## Recent Updates (December 2025)

- Full translation of comments to English
- Removal of all emojis from documentation
- Code standardization for professional presentation
- Improved documentation clarity

## Next Steps for Engineer Review

1. Review invoice/NF-e generation system
2. Examine SEFAZ integration implementation
3. Analyze security measures (CSRF handling, authentication)
4. Review database models and relationships
5. Test API endpoints
6. Verify Docker deployment

---

For detailed technical documentation, refer to the individual service files and API endpoints.
