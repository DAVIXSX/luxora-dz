# Luxora DZ - E-commerce Platform

A modern e-commerce web application built with Flask for the Algerian market.

## Features

- 🛍️ Product catalog with categories
- 📱 Responsive design for mobile and desktop
- 🛒 Order management system
- 📋 Product request functionality
- 👤 Admin authentication and dashboard
- 🏪 Multi-category product organization
- 📸 Multiple product images support
- 📊 Order tracking and management
- 🗃️ SQLite database for easy deployment

## Technologies Used

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Werkzeug Security
- **File Handling**: Secure file uploads

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/luxora-dz.git
cd luxora-dz
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
# Copy .env.example to .env and configure your settings
cp .env.example .env

# IMPORTANT: Edit .env and set your own secure values:
# - SECRET_KEY: Use a long, random string
# - ADMIN_USERNAME: Your admin username
# - ADMIN_PASSWORD: A strong password
```

6. Initialize the database:
```bash
python app.py
```

## Configuration

The application uses environment variables for configuration. Key settings in `.env`:

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `ADMIN_USERNAME`: Admin panel username
- `ADMIN_PASSWORD`: Admin panel password
- `FLASK_ENV`: Environment mode (development/production)

## Usage

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Admin Panel

Access the admin panel at `/admin` with the credentials configured in your environment variables.

## Project Structure

```
luxora-dz/
├── app.py                              # Main application file
├── models.py                           # Database models
├── requirements.txt                    # Python dependencies
├── .env                               # Environment variables
├── templates/                         # HTML templates
│   ├── index.html                     # Homepage
│   ├── product.html                   # Product details
│   ├── customer_info.html             # Order form
│   └── ...
├── static/                            # Static assets
│   ├── css/                          # Stylesheets
│   ├── js/                           # JavaScript files
│   ├── images/                       # Images
│   └── uploads/                      # Uploaded product images
├── instance/                          # Instance-specific files
└── database.db                       # SQLite database
```

## API Endpoints

### Public Endpoints
- `GET /` - Homepage with product listings
- `GET /product/<id>` - Product details page
- `POST /order/<id>` - Place an order
- `POST /api/product-request` - Submit product request

### Admin Endpoints
- `GET /admin` - Admin dashboard
- `POST /admin/login` - Admin authentication
- `GET /admin/products` - Manage products
- `GET /admin/orders` - View orders
- `GET /admin/product-requests` - Manage product requests

## Database Schema

The application uses SQLite with the following main tables:

- **products**: Product information and pricing
- **categories**: Product categories
- **product_images**: Multiple images per product
- **orders**: Customer orders
- **product_requests**: Customer inquiries
- **admins**: Admin user accounts

## Testing

Run the test suite:

```bash
python -m pytest test_*.py
```

Test files included:
- `test_database.py` - Database functionality tests
- `test_users.py` - User authentication tests
- `test_product_requests_api.py` - API endpoint tests
- `test_images.py` - Image handling tests

## Deployment

### Local Deployment

The application can be run locally using the included batch file:

```bash
./start_app.bat
```

### Production Deployment

For production deployment, consider:

1. Using a production WSGI server (Gunicorn, uWSGI)
2. Setting up a reverse proxy (Nginx)
3. Using a production database (PostgreSQL, MySQL)
4. Configuring proper environment variables
5. Setting up SSL/HTTPS

## Security

⚠️ **IMPORTANT SECURITY NOTES**:

1. **Environment Variables**: Never commit `.env` files to version control. Always use `.env.example` as a template.

2. **Admin Credentials**: Change the default admin username and password in your `.env` file before deployment.

3. **Secret Key**: Use a long, random string for `SECRET_KEY` in production. You can generate one using:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

4. **Database**: The SQLite database file (`database.db`) is excluded from version control for security.

5. **Production**: Never run with `FLASK_DEBUG=True` in production.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and version history.

---

**Luxora DZ** - Modern e-commerce solution for Algeria 🇩🇿
