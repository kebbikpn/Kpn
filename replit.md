# Overview

The Kebbi Progressive Network (KPN) is a Flask-based web platform designed to strengthen youth mobilization, promote civic engagement, and advocate for good governance across Kebbi State, Nigeria. The platform serves as a comprehensive digital network connecting citizens, leaders, and organizations through various modules including campaign management, event coordination, media galleries, donation systems, duty assignments, and disciplinary actions. The system implements a hierarchical role-based structure spanning from state executives down to ward-level leaders, with sophisticated jurisdiction-based access controls.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses server-side rendering with Jinja2 templates and Bootstrap 5 for responsive design. The template system employs a base template with modular components, implementing consistent KPN branding with custom CSS variables for color theming. JavaScript integration handles dynamic interactions like form validation, modal displays, and AJAX requests for enhanced user experience.

## Backend Architecture
Built on Flask with a modular blueprint structure organizing functionality into distinct modules: core (public pages), staff (authentication/dashboards), leadership (approvals/management), campaigns, donations, media, events, registration, duty_logs, and disciplinary. Each blueprint handles its specific domain logic while sharing common authentication and authorization patterns.

## Authentication & Authorization
Implements Flask-Login for session management with role-based access control using enum-defined user roles (ADMIN, EXECUTIVE, ZONAL_COORDINATOR, LGA_LEADER, WARD_LEADER, GENERAL_MEMBER). Authorization logic in auth_helpers.py enforces hierarchical jurisdiction rules - users can only manage subordinates within their geographical and organizational scope. CSRF protection is enabled across all forms.

## Database Design
Uses SQLAlchemy ORM with enum-based status tracking for approval workflows, action types, and role definitions. The schema implements a hierarchical geographical structure (Zone → LGA → Ward) mirroring Kebbi State's administrative divisions. User relationships are established through foreign keys linking users to their assigned geographical locations and organizational hierarchy.

## Data Management
The seed_data.py module preloads the database with complete Kebbi State geographical data including all 3 zones, 21 LGAs, and their respective wards. User registration includes seat availability checking for leadership positions to prevent duplicate appointments. File uploads are handled with secure filename generation and organized directory structures.

## Session & Security
Configured with secure session cookies, HTTP-only flags, and 24-hour session lifetime. File upload limits are set to 16MB with CSRF time limits disabled for long-form submissions. Environment-based configuration allows for development and production security settings.

# External Dependencies

## Core Framework
- **Flask**: Web framework with SQLAlchemy ORM for database operations
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: CSRF protection and form handling
- **Werkzeug**: Password hashing and secure file uploads

## Frontend Libraries
- **Bootstrap 5**: Responsive CSS framework and UI components
- **Font Awesome 6**: Icon library for consistent visual elements
- **JavaScript**: Client-side form validation and dynamic interactions

## Database
- **SQLite**: Default database for development with environment variable override support
- **PostgreSQL**: Production database option through DATABASE_URL configuration

## Optional Integrations
- **Facebook Graph API**: Social media verification system for user registration (requires FACEBOOK_APP_ID and FACEBOOK_APP_SECRET environment variables)
- **File Storage**: Local file system for media uploads with configurable paths

## Environment Configuration
The system relies on environment variables for:
- SECRET_KEY: Session encryption
- DATABASE_URL: Database connection string  
- FACEBOOK_APP_ID/SECRET: Social media integration
- FLASK_ENV: Environment-specific security settings