# Thyroid Disease Prediction Prototype

This Django project is a prototype for thyroid disease classification and prediction based on the design documents you provided.

## Features

- User registration with admin activation
- Secure login and logout
- Dataset upload in CSV format
- Classification score summary using SVM, KNN, Logistic Regression, and Neural Network
- Prediction form
- Admin dashboard for activating users

## Local setup

```bash
cd /Users/harsheethkurelli/Downloads/DOCUMENTS/thyroid_project
source venv/bin/activate
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

## Notes

- The prototype uses SQLite for the database.
- Dataset upload expects a CSV file with six numeric feature columns and a binary `label` column.
- If no dataset is uploaded, a sample dataset is available in `data/sample_thyroid.csv`.
