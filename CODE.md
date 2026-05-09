# Thyroid Prediction Project Code Overview

This repository implements a Django prototype for thyroid disease classification and prediction.

## Key files

- `core/views.py` - main application logic for registration, login, dataset upload, classification, and prediction.
- `core/forms.py` - forms for user registration, login, dataset upload, and prediction inputs.
- `core/models.py` - user profile and dataset upload models.
- `core/urls.py` - application URL routes.
- `thyroid_project/settings.py` - Django settings including database, static and media configuration.
- `thyroid_project/urls.py` - root URL patterns.
- `data/sample_thyroid.csv` - sample data used by the app when no user upload exists.

## Core application logic sample

```python
# core/views.py

def get_dataset_path(user):
    upload = DatasetUpload.objects.filter(uploaded_by=user).order_by("-uploaded_at").first()
    if upload and upload.file:
        return upload.file.path
    sample_path = settings.BASE_DIR / "data" / "sample_thyroid.csv"
    if sample_path.exists():
        return str(sample_path)
    return None


def train_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    models = {
        "Support Vector Machine": SVC(kernel="linear", probability=True, max_iter=10000),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=1000),
    }
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        results[name] = round(score * 100, 2)
    return results
```

## Notes

- The project is committed locally in Git under `thyroid_project/`.
- There is currently no GitHub remote configured in this local repository.
- A public website URL is not available until the app is deployed to a hosting service.
