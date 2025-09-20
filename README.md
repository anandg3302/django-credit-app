# Django Credit App

A backend application built with Django and Django REST Framework to manage customer registrations, loan eligibility checks, and loan applications. The project is fully Dockerized for easy setup and deployment.

---

## Features

- Customer Registration:Register new customers with automatic calculation of approved loan limits.
- Loan Eligibility Check:Evaluate loan eligibility based on credit score, income, and loan parameters.
- Loan Application:Process loan applications with approval or rejection logic.
- REST API:Clean and well-structured API endpoints for all operations.
- Dockerized:Multi-container setup with Django, PostgreSQL, and Redis using Docker Compose.
- Environment Config:Secure management of secrets and service URLs via `.env` file.

---

## Technologies Used

- Python 3.13  
- Django 5.2  
- Django REST Framework  
- PostgreSQL  
- Redis (optional caching)  
- Docker & Docker Compose  
- python-decouple & dj-database-url for environment management

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running  
- Optional: [Postman](https://www.postman.com/) or curl for API testing

### Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/anandg3302/django-credit-app.git
   cd django-credit-app
