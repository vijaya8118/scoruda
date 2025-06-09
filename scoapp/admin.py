from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Purchase_model)
admin.site.register(PurchaseBook)
admin.site.register(Invoice_model)
admin.site.register(CashBook)
admin.site.register(Add_item_model)
admin.site.register(Members)

class TenantAdminSite(admin.AdminSite):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.register(Client)
        self.register(Domain)

tenant_admin_site = TenantAdminSite(name = "tenant_admin_site")