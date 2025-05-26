# Logistics Delivery Management System API

## Overview

This project is a FastAPI-based backend for a Logistics Delivery Management System. It provides a comprehensive suite of APIs to manage user authentication, shipment creation and tracking, user profiles, pricing information, feedback, and support tickets. The system is designed to be modular and scalable, leveraging modern Python technologies.

## Features

*   **User Authentication**: Secure registration and login using JWT (Access and Refresh tokens), password recovery.
*   **Shipment Management**:
    *   Create and track shipments with unique tracking numbers.
    *   Manage pickup and delivery addresses and time windows.
    *   Update shipment status.
    *   Filter shipments by status.
*   **User Profile Management**:
    *   View and update user profile information (name, phone, default address, notification preferences).
    *   Terms of service acceptance tracking.
    *   Preferred service levels and pickup windows.
*   **Pricing System**:
    *   Dynamic cost calculation based on service tiers (Express, Standard, Economy).
    *   API to fetch available pricing tiers.
*   **Feedback and Rating System**:
    *   Allow users to submit feedback and ratings for shipments or general service.
*   **Support Ticket Management**:
    *   Users can create and manage support tickets for issues.
    *   Status tracking for support tickets.
*   **Database Migrations**: Handled by Alembic for schema evolution.
*   **Async Support**: Built with `async` and `await` for non-blocking I/O, suitable for high-concurrency.
*   **Dependency Management**: Uses Poetry for managing project dependencies.

## Tech Stack/Dependencies

*   **Programming Language**: Python 3.9+
*   **Web Framework**: FastAPI
*   **Database ORM**: SQLAlchemy (with async support via `asyncpg`)
*   **Database Migration**: Alembic
*   **Data Validation**: Pydantic & Pydantic-Settings
*   **Authentication**: Python-JOSE for JWT, Passlib for password hashing
*   **ASGI Server**: Uvicorn
*   **Rate Limiting**: SlowAPI (though not explicitly implemented in detail in this plan, it's in dependencies)
*   **Database Backend Service**: Assumed to be a PostgreSQL-compatible service (e.g., Supabase, or any standard PostgreSQL instance).

Key Python dependencies (from `pyproject.toml`):
*   `fastapi = "^0.104.1"`
*   `uvicorn = {extras = ["standard"], version = "^0.23.2"}`
*   `pydantic = "^2.4.2"`
*   `pydantic-settings = "^2.0.3"`
*   `sqlalchemy = "^2.0.22"`
*   `asyncpg = "^0.28.0"`
*   `python-jose = {extras = ["cryptography"], version = "^3.3.0"}`
*   `passlib = {extras = ["bcrypt"], version = "^1.7.4"}`
*   `alembic = "^1.12.0"`
*   `httpx = "^0.25.0"` (useful for testing or external API calls)
*   `slowapi = "^0.1.8"`

## Project Structure

*   `app/`: Contains the core application code.
    *   `api/`: API endpoint definitions, structured by version and specific endpoints.
    *   `core/`: Core logic, including configuration (`config.py`) and security (`security.py`).
    *   `crud/`: CRUD (Create, Read, Update, Delete) operations for database models.
    *   `db/`: Database session management (`session.py`) and base model definitions (`base.py`).
    *   `models/`: SQLAlchemy ORM models.
    *   `schemas/`: Pydantic schemas for data validation and serialization, including enums.
    *   `services/`: Business logic and service layer functions (e.g., shipment creation, pricing calculation).
    *   `main.py`: FastAPI application entry point.
*   `alembic/`: Database migration scripts and Alembic configuration.
    *   `versions/`: Individual migration files.
    *   `env.py`: Alembic environment setup.
*   `tests/`: (Placeholder) Unit and integration tests.
*   `.env.example`: Example environment variables file.
*   `pyproject.toml`: Project metadata and dependencies for Poetry.
*   `README.md`: This file.

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url> 
    # Replace <repository_url> with the actual URL of this repository
    ```

2.  **Navigate to the project directory**:
    ```bash
    cd <repository_name>
    # Replace <repository_name> with the directory name of the cloned repository
    ```

3.  **Install dependencies using Poetry**:
    Ensure you have Poetry installed. If not, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).
    ```bash
    poetry install
    ```

4.  **Create and configure the environment file**:
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and populate it with your actual credentials and settings.
    Key variables to set:
    *   `DATABASE_URL`: Your asynchronous PostgreSQL database connection string.
        Example: `postgresql+asyncpg://user:password@host:port/db_name`
    *   `SECRET_KEY`: A strong, unique secret key for JWT token generation. You can generate one using `openssl rand -hex 32`.
    *   `ALGORITHM`: (Optional, defaults to HS256) JWT algorithm.
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: (Optional, defaults to 30)
    *   `REFRESH_TOKEN_EXPIRE_DAYS`: (Optional, defaults to 7)

5.  **Apply database migrations**:
    Ensure your database server is running and accessible via the `DATABASE_URL` you configured.
    ```bash
    poetry run alembic upgrade head
    ```
    This command applies all pending database migrations to set up your database schema.

## Running the Application

To run the development server:
```bash
poetry run uvicorn app.main:app --reload
```
The application will typically be available at `http://127.0.0.1:8000`. The `--reload` flag enables auto-reloading when code changes are detected.

## API Documentation Access

FastAPI provides automatic interactive API documentation. Once the application is running:
*   **Swagger UI**: Access at `http://127.0.0.1:8000/docs`
*   **ReDoc**: Access at `http://127.0.0.1:8000/redoc`

These interfaces allow you to explore and interact with all available API endpoints.

## Running Tests (Placeholder)

Tests are planned and will be implemented using Pytest. Once tests are available, they can be run using:
```bash
poetry run pytest
```
**Note**: Test development is pending.

---
This README provides a comprehensive guide for developers to get started with the Logistics Delivery Management System API.
