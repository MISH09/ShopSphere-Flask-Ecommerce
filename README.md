# ShopSphere — Flask E-commerce Demo

A ready-to-run online store demo built with Python, Flask, Jinja templates, HTML, CSS, JavaScript, and SQLite.

## Features
- Responsive storefront and product cards
- Search, category filtering, and sorting
- Product detail pages
- Session-based shopping cart with quantity updates and item removal
- Registration and login with hashed passwords
- Demo checkout that records orders in SQLite (no real payment processing)
- Logged-in order history
- About and contact pages

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this folder and open it in VS Code.
3. In the project folder, run `run_windows.bat`, or use PowerShell:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000 in your browser.

The SQLite database is created automatically the first time the app runs.

## Notes
- This is a learning/demo project. Checkout records an order but does not charge a payment method.
- Before deployment, set a strong secret key using an environment variable, disable debug mode, add CSRF protection and production-grade configuration, and validate any payment integration.
- Product images are illustrated with emoji-style product tiles to keep the project self-contained and runnable offline.

- CI/CD automatic deployment test 2
- CI?CD TESTING 3
