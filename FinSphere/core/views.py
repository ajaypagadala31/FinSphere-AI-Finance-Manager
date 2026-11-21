import secrets, time
from functools import lru_cache
from pathlib import Path

import pandas as pd

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import redirect, render

from . import analytics, sentiment
from .models import Feedback


# ---------- cached data / model (reloaded automatically if the CSV changes) ----------
@lru_cache(maxsize=2)
def _data(mtime):
    df, info = analytics.load_dataset(settings.DATASET_PATH)
    return df, info


def get_data():
    return _data(Path(settings.DATASET_PATH).stat().st_mtime)


@lru_cache(maxsize=2)
def _forecaster(mtime):
    return analytics.build_forecaster(_data(mtime)[0])


def get_forecaster():
    return _forecaster(Path(settings.DATASET_PATH).stat().st_mtime)


# ---------- public pages & auth ----------
def index(request):
    return render(request, "core/index.html", {"scene": "hero"})


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        e = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=e).exists():
            raise forms.ValidationError("This e-mail is already registered.")
        return e


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created. Please sign in.")
        return redirect("login")
    return render(request, "core/auth.html", {"form": form, "title": "Create account", "btn": "Sign up", "scene": "app"})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        code = f"{secrets.randbelow(10 ** 6):06d}"
        request.session["otp"] = {"uid": user.pk, "hash": make_password(code), "exp": time.time() + 300, "tries": 0}
        send_mail("Your FinSphere sign-in code", f"Your one-time code is {code}. It expires in 5 minutes.",
                  None, [user.email or "unknown@example.com"])
        return redirect("verify")
    return render(request, "core/auth.html", {"form": form, "title": "Sign in", "btn": "Send OTP", "scene": "app"})


def verify_otp(request):
    data = request.session.get("otp")
    if not data:
        return redirect("login")
    if request.method == "POST":
        data["tries"] += 1
        request.session["otp"] = data
        if time.time() > data["exp"] or data["tries"] > 5:
            del request.session["otp"]
            messages.error(request, "Code expired or too many attempts. Sign in again.")
            return redirect("login")
        if check_password(request.POST.get("code", "").strip(), data["hash"]):
            user = User.objects.get(pk=data["uid"])
            del request.session["otp"]
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("dashboard")
        messages.error(request, "Incorrect code.")
    dev = settings.EMAIL_BACKEND.endswith("console.EmailBackend")
    return render(request, "core/verify.html", {"dev": dev, "scene": "app"})


def logout_view(request):
    logout(request)
    return redirect("index")


# ---------- app modules ----------
@login_required
def dashboard(request):
    _, info = get_data()
    return render(request, "core/dashboard.html", {"info": info, "scene": "app"})


@login_required
def dataset(request):
    df, info = get_data()
    cats = analytics.category_table(df).to_dict("records")
    preview = df.sort_values("date_time").tail(10).assign(date_time=lambda d: d.date_time.dt.strftime("%Y-%m-%d"))
    return render(request, "core/dataset.html", {"info": info, "cats": cats, "scene": "app",
                                                 "preview": preview.to_dict("records")})


@login_required
def clusters(request):
    df, _ = get_data()
    data = analytics.cluster_categories(df)
    return render(request, "core/clusters.html", {"data": data, "scene": "app"})


@login_required
def forecast(request):
    fc = get_forecaster()
    target = fc["months"][-1] + pd.DateOffset(months=6)          # chart shows history + a 6-month outlook
    res = analytics.forecast_month(fc, target.year, target.month)
    return render(request, "core/forecast.html", {"res": res, "m": res["metrics"], "scene": "app"})


@login_required
def budget(request):
    fc = get_forecaster()
    nxt = fc["months"][-1] + pd.DateOffset(months=1)
    ctx = {"scene": "app", "min_month": f"{fc['months'][0]:%Y-%m}", "default_month": f"{nxt:%Y-%m}"}
    if request.method == "POST":
        try:
            y, m = map(int, request.POST["month"].split("-"))
            income = float(request.POST["income"])
            if income <= 0:
                raise ValueError("Income must be positive.")
            res = analytics.forecast_month(fc, y, m)
            ctx.update(res=res, rec=analytics.recommend(income, res["value"]), income=income, sel=request.POST["month"])
        except (ValueError, KeyError) as e:
            messages.error(request, str(e) or "Invalid input.")
    return render(request, "core/budget.html", ctx)


@login_required
def feedback(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()[:500]
        if text:
            label, score = sentiment.analyze(text)
            Feedback.objects.create(user=request.user, text=text, sentiment=label, score=score)
            messages.success(request, f"Feedback received - detected sentiment: {label}")
            return redirect("feedback")
    stats = {r["sentiment"]: r["n"] for r in Feedback.objects.values("sentiment").annotate(n=Count("id"))}
    return render(request, "core/feedback.html", {"mine": Feedback.objects.filter(user=request.user)[:8],
                                                  "stats": stats, "scene": "app"})
