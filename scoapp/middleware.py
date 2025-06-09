from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .models import *

class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        domain = request.get_host().split(":")[0]  # Extract domain without port
        try:
            tenant = Client.objects.get(domain=domain)
            request.tenant = tenant
        except Client.DoesNotExist:
            request.tenant = None


from django.http import HttpResponseForbidden

class GroupBasedNavbarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure the user is authenticated before checking groups
        if request.user.is_authenticated:
            user_groups = request.user.groups.all()

            # Check if user belongs to specific groups
            if request.user.groups.filter(name='admin').exists():
                request.user.navbar_group = 'admin'
            elif request.user.groups.filter(name='manager').exists():
                request.user.navbar_group = 'manager'
            elif request.user.groups.filter(name='employee').exists():
                request.user.navbar_group = 'employee'
            else:
                request.user.navbar_group = 'guest'
        else:
            request.user.navbar_group = 'guest'

        # Continue processing the request
        response = self.get_response(request)
        return response