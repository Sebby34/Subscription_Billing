# Subscription Billing System

A simple Flask-based API for managing users, subscription plans, payments, and invoices. Built with SQLAlchemy and organized using Flask Blueprints.

---

## Features

- Manage users, plans, and subscriptions
- Record payments and generate invoices
- Modular API structure with Flask Blueprints
- Simple caching for faster responses

---

## Tech Stack

- Flask (Python)
- MySQL with SQLAlchemy ORM
- Flask-Caching (SimpleCache)

---

## Setup

1. Clone the repository:

git clone git@github.com:Sebby34/Subscription_Billing.git
cd Subscription_Billing

2. Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

3. Set the database URL in `.env`:

DATABASE_URL=mysql+mysqlconnector://root:<your-password>@localhost/subscription_billing

4. Run the app:

python main.py

---

## Project Structure

app/
  blueprints/
  models.py
  extensions.py
  __init__.py
config.py
main.py
requirements.txt