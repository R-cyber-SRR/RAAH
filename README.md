# RAAH
Revolutionary AI-Assisted Hybrid learning platform
# EduManage - Educational Management System

EduManage is a comprehensive educational management system built with Flask and PostgreSQL. It provides separate portals for students and teachers, allowing them to manage learning modules, track attendance, record grades, and communicate through academic notifications. The system also includes advanced AI-assisted learning features.

## Features

### User Authentication
- Secure login system with role-based access (students and teachers)
- User registration with profile creation
- Password encryption and protection

### Student Portal
- View learning modules uploaded by teachers
- Check attendance records and statistics
- Monitor academic performance with grade visualization
- Receive and view academic notifications
- Access AI learning tools

### Teacher Portal
- Upload and manage learning modules
- Record and track student attendance
- Manage student grades and assessments
- Send academic notifications to students
- Access AI teaching tools

### AI Assistant Features
- Speech-to-speech translation
- Text-to-speech conversion
- Speech-to-text transcription
- Text-to-image generation
- Educational assistance for both students and teachers

## Technology Stack

- **Backend:**
  - Python 3.9+
  - Flask (web framework)
  - SQLAlchemy (ORM)
  - psycopg2 (PostgreSQL adapter)
  - Flask-Login (authentication)
  - OpenAI API (for AI assistant features)
  - Werkzeug (for file handling)

- **Frontend:**
  - HTML5
  - CSS3
  - Bootstrap 5
  - Vanilla JavaScript
  - Chart.js (for grade visualization)

- **Database:**
  - PostgreSQL

## Installation and Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database
- OpenAI API key (for AI features)

### Environment Variables
The application requires the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session management
- `OPENAI_API_KEY`: API key for OpenAI services

You may also set these PostgreSQL-specific variables instead of using `DATABASE_URL`:
- `PGUSER`: PostgreSQL username
- `PGPASSWORD`: PostgreSQL password
- `PGHOST`: PostgreSQL host
- `PGPORT`: PostgreSQL port
- `PGDATABASE`: PostgreSQL database name

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/edumanage.git
   cd edumanage
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install flask flask-sqlalchemy flask-login psycopg2-binary openai werkzeug
   ```

4. Set up environment variables (example using export for Linux/Mac):
   ```
   export DATABASE_URL="postgresql://username:password@localhost:5432/edumanage"
   export SESSION_SECRET="your_secret_key"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

5. Initialize the database:
   
