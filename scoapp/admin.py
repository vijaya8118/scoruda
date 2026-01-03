from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Invoice_model)
admin.site.register(Purchase_model)
admin.site.register(Transportation)
admin.site.register(PurchaseBook)
admin.site.register(CashBook)