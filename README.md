# Laydies Den Backend API

A comprehensive Django REST API backend for the Laydies Den wellness and beauty platform.

## Features

### Core Applications

1. **Accounts** - User authentication and profile management
2. **Products** - Product catalog with categories, variants, and reviews
3. **Services** - Spa services, therapists, and packages
4. **Appointments** - Booking system for services
5. **Orders** - Order management for products and services
6. **Payments** - Payment processing and transaction management
7. **Cart** - Shopping cart functionality

### Key Features

- **JWT Authentication** - Secure token-based authentication
- **Email-based Login** - Users login with email instead of username
- **Admin Panel** - Comprehensive Django admin interface
- **API Documentation** - RESTful API endpoints
- **Image Upload** - Support for product and service images
- **Search & Filtering** - Advanced search and filtering capabilities
- **Pagination** - Efficient data pagination
- **CORS Support** - Cross-origin resource sharing for frontend integration

## API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get product details
- `GET /api/products/categories/` - List product categories
- `GET /api/products/featured/` - List featured products
- `POST /api/products/{id}/reviews/` - Add product review

### Services
- `GET /api/services/` - List all services
- `GET /api/services/{id}/` - Get service details
- `GET /api/services/categories/` - List service categories
- `GET /api/services/therapists/` - List therapists
- `GET /api/services/featured/` - List featured services

### Appointments
- `GET /api/appointments/` - List user bookings
- `POST /api/appointments/` - Create new booking
- `GET /api/appointments/available-slots/` - Get available time slots
- `POST /api/appointments/{id}/cancel/` - Cancel booking

### Orders
- `GET /api/orders/` - List user orders
- `POST /api/orders/from-cart/` - Create order from cart
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/{id}/cancel/` - Cancel order

### Cart
- `GET /api/cart/` - Get user cart
- `POST /api/cart/add/` - Add item to cart
- `PUT /api/cart/items/{id}/` - Update cart item
- `DELETE /api/cart/items/{id}/` - Remove cart item

### Payments
- `GET /api/payments/` - List user payments
- `POST /api/payments/process/` - Process payment
- `GET /api/payments/methods/` - List payment methods

## Models Overview

### User Management
- **User** - Custom user model with email authentication
- **UserProfile** - Extended user information and preferences

### Product Management
- **Category** - Product categories
- **Product** - Main product model
- **ProductVariant** - Product variations (size, color, etc.)
- **ProductImage** - Product images
- **Review** - Product reviews and ratings
- **Wishlist** - User wishlists

### Service Management
- **ServiceCategory** - Service categories
- **Service** - Available services
- **Therapist** - Service providers
- **ServicePackage** - Service bundles
- **ServiceAddon** - Additional service options

### Booking System
- **Booking** - Service appointments
- **TimeSlot** - Available time slots
- **BookingCancellation** - Cancellation records
- **RecurringBooking** - Recurring appointments

### Order Management
- **Order** - Product orders
- **OrderItem** - Individual order items
- **ServiceOrder** - Service-specific orders
- **OrderTracking** - Order status tracking
- **Coupon** - Discount coupons

### Payment System
- **Payment** - Payment records
- **PaymentMethod** - Available payment methods
- **Transaction** - Transaction logs

### Shopping Cart
- **Cart** - User shopping carts
- **CartItem** - Cart items
- **SavedItem** - Saved for later items

## Setup Instructions

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (or SQLite for development)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   python manage.py createsuperuser --email your-email@example.com
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

### Testing the Setup

Run the verification script:
```bash
python test_backend.py
```

## Admin Panel

Access the Django admin panel at: `http://127.0.0.1:8000/admin/`

### Admin Features
- User management with profiles
- Product catalog management
- Service and therapist management
- Booking and appointment management
- Order tracking and management
- Payment monitoring
- Coupon management

## Configuration

### Key Settings
- **Authentication**: JWT-based with email login
- **File Uploads**: Media files stored in `media/` directory
- **CORS**: Configured for frontend integration
- **Pagination**: 20 items per page by default
- **Time Zone**: Africa/Nairobi

### Security Features
- CSRF protection
- Secure password validation
- JWT token rotation
- User permission controls

## Development

### Adding New Features
1. Create models in appropriate app
2. Create serializers for API
3. Implement views with proper permissions
4. Add URL patterns
5. Create admin configurations
6. Write tests

### Code Structure
- **Models**: Database schema definitions
- **Serializers**: API request/response formatting
- **Views**: Business logic and API endpoints
- **URLs**: Route definitions
- **Admin**: Admin panel configurations

## Production Deployment

### Environment Setup
1. Set `DEBUG=False`
2. Configure production database
3. Set up proper email backend
4. Configure static file serving
5. Set up SSL certificates
6. Configure domain settings

### Security Checklist
- [ ] Update SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure secure cookies
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting

## Support

For issues and support:
- Check the Django documentation
- Review API endpoint documentation
- Test with the provided verification script
- Check server logs for errors

## License

This project is part of the Laydies Den platform.
