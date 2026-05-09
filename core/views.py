import os
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from .forms import DatasetUploadForm, LoginForm, PredictionForm, UserRegistrationForm
from .models import DatasetUpload, UserProfile


def home(request):
    return render(request, "core/home.html")


def get_dataset_path(user):
    upload = DatasetUpload.objects.filter(uploaded_by=user).order_by("-uploaded_at").first()
    if upload and upload.file:
        return upload.file.path
    sample_path = settings.BASE_DIR / "data" / "sample_thyroid.csv"
    if sample_path.exists():
        return str(sample_path)
    return None


def load_dataset(path):
    df = pd.read_csv(path)
    label_column = None
    for candidate in ["label", "target", "class", "status"]:
        if candidate in df.columns:
            label_column = candidate
            break
    if label_column is None:
        raise ValueError("CSV file must contain a 'label' or 'target' column.")

    X = df.drop(columns=[label_column])
    y = df[label_column]
    if X.select_dtypes(include="number").shape[1] != X.shape[1]:
        X = pd.get_dummies(X)
    return X, y


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


def get_prediction_model(path):
    X, y = load_dataset(path)
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model, X.columns.tolist()


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please wait for admin activation.")
            return redirect("home")
        messages.error(request, "Please fix the errors in the registration form.")
    else:
        form = UserRegistrationForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user and not user.is_active:
                messages.error(request, "Your account has not been activated by admin yet.")
                return redirect("login")
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    dataset_path = get_dataset_path(request.user)
    uploaded = DatasetUpload.objects.filter(uploaded_by=request.user).order_by("-uploaded_at").first()
    return render(request, "core/dashboard.html", {
        "uploaded": uploaded,
        "dataset_path": dataset_path,
    })


@login_required
def upload_dataset(request):
    if request.method == "POST":
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.uploaded_by = request.user
            upload.save()
            messages.success(request, "Dataset uploaded successfully.")
            return redirect("dashboard")
        messages.error(request, "Please upload a valid CSV dataset.")
    else:
        form = DatasetUploadForm()
    return render(request, "core/upload_dataset.html", {"form": form})


@login_required
def classification_view(request):
    dataset_path = get_dataset_path(request.user)
    if not dataset_path:
        messages.error(request, "No dataset is available for classification.")
        return redirect("dashboard")

    try:
        X, y = load_dataset(dataset_path)
        results = train_models(X, y)
    except Exception as exc:
        messages.error(request, f"Unable to run classification: {exc}")
        results = {}

    return render(request, "core/classification.html", {"results": results, "dataset_path": dataset_path})


@login_required
def predict_view(request):
    dataset_path = get_dataset_path(request.user)
    if not dataset_path:
        messages.error(request, "No dataset is available for prediction.")
        return redirect("dashboard")

    prediction = None
    label = None
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            try:
                model, feature_columns = get_prediction_model(dataset_path)
                features = [form.cleaned_data[f"feature{i}"] for i in range(1, 7)]
                prediction = model.predict([features])[0]
                label = "positive" if str(prediction) in ["1", "True", "positive"] else "negative"
            except Exception as exc:
                messages.error(request, f"Prediction failed: {exc}")
        else:
            messages.error(request, "Please fix the prediction form errors.")
    else:
        form = PredictionForm()

    return render(request, "core/prediction.html", {"form": form, "prediction": prediction, "label": label})


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_profiles = UserProfile.objects.filter(status="pending")
    uploads = DatasetUpload.objects.order_by("-uploaded_at")[:10]
    return render(request, "core/admin_dashboard.html", {"pending_profiles": pending_profiles, "uploads": uploads})


@user_passes_test(is_admin)
def activate_user(request, user_id):
    profile = get_object_or_404(UserProfile, pk=user_id)
    profile.status = "activated"
    profile.activated_at = datetime.now()
    profile.user.is_active = True
    profile.user.save()
    profile.save()
    messages.success(request, f"Activated user {profile.user.username}.")
    return redirect("admin_dashboard")
