# Django E-commerce Platform

A full-stack e-commerce application built with Django and Django REST Framework, featuring a web interface and RESTful APIs for mobile application integration.

## Overview

This project is an online jewelry and accessories store developed using Django. It provides product management, user authentication, shopping cart functionality, order processing, and product reviews.

The backend is designed to serve both the web application and external clients, including Android applications.

## Technologies

### Backend
- Python
- Django 5.2
- Django REST Framework
- Django REST Framework Simple JWT
- SQLite

### Frontend
- HTML5
- CSS3
- JavaScript
- React
- Vite

## Features

- User registration and authentication
- JWT-based API authentication
- User profile management
- Product listing and product details
- Product categories and filtering
- Product image management
- Shopping cart
- Order and checkout management
- Product reviews and ratings
- Django Admin integration
- RESTful APIs for mobile application integration

## Project Structure

```text
shop/
├── accounts/
├── cart/
├── config/
├── frontend/
├── orders/
├── products/
├── templates/
├── manage.py
└── requirements.txt
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/maheht/django-ecommerce.git
cd django-ecommerce
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Set a secure Django secret key using the `DJANGO_SECRET_KEY` environment variable.

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open the application at:

http://127.0.0.1:8000/

## API

The backend provides RESTful API endpoints designed for integration with mobile applications.

Authentication uses JSON Web Tokens (JWT).

## Future Improvements

- Automated testing
- Improved API documentation
- Enhanced