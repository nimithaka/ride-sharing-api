# Ride Sharing API

A RESTful API for a ride-sharing application built using Django Rest Framework (DRF).

## Features
- User Authentication (Token-based)
- Creating a ride request, viewing a ride's details, and listing all rides.
- Updating the status of a ride from 'requested' to 'matched', 'in progress', 'completed' or 'cancelled'.
- Updating the current location of the ride.
- View nearby drivers that are within a 1km proximity of their location

## Technologies Used
- Python
- Django Rest Framework (DRF)
- SQLite

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone git@github.com:nimithaka/ride-sharing-api.git
cd ride-sharing-api
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```
Access the API at: `http://127.0.0.1:8000/`# Ride Sharing API
