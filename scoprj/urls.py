"""
URL configuration for scoprj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""
URL configuration for scoprj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from scoapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('create_company',views.createCompany,name ='create_company'),
    path('emailsent',views.emailsent,name ='emailsent'),

    path('setupcompany',views.setupCompany,name ='setupcompany'),
    path('setup',views.create_member,name ='setup'),
    path('profile',views.profile,name ='profile'),
    path('kyc',views.kyc,name ='kyc'),
    path('',views.landing,name =''),

#############
    path('additem',views.Add_item,name='additem'),
    path('seller',views.seller,name='seller'),
    path('customer',views.customer,name='customer'),
    path('cashbook',views.cashbook,name='cashbook'),
    path('purchasebook',views.purchasebook,name='purchasebook'),

# ####delete
    path('item_delete/<str:pk>/',views.item_delete,name='item_delete'),
    path('seller_delete/<str:pk>/',views.seller_delete,name='seller_delete'),
    path('customer_delete/<str:pk>/',views.customer_delete,name='customer_delete'),
    path('cashbook_delete/<str:pk>/',views.cashbook_delete,name='cashbook_delete'),
    path('purchasebook_delete/<str:pk>/',views.purchasebook_delete,name='purchasebook_delete'),
    path('purchase_delete/<str:pk>/',views.purchase_delete,name='purchase_delete'),
    path('bill_delete/<str:pk>/',views.bill_delete,name='bill_delete'),

# ####edits
    path('item_edit/<str:pk>/',views.item_edit,name='item_edit'),
    path('seller_edit/<str:pk>/',views.seller_edit,name='seller_edit'),
    path('customer_edit/<str:pk>/',views.customer_edit,name='customer_edit'),
    path('cashbook_edit/<str:pk>/',views.cashbook_edit,name='cashbook_edit'),
    path('purchasebook_edit/<str:pk>/',views.purchasebook_edit,name='purchasebook_edit'),
    path('purchase_edit/<str:pk>/',views.purchase_edit,name='purchase_edit'),
    path('bill_edit/<str:pk>/',views.bill_edit,name='bill_edit'),
    # path('price_edit/<str:pk>/',views.price_edit,name='price_edit'),
    path('company_edit/<str:pk>/',views.setupCompany_edit,name='company_edit'),
                                                                 
# ##view
    path('item',views.item_display,name='item'),
    path('customerall',views.customer_display,name='customerall'),
    path('sellerall',views.seller_display,name='sellerall'),

# ##Bills and purchase
    path('b2c',views.sale,name='b2c'),####Auto
    path('t', views.process_sale, name='t'),

#     path('b2b',views.b2b, name='b2b'),
#     path('t1', views.process_b2b, name='t1'),

#     path('p', views.purchaseauto_process, name='p'),####Auto
#     path('purchaseprod',views.purchase_auto,name='purchaseprod'),

    path('retailpurch',views.purchase,name='retailpurch'),
    path('r1',views.process_purchase,name='r1'),
    

# ##overviews
    path('show',views.scout,name='show'),
    path('cshbal',views.cash_balance,name='cshbal'),
    path('invoice',views.invoiceDisplay,name='invoice'),
    path('stock',views.Stock,name='stock'),
    path('search',views.search,name='search'),
#     path('productAnalysis',views.productAnalysis,name='productAnalysis'),
#     path('invoice1',views.invoice1,name='invoice1'),
#     path('prodlist',views.product_list,name='prodlist'),

# ##filters
    # path('dateie/<str:pk>/',views.dateie,name ='dateie'),
    # path('purchdateie/<str:pk>/',views.purchdateie,name ='purchdateie'),
    path('prod/<str:pk>/',views.prod,name ='prod'),
    path('purchprod/<str:pk>/',views.prod_purch,name ='purchprod'),
    path('seller_shop/<str:pk>/',views.seller,name='seller_shop'),
    path('purchseller_shop/<str:pk>/',views.seller_purch,name='purchseller_shop'),
    path('modepurch/<str:pk>/',views.mode_purch,name='modepurch'),
    path('mode/<str:pk>/',views.mode,name='mode'),
    # path('date_wise/<str:pk>/<str:factor>/',views.date_by_query,name='date_wise'),

# ##User Authentication
    path('login',views.loginPage,name='login'),
    path('signout',views.signout,name='signout'),
#     # path('',views.frontPage,name=''),
#     path('cr/<str:pk>',views.credit,name='cr'),
#     path('cr1/<str:pk>/',views.credit1,name='cr1'),

# #####
#     path('send_to_serial', views.serial_data, name='send_to_serial'),
#     path('index',views.index,name='index'),
    path('dashboard',views.dashboard_today,name='dashboard'),
# ####
#     path('download_pdf/', views.download_pdf, name='download_pdf'),
# #####
#     path('upload_items/', views.upload_items, name='upload_items'),
#     path('upload_customer/', views.upload_customer, name='upload_customer'),
#     path('upload_seller/', views.upload_seller, name='upload_seller'),
#     path('upload_purchasebook/', views.upload_purchasebook, name='upload_purchasebook'),
#     path('upload_cashebook/', views.upload_cashebook, name='upload_cashebook'),
#     path('upload_invoice/', views.upload_invoice, name='upload_invoice'),
#     path('upload_purchase/', views.upload_purchase, name='upload_purchase'),


]



