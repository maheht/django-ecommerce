
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import RegistrationForm
from .serializers import RegistrationSerializer

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken


# HTML Registration View


def register_view(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            # Log out any previously authenticated user
            logout(request)

            messages.success(
                request,
                "Registration successful! Please login."
            )

            return redirect("login")

    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )




# HTML Login View
def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=phone,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "You logged in successfully!"
            )

            return redirect("home")

        messages.error(
            request,
            "Invalid phone number or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


# HTML Logout View
def logout_view(request):

    if request.method == "POST":

        logout(request)

        messages.success(
            request,
            "You logged out successfully."
        )

    return redirect("home")


# JWT Registration API
class RegistrationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegistrationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Registration successful!",
                    "user": {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone": user.profile.phone,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
