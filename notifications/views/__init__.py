from .actions import *
from .base import *
from .cycle import *
from emailtemplate import *

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'You have been logged out.')
    return redirect('notifications:dashboard')

