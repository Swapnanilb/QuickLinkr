# QuickLinkr

A smart, feature-rich URL shortener built with FastAPI that transforms long URLs into intelligent short links with advanced analytics, QR codes, and enterprise features.

## 🚀 Features

### Core Features
- ✅ **URL Shortening** - Convert long URLs to short, memorable codes
- ✅ **Custom Short Codes** - Choose your own personalized short codes
- ✅ **URL Validation** - Automatically validates URL reachability before shortening
- ✅ **QR Code Generation** - Auto-generate QR codes for all shortened URLs
- ✅ **URL Expiration** - Set expiration dates (1 day to 1 year or never)

### Analytics & Tracking
- ✅ **Analytics Dashboard** - Comprehensive statistics and insights
- ✅ **Click Tracking** - Real-time click counting with detailed logs
- ✅ **Performance Metrics** - Daily, weekly, and total statistics
- ✅ **Top URLs** - Identify your most popular links
- ✅ **Visual Charts** - Interactive bar charts for click analytics

### Bulk Operations
- ✅ **Bulk Processing** - Shorten multiple URLs simultaneously
- ✅ **CSV Upload** - Upload and process CSV files with URLs
- ✅ **Batch Analytics** - Process hundreds of URLs at once

### User Experience
- ✅ **Modern Web Interface** - Beautiful tabbed interface with gradients
- ✅ **Mobile Responsive** - Works perfectly on all devices
- ✅ **Copy to Clipboard** - One-click copying with toast notifications
- ✅ **Interactive Swagger UI** - Complete API documentation

## 🛠️ Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic with custom validators
- **QR Codes**: qrcode library with PIL
- **HTTP Client**: httpx for URL validation
- **Frontend**: Vanilla HTML/CSS/JavaScript

## 📦 Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd url-shortener
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run database migration** (if upgrading):
```bash
python migrate_db.py
```

5. **Start the application**:
```bash
uvicorn app.main:app --reload
```

## 🌐 Access Points

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🎯 API Endpoints

### URL Management
```http
POST /shorten
```
Create a shortened URL with optional custom code and expiration
```json
{
  "url": "https://example.com/very-long-url",
  "custom_code": "my-link",
  "expires_in_days": 30
}
```

```http
GET /{code}
```
Redirect to original URL (tracks clicks)

```http
GET /info/{code}
```
Get URL statistics and metadata

### Bulk Operations
```http
POST /bulk-shorten
```
Shorten multiple URLs
```json
{
  "urls": ["https://example1.com", "https://example2.com"]
}
```

```http
POST /bulk-upload
```
Upload CSV file for bulk processing

### Analytics
```http
GET /api/analytics
```
Get comprehensive analytics dashboard data

```http
GET /api/history
```
Get recent URL history (last 10)

```http
DELETE /api/history
```
Clear all URL history

## 💾 Database Schema

### URLs Table
| Field      | Type     | Description                    |
|------------|----------|--------------------------------|
| id         | Integer  | Primary key                    |
| original   | String   | Original long URL              |
| short      | String   | Unique short code              |
| clicks     | Integer  | Total click count              |
| created_at | DateTime | Creation timestamp             |
| expires_at | DateTime | Expiration date (nullable)     |

### Click Logs Table
| Field      | Type     | Description                    |
|------------|----------|--------------------------------|
| id         | Integer  | Primary key                    |
| url_id     | Integer  | Foreign key to URLs           |
| clicked_at | DateTime | Click timestamp                |
| user_agent | String   | Browser/client information     |
| ip_address | String   | Client IP address              |

## 🎨 Web Interface

### Tabs Overview
1. **✨ Single URL** - Create individual short URLs with custom codes and expiration
2. **📦 Bulk URLs** - Process multiple URLs or upload CSV files
3. **📊 History** - View and manage your shortened URLs
4. **📈 Analytics** - Comprehensive dashboard with statistics and charts

### Key Features
- **Gradient Design** - Modern, professional appearance
- **Real-time Validation** - Instant feedback on URL validity
- **QR Code Display** - Visual QR codes for easy sharing
- **Statistics Cards** - Quick overview of key metrics
- **Interactive Charts** - Visual representation of click data
- **Toast Notifications** - User-friendly feedback system

## 📁 CSV Upload Format

Create a CSV file with one URL per line:
```
https://example1.com
https://example2.com
https://example3.com
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL` - Database connection string (default: SQLite)
- `HOST` - Server host (default: localhost)
- `PORT` - Server port (default: 8000)

### Customization
- Modify `generate_short_code()` function for different code patterns
- Adjust expiration options in the frontend dropdown
- Customize analytics time ranges in the backend

## 🚀 Deployment

### Production Setup
1. Use PostgreSQL instead of SQLite
2. Set up reverse proxy (Nginx)
3. Use production ASGI server (Gunicorn + Uvicorn)
4. Configure environment variables
5. Set up SSL certificates

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Portfolio Highlights

This project demonstrates:
- **Full-stack Development** - FastAPI backend + responsive frontend
- **Database Design** - Relational schema with proper indexing
- **API Development** - RESTful endpoints with comprehensive documentation
- **Data Analytics** - Statistical calculations and visualizations
- **User Experience** - Modern, intuitive interface design
- **Error Handling** - Graceful error management and user feedback
- **Performance** - Efficient database queries and caching strategies
- **Security** - URL validation and input sanitization