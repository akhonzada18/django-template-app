# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.generics import get_object_or_404

# Local imports
from .forms import AddUser, UpdateUser, UserSigninForm
from .models import User, Device

# TODO: Import your project-specific models and forms here, e.g.:
# from .models import Category, Item
# from .forms import AddCategoryForm, AddItemForm


# ---------------------------------------------------------------------------
# CMS Dashboard
# ---------------------------------------------------------------------------

@login_required(login_url="/sign_in")
def dashboard_view(request):
    """
    Render the CMS home dashboard with basic statistics.
    TODO: Add your project-specific stats to the context.
    """
    total_users = User.objects.filter(deleted_at__isnull=True).count()
    total_devices = Device.objects.count()

    # 15-day device registration trend (for the chart)
    today = timezone.now().date()
    fifteen_days_ago = today - timedelta(days=14)
    device_trend_qs = (
        Device.objects.filter(created_at__date__gte=fifteen_days_ago)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    date_map = {entry["day"]: entry["count"] for entry in device_trend_qs}
    labels = [(today - timedelta(days=i)) for i in reversed(range(15))]
    chart_labels = [d.strftime("%Y-%m-%d") for d in labels]
    chart_counts = [date_map.get(d, 0) for d in labels]

    context = {
        "total_users": total_users,
        "total_devices": total_devices,
        "chart_labels": chart_labels,
        "device_counts": chart_counts,
        # TODO: Add your project-specific stats here, e.g.:
        # "total_items": Item.objects.filter(is_active=True).count(),
    }
    return render(request, "home.html", context)


# ---------------------------------------------------------------------------
# CMS Authentication
# ---------------------------------------------------------------------------

def signin_view(request):
    """Handle admin/staff sign-in."""
    if (
        request.user
        and request.user.is_authenticated
        and (request.user.is_superuser or request.user.is_staff)
    ):
        return redirect("dashboard")

    if request.method == "POST":
        form = UserSigninForm(request.POST)
        try:
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(username=username, password=password)

                if user is not None:
                    if user.deleted_at is not None:
                        messages.error(request, "Invalid user")
                        return render(request, "user/new_signin.html", {"form": UserSigninForm()})
                    login(request, user)
                    messages.success(request, "Logged in successfully")
                    if request.user.is_superuser or request.user.is_staff:
                        return redirect("dashboard")
                else:
                    print("Authentication failed for user:", username)
                    messages.error(request, "Invalid credentials")

                return render(request, "user/new_signin.html", {"form": UserSigninForm()})
            else:
                print("Signin form errors:", form.errors)
                return render(request, "user/new_signin.html", {"form": form})
        except Exception as e:
            print(str(e))
        return render(request, "user/new_signin.html", {"form": UserSigninForm()})
    else:
        return render(request, "user/new_signin.html", {"form": UserSigninForm()})


def Logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("/sign_in")


# ---------------------------------------------------------------------------
# CMS User Management
# ---------------------------------------------------------------------------

@login_required(login_url="/sign_in")
def delete_user_view(request, id):
    user = get_object_or_404(User, id=id)
    if request.user.is_authenticated and request.user.is_staff and request.user.is_superuser:
        user.deleted_at = datetime.now()
        user.save()
    return redirect("userList")


@login_required(login_url="/sign_in")
def restore_user_view(request, id):
    user = get_object_or_404(User, id=id)
    if request.user.is_authenticated and request.user.is_staff:
        user.deleted_at = None
        user.save()
        messages.success(request, "User restored successfully")
    return redirect("userList")


@login_required(login_url="/sign_in")
def user_list_view(request):
    users = User.objects.all()
    return render(request, "user/list.html", {"users": users})


@login_required(login_url="/sign_in")
def add_user_view(request):
    if (
        request.user
        and request.user.is_authenticated
        and request.user.is_staff
        and not request.user.is_superuser
    ):
        messages.error(request, "Unauthorized access (Staff cannot add a user)")
        return redirect("userList")

    if request.method == "POST":
        form = AddUser(request.POST)
        if form.is_valid():
            if request.user.is_superuser:
                role = form.cleaned_data.get("user_role")
                is_superuser = role == "superuser"
                is_staff = role in ("superuser", "staff")
                new_user = User.objects.create(
                    username=form.cleaned_data.get("username"),
                    email=form.cleaned_data.get("email"),
                    first_name=form.cleaned_data.get("first_name"),
                    last_name=form.cleaned_data.get("last_name"),
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                )
                new_user.set_password(form.cleaned_data.get("password"))
                new_user.save()
                messages.success(request, "User added successfully")
                return redirect("userList")
            messages.error(request, "Only SuperUser can add a user")
    else:
        form = AddUser()

    return render(request, "user/add_user.html", {"form": form})


@login_required(login_url="/sign_in")
def update_user_view(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        form = UpdateUser(request.POST)
        if form.is_valid():
            if not request.user.is_superuser and form.cleaned_data.get("user_role") == "superuser":
                messages.error(request, "Unauthorized access (Staff cannot assign SuperUser role)")
                return redirect("userList")

            password = form.cleaned_data.get("password")
            confirm_password = form.cleaned_data.get("confirm_password")

            if password and password != confirm_password:
                form.add_error("confirm_password", "Password and Confirm Password should match")
                return render(request, "user/update_user.html", {"form": form, "user_data": user})

            if password:
                user.set_password(password)

            role = form.cleaned_data.get("user_role")
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            if role == "staff":
                user.is_superuser = False
                user.is_staff = True
            elif role == "superuser":
                user.is_superuser = True
                user.is_staff = True
            user.save()
            messages.success(request, "User updated successfully")
            return redirect("userList")
    else:
        form = UpdateUser(instance=user)

    user_data = {k: v for k, v in user.__dict__.items() if k != "password"}
    return render(request, "user/update_user.html", {"form": form, "user_data": user_data})


# ---------------------------------------------------------------------------
# TODO: Add your project-specific CMS views below, e.g.:
# ---------------------------------------------------------------------------
#
# @login_required(login_url="/sign_in")
# def item_list_view(request):
#     items = Item.objects.filter(is_active=True).order_by("-created_at")
#     return render(request, "item/list.html", {"items": items})
#
# @login_required(login_url="/sign_in")
# def item_update_view(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     if request.method == "POST":
#         form = AddItemForm(request.POST, instance=item)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Item updated successfully")
#             return redirect("itemList")
#     else:
#         form = AddItemForm(instance=item)
#     return render(request, "item/update.html", {"form": form, "item": item})
