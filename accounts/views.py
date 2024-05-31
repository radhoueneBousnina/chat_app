import sys

from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm
from django.contrib import messages

import logging

logger = logging.getLogger(__name__)


def is_running_tests():
    return 'test' in sys.argv


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.username = user.email  # we use email as username
                user.set_password(form.cleaned_data['password'])
                user.save()

                # we log in after user creation
                user = authenticate(username=user.email, password=form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    logger.info(f"User {user.email} registered and logged in successfully.")
                    return redirect('chat:index')
            except IntegrityError:
                form.add_error('email', 'A user with that email already exists.')
                if not is_running_tests():
                    logger.error("IntegrityError: A user with that email already exists.")
            except Exception as e:
                form.add_error(None, 'An unexpected error occurred. Please try again later.')
                if not is_running_tests():
                    logger.error(f"Unexpected error: {e}")

    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        try:
            if form.is_valid():
                email = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
                    logger.info(f"User {email}  logged in successfully.")

                    return redirect('chat:index')
            else:

                if any('This field is required.' in errors for errors in form.errors.values()):
                    messages.error(request, 'This field is required.')
                    if not is_running_tests():
                        logger.error("This field is required.")
                else:
                    messages.error(request, 'Invalid email or password.')
                    if not is_running_tests():
                        logger.error("Invalid email or password.")

        except Exception as e:
            form.add_error(None, 'An unexpected error occurred. Please try again later.')
            if not is_running_tests():
                logger.error(f"Unexpected error: {e}")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

