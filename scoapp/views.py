from.models import *
from .forms import *
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.management import call_command
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.shortcuts import render,redirect,reverse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from collections import defaultdict
import calendar 
from django.http import HttpResponse
from django.template.loader import render_to_string
from tenant_schemas.utils import schema_context, get_tenant_model
from django.db import IntegrityError
from django.contrib.auth import get_user_model



## User defines functions
def mode_total(model,model1,need_query ):
    # ## Invoice_model
        upi_query=model.objects.all().filter(mode = 'UPI')
        cash_query=model.objects.all().filter(mode = 'cash')
        credit_query=model1.objects.all().filter(mode = 'credit')

        cashdict = cash_query.aggregate(Sum('amt')) 
        cash = cashdict['amt__sum'] or 0

        upiquery = upi_query.aggregate(Sum('amt')) 
        upi = upiquery['amt__sum'] or 0
        
        total_transaction_query = model1.objects.all() 
        total_dict = total_transaction_query.aggregate(Sum('amt')) 
        total_transaction = total_dict['amt__sum'] or 0

        cash_upi = Decimal(cash or 0) + Decimal(upi or 0)
        credit = Decimal(total_transaction or 0) - Decimal(cash_upi or 0)
        if need_query == False:
            return cash,upi,credit
        else :
            return cash,upi,credit,upi_query,cash_query,credit_query


        # query=model.objects.all().filter(mode = mode_type)
        # dict = query.aggregate(Sum('amt')) 
        # val = dict['amt__sum'] or 0
        # return val

def invoice(request, chk):
    latest_invoices = Invoice_model.objects.filter(billnum=chk)

    products = []
    invoice_num = invoice_to = created = payment = ""

    # Defaults for company and outward data
    company_name = company_address = company_phone = company_acc = company_bank = company_gst = company_ifsc = ""
    outward_name = outward_address = outward_phone = outward_acc = outward_bank = outward_gst = outward_ifsc = ""

    # Get company details
    mycompany = SetupCompany.objects.all()
    if mycompany.exists():
        company = mycompany.first()
        company_name = company.name
        company_address = company.address
        company_phone = company.phone
        company_acc = company.account
        company_bank = company.bank
        company_gst = company.gst
        company_ifsc = company.ifsc

    # If invoice found
    if latest_invoices.exists():
        first_invoice = latest_invoices[0]
        invoice_num = first_invoice.billnum
        invoice_to = first_invoice.selbuy
        created = first_invoice.date1
        payment = first_invoice.mode

        # Get outward party details
        outward = Customer.objects.filter(name=invoice_to)
        if outward.exists():
            party = outward.first()
            outward_name = party.name
            outward_address = party.address
            outward_phone = party.phone
            outward_acc = party.account
            outward_bank = party.bank
            outward_gst = party.gst
            outward_ifsc = party.ifsc

        # Products list
        for qs in latest_invoices:
            products.append({
                'commodity': qs.product,
                'quantity': qs.qty,
                'price': qs.rate,
                'current_price': qs.amt,
                'gst': qs.gst,
            })

    # Prepare context
    context = {
        'products': products,
        'invoice_num': invoice_num,
        'invoice_to': invoice_to,
        'created': created,
        'payment': payment,
        'company': {
            'name': company_name,
            'address': company_address,
            'phone': company_phone,
            'account': company_acc,
            'bank': company_bank,
            'gst': company_gst,
            'ifsc': company_ifsc,
        },
        'outward': {
            'name': outward_name,
            'address': outward_address,
            'phone': outward_phone,
            'account': outward_acc,
            'bank': outward_bank,
            'gst': outward_gst,
            'ifsc': outward_ifsc,
        }
    }

    return render(request, 'invoice_display.html', context)

def collect_values(request,pk,model,compare_field,field_to_access):    
        name = "no Entry"
        query = model.objects.filter(**{compare_field: pk}).order_by('-date')
        for q in query:
            name = getattr(q, field_to_access)
        if hasattr(model, 'qty'):
            qtytot = query.aggregate(Sum('qty')) 
            qty_total = qtytot['qty__sum']
        else:
            qty_total = '-'
        amttot = query.aggregate(Sum('amt'))  # total_amount is the key for the aggregate result
        amt_total = amttot['amt__sum']
        paginator = Paginator(query, 10)
        page_number = request.GET.get("page")
        pages = paginator.get_page(page_number)
        return amt_total,qty_total,name,pages



def formFunction(request,heading,formvar,redirectpage,context_data):
    form = formvar(request.POST or None, request.FILES or None)
    theuser = request.user
    print(theuser)
    if request.method == 'POST':
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = theuser
            obj.save()
            return redirect(redirectpage)
    return render(request, 'formjust.html', context={'form': form, 'heading': heading,**context_data})

def display(request, modelvar, var):
    query = modelvar.objects.all().order_by(var)
    paginator = Paginator(query, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj

def edit_view_decorator(Modelvar, redirect_view, Formvar, use_edit_view=True):
    def edit_using_num(request, pk):
        obj = get_object_or_404(Modelvar, num=pk)
        if request.method == 'POST':
            form = Formvar(request.POST, request.FILES, instance=obj)
        else:
            form = Formvar(instance=obj)
        
        if form.is_valid():
            form.save()
            return redirect(redirect_view)
        
        return render(request, "formjust.html", context={'form': form, 'shopnav': True})

    def edit_using_id(request, pk):
        obj = get_object_or_404(Modelvar, id=pk)
        if request.method == 'POST':
            form = Formvar(request.POST, request.FILES, instance=obj)
        else:
            form = Formvar(instance=obj)        
        if form.is_valid():
            form.save()
            return redirect(redirect_view)
        
        return render(request, "formjust.html", context={'form': form, 'shopnav': True})

    if use_edit_view==True:
        return edit_using_num
    else:
        return edit_using_id
    
def delete_view_decorator(Modelvar, redirect_view, use_delete_view=True):
    def delete_using_num(request, pk):
        instance = get_object_or_404(Modelvar, num=pk)
        if request.method == 'POST':
            instance.delete()
            return redirect(redirect_view)
        return render(request, "delete.html", context={})

    def delete_using_id(request, pk):
        instance = get_object_or_404(Modelvar, id=pk)
        if request.method == 'POST':
            instance.delete()
            return redirect(redirect_view)
        return render(request, "delete.html", context={})

    if use_delete_view:
        return delete_using_num
    else:
        return delete_using_id
    
def total_quantity(modelname,prod):
    qs=modelname.objects.filter(product_id=prod)
    dict_total_quantity= qs.aggregate(Sum('qty'))
    total_quantity=dict_total_quantity['qty__sum']
    if total_quantity==None:
        total_quantity=0
    tot =float(total_quantity)
    return tot

##################### REGISTRATION AND LOGIN ####################
def landing(request):
    return render(request,'landing.html',context={})

def createCompany(request):
    form = TenantForm()  # Default form for GET requests
    print('Before POST')
    heading = "Create Subdomain for your Company"

    if request.method == "POST":
        print('After POST')
        tenant_form = TenantForm(request.POST)
        print('Before Valid')

        if tenant_form.is_valid():
            print('After Valid')
            tenant = tenant_form.save()

            # ✅ First, create the schema for the tenant
            tenant.create_schema(check_if_exists=True)  # Make sure the schema is created
            print(f"Schema for {tenant.schema_name} created.")

            # ✅ Now run migrations for the newly created schema
            from django.core.management import call_command
            call_command('migrate_schemas', schema_name=tenant.schema_name)
            print('Migrations applied to schema.')

            print('Tenant Saved')

            try:
                # Create the domain associated with the tenant
                domain = Domain.objects.create(
                    tenant=tenant,
                    domain=f"{tenant.schema_name}.{settings.BASE_URL}",
                    is_primary=True
                )
                print('Domain Created')
                print(f"Created domain: http://{domain.domain}:8000/setup")

                # Prepare and send the email notification
                tenant_email = tenant.email
                print(f"Created email: {tenant_email}")
                print('Preparing email')

                email = EmailMessage(
                    'Domain name from Scoruda',  # Subject of the email
                    f"Domain has been created successfully for your company. Please use the given domain name for login: https://{domain}/setupcompany",  # Body
                    to=[tenant_email]
                )
                print('Email launching....')
                email.send()
                print('Email Launched')

            except IntegrityError as e:
                print(f"Error with domain creation: {e}")
                return render(request, 'form.html', context={'form': tenant_form, 'error': 'Domain creation failed due to a conflict or issue'})

            return redirect('emailsent')  # Change to actual URL name if necessary
        else:
            print('Form is not valid')
            print(f'Errors: {tenant_form.errors}')
    
    return render(request, 'formjust.html', context={'form': tenant_form if request.method == 'POST' else form,'heading':heading,})


def emailsent(request):
    return render(request,'emailsent.html',context={})

def create_member(request):
    heading = "Create a account"
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            # Save the form and create the new user
            new_member = form.save()
            role = form.cleaned_data.get('role')  
            if role == 'Admin':
                group = Group.objects.get(name='Admin')
            elif role == 'Manage':
                group = Group.objects.get(name='Manage')
            elif role == 'Employee':
                group = Group.objects.get(name='Employee')
            else:
                group = Group.objects.get(name='Employee')  
            new_member.groups.add(group)
            login(request, new_member)#auto login

            messages.success(request, f"Member {role} created successfully!")
            return redirect('profile')  
        else:
            messages.error(request, "There was an error creating the member.")
    else:
        form = MemberForm()
    return render(request, 'formjust.html', {'form': form,'heading':heading})

def loginPage(request):
    if request.user.is_authenticated:
            return redirect('show')
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username = username,password = password)
        if user is not None:
            login(request,user)
            # request.session.set_expiry(1209600)
            User = get_user_model()
            is_anonymous = request.user.is_anonymous

            print('An',is_anonymous)
            print(user.is_active)
            print("username", username)
            print('Groups:', [group.name for group in user.groups.all()])  # prints list of group names

            return redirect('show')
        else:
            messages.info(request,'User or Password is incorrect')
    return render(request,'login.html',context={})

def signout(request):
    logout(request)
    return redirect('')

@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user,})

def setupCompany(request):
  heading = "Please complete your company profile to continue."
  context_data = {}
  return formFunction(request,heading,SetupCompany_form,redirectpage='kyc',context_data=context_data)


def kyc(request):
    # Fetch all users from the Members model
    users = Members.objects.all()  # Retrieve all users from the database
    company_query = SetupCompany.objects.all()

    return render(request, 'kyc.html', {'users': users,'company_query':company_query,})

from datetime import datetime, timedelta

############ DATA ENTRY #################

def Add_item(request):
    heading = "Add Product"
    context_data = {}
    return formFunction(request,heading,Add_item_form,redirectpage='additem',context_data=context_data)


def setupCompany(request):
  heading = "Please complete your company profile to continue."
  context_data = {}
  return formFunction(request,heading,SetupCompany_form,redirectpage='kyc',context_data=context_data)


def seller(request):
  heading = "Add Seller"
  context_data = {}
  return formFunction(request,heading,Seller_form,redirectpage='seller',context_data=context_data)

def cashbook(request):
  heading = "Cash Receipt"
  context_data = {}
  return formFunction(request,heading,CashReceipt_form,redirectpage='cashbook',context_data=context_data)

def purchasebook(request):
  heading = "Purchase Receipt"
  context_data = {}
  return formFunction(request,heading,PurchaseBookForm,redirectpage='purchasebook',context_data=context_data)

def customer(request):
  heading = "Add Customer"
  context_data = {}
  return formFunction(request,heading,Customer_form,redirectpage='customer',context_data=context_data)

############ EDIT AND DELETE #################
item_delete = delete_view_decorator(Add_item_model, 'item',use_delete_view=False)
customer_delete = delete_view_decorator(Customer, 'customerall',use_delete_view=False)
seller_delete = delete_view_decorator(Seller, 'sellerall',use_delete_view=False)
cashbook_delete = delete_view_decorator(CashBook, 'show',use_delete_view=False)
purchasebook_delete = delete_view_decorator(PurchaseBook, 'show',use_delete_view=False)
bill_delete = delete_view_decorator(Invoice_model, 'show',use_delete_view=True)
purchase_delete = delete_view_decorator(Purchase_model, 'show',use_delete_view=True)

item_edit = edit_view_decorator(Add_item_model, 'item',Add_item_form, use_edit_view=False)
seller_edit = edit_view_decorator(Seller, 'sellerall',Seller_form, use_edit_view=False)
customer_edit = edit_view_decorator(Customer, 'customerall',Customer_form, use_edit_view=False)
cashbook_edit = edit_view_decorator(CashBook, 'show',CashReceipt_form, use_edit_view=False)
purchasebook_edit = edit_view_decorator(PurchaseBook, 'show',PurchaseBookForm, use_edit_view=False)
bill_edit = edit_view_decorator(Invoice_model, 'show',InvoiceSecond_form, use_edit_view=True)
purchase_edit = edit_view_decorator(Purchase_model, 'show',Purchase_form, use_edit_view=True)
setupCompany_edit = edit_view_decorator(SetupCompany, 'setup',SetupCompany_form, use_edit_view=False)

############ DISPLAY #################
def item_display(request):
    heading="Product List"
    query = display(request, Add_item_model, 'id')
    return render(request,'view.html',context={'query':query,'heading':heading})

def product_list(request):
    heading="Product List"
    query = display(request, Add_item_model, 'id')
    return render(request,'product_list.html',context={'query':query,'heading':heading})

def seller_display(request):
    heading="Seller List"
    query = display(request, Seller, 'name')
    return render(request,'view.html',context={'query':query,'heading':heading})

def customer_display(request):
    heading="Customer List"
    query = display(request, Customer, 'name')
    return render(request,'view.html',context={'query':query,'heading':heading})

#################### PURCHASES AND SALES ###############################
def process(request,Tansaction_model,CustSel,Book_model,redirectpage):
    print("enter view")
    if request.method == 'POST':
        print('POST request received')
        try:
            print('Entering POST try block')
            selected_products = json.loads(request.body.decode('utf-8'))
            print(selected_products)
            if not isinstance(selected_products, list):
                raise ValueError("Expected a list of products, got something else.")
            total_amount = 0
            if not selected_products:
                print("No products received in the order.")
            try:
                latest_invoice = Tansaction_model.objects.latest('date')
                bill_number = latest_invoice.billnum + 1
            except Tansaction_model.DoesNotExist:
                # If no invoices exist, set the initial bill number to 1
                bill_number = 1
            print('Bill number:', bill_number)
            for product in selected_products:  
                if not isinstance(product, dict):
                    print(f"Skipping invalid product: {product}")
                    continue
                product_id = product.get('productId')
                payment_mode = product.get('mode')  
                quantity = product.get('qty', 1) 
                seller_buyer_id = product.get('customer')  
            
                seller_buyer = CustSel.objects.get(id=seller_buyer_id)
                print('Mode:', payment_mode)                              
                print('Quantity:', quantity)  
                print("Seller/Buyer:", seller_buyer)
                from_company = SetupCompany.objects.all()
                for f in from_company:
                    gstperc = f.gsttype
                if not product_id:
                    print("Missing product ID, skipping this product.")
                    continue
                product_list = Add_item_model.objects.filter(id=product_id)
                if not product_list.exists():
                    print(f"Product with ID {product_id} not found.")
                    continue
                for p in product_list:
                    ratee = p.rate  # Product rate
                    print('Product rate:', ratee)
                    try:
                        amount_before_gst = float(quantity) * float(ratee)  
                        gst_amt = float(amount_before_gst) * float(gstperc)/100
                        amount = float(gst_amt) + float(amount_before_gst)
                        print('Amount:', amount)
                    except Exception as e:
                        print(f"Error calculating amount: {e}")
                        continue
                
                    new_invoice = Tansaction_model(
                        product_id=product_id,
                        qty=quantity,
                        rate = ratee,
                        gst = gst_amt,
                        amt=amount,
                        billnum=bill_number,  # Ensure all products have the same billnum
                        mode=payment_mode,
                        selbuy=seller_buyer,  # Now passing the actual Customer instance
                        user = request.user
                    )
                    new_invoice.save()
                    print(f" Data saved: {new_invoice}")
                    total_amount += amount

                    print('1')
                    if payment_mode in ['cash', 'UPI']:
                        try:
                            print('2')
                            cash_book_entry = Book_model(
                                user = request.user,
                                selbuy=seller_buyer,  # Link to the customer
                                amt=amount,  # Amount paid
                                mode=payment_mode,  # Payment mode (cash/UPI)
                                comment=f"Payment for Invoice {bill_number}"  # Optional comment
                            )
                            print('3')
                            cash_book_entry.save()
                            print('4')
                            print(f"CashBook entry saved: {cash_book_entry}")
                        except Exception as e:
                            print(f"Error saving CashBook entry: {e}")
            
            return redirect(redirectpage)
        except Exception as e:
            print(f"Error processing order: {e}")
    return render(request, 'sale.html', context={})


def sale(request):
    head = "Bill"
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='')  
    form = InvoiceSecond_form(request.POST or None)
    print(items)
    return render(request, 'sale.html', context={'items': items, 'head': head, 'form': form})

@require_POST
@csrf_exempt
def process_sale(request):
    query = process(request, Invoice_model,Customer,CashBook, 'invoice')
    return render(request,'sale.html',context={'query':query})

def purchase(request):
    head = "Purchase"
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='')  
    form = Purchase_form2(request.POST or None)
    print(items)
    return render(request, 'purchase.html', context={'items': items, 'head': head, 'form': form})


@require_POST
@csrf_exempt
def process_purchase(request):
    query = process(request, Purchase_model,Seller,PurchaseBook, 'invoice')
    return render(request,'purchase.html',context={'query':query})

###################### DASHBOARD AND SUMMARY ################################

def scout(request):
        head = "SCOUT"
        purch_query=display(request,Purchase_model,'-date')
        bill_query = display(request,Invoice_model,'-date')
            
        context={
            'purch_query':purch_query,'bill_query':bill_query,'head':head,
        }
        return render(request,'scout.html',context)

def invoiceDisplay(request):
    # Fetch the latest invoice and related products
    query = Invoice_model.objects.all().latest('date')
    billnumber = query.billnum
    response = invoice(request,billnumber)
    return response

def Stock(request):
    head = "Stock"
    products = Add_item_model.objects.all()
    d = {}
    d1 = {}
    d2 = {}

    for p in products:
        prod = p.id
        prod_name = p.product
        purchased = total_quantity(Purchase_model, prod)
        d[prod_name] = purchased

        sold = total_quantity(Invoice_model, prod)
        d1[prod_name] = sold

        bal = purchased - sold
        d2[prod_name] = bal
    return render(request,'stock.html',context={'d':d,'d1':d1,'d2':d2,'head':head,'products':products,'product':True,})

def cash_balance(request):
        head = "CASH BALANCE"
        g ={}
        d={}
        d1={}
        d2={}


        cash_sold ,upi_sold,credit_sold = mode_total(CashBook,Invoice_model,need_query = False)
        cash_purch ,upi_purch,credit_purch = mode_total(PurchaseBook,Purchase_model,need_query = False)

        d1 = {
        "Cash": cash_sold,  
        "UPI":upi_sold,
        "Credit":credit_sold,
        }

        d = {
        "Cash": cash_purch,  
        "UPI":upi_purch,
        "Credit":credit_purch,
        }
    
        d2 = {key: d1[key] - d.get(key, 0)
                                for key in d1.keys()}

        context={
                "d":d,
                "d1":d1,
                "d2":d2,
                'mode':True,
                'head':head,
                'product':False,
               
        }
        return render(request,'stock.html',context)

def search(request):
    heading = "Choses any one field to Search data"
    context_data = {'shopnav': True}
    form = SearchForm
    if request.method=='POST':
        # prod=seller=custo=0
        prd = request.POST.get('product')
        prd1 = request.POST.get('product_purch')
        seller = request.POST.get('seller')
        custo = request.POST.get('customer')
        datee = request.POST.get('datee')
        date_purch = request.POST.get('datee1')
        billnumber= request.POST.get('billnumber')
        if prd :
            return redirect(reverse('prod', kwargs={'pk': prd}))
        elif prd1:
            # response = sellershop(request,custo)
            return redirect(reverse('purchprod', kwargs={'pk': prd1}))
        elif seller:
            # response = purchseller_shop(request,seller)
            # return response
            return redirect(reverse('purchseller_shop', kwargs={'pk': seller}))
        elif custo:
            # response = sellershop(request,custo)
            return redirect(reverse('seller_shop', kwargs={'pk': custo}))
        elif datee:
            # response = date_by_query(request,datee,'sale')
            return redirect(reverse('date_wise', kwargs={'pk': datee,'factor':'sale'}))
        elif date_purch:
            # response = date_by_query(request,date_purch,'purchase')
            return redirect(reverse('date_wise', kwargs={'pk': date_purch,'factor':'purchase'}))
        elif billnumber:
            response = invoice(request,billnumber)
            return response
            # return redirect(reverse('invoice1', kwargs={'pk': billnumber}))
        else:
            print('no value')
    return render(request,'search.html',context = {'form':form,'msg':heading})

def multisearch(request):
    heading = "Choses any one field to Search data"
    context_data = {'shopnav': True}
    combined_query =None
    query_prd = Invoice_model.objects.none()
    query_purchprd = Purchase_model.objects.none()
    query_seller = Purchase_model.objects.none()
    query_custo = Invoice_model.objects.none()
    query_datee = Invoice_model.objects.none()
    query_purchdate = Purchase_model.objects.none()
    query_billno = Invoice_model.objects.none()
    form = SearchForm
    if request.method=='POST':
        # prod=seller=custo=0
        prd = request.POST.get('product')
        prd1 = request.POST.get('product_purch')
        seller = request.POST.get('seller')
        custo = request.POST.get('customer')
        datee = request.POST.get('datee')
        date_purch = request.POST.get('datee1')
        billnumber = request.POST.get('billnumber')

        # Create filters dynamically based on input
        if prd:
            query_prd = Invoice_model.objects.filter(product_id=prd)
        if prd1:
            query_purchprd = Purchase_model.objects.filter(product=prd1)
        if seller:
            query_seller = Purchase_model.objects.filter(selbuy=seller)
        if custo:
            query_custo = Invoice_model.objects.filter(selbuy=custo)
        if datee:
            query_datee = Invoice_model.objects.filter(date=datee)
        if date_purch:
            query_purchdate = Purchase_model.objects.filter(date=date_purch)
        if billnumber:
            query_billno = Invoice_model.objects.filter(billnum=billnumber)

        # Combine the queries
        combined_query = query_prd & query_custo & query_datee &  query_billno


        # Print the combined query (for debugging)
        print(combined_query)

    return render(request,'search.html',context = {'form':form,'bill_query':combined_query})

def dashboard_today(request):
    products = Add_item_model.objects.all()
    product_names = []
    balances = []
    for p in products:
        prod_name = p.product
        prod_id = p.id if p.id is not None else 0

        purchased = total_quantity(Purchase_model, prod_id)
        sold = total_quantity(Invoice_model, prod_id)
        balance = purchased - sold
        print(prod_name, balances)
        product_names.append(prod_name)
        balances.append(balance)
################CASH BOXES ######################
    today1 = timezone.now().date()
    today = today1.strftime('%Y-%m-%d')
    head = f'Balances as on {today}'
       
    purch_query=Purchase_model.objects.all()
    purchBook_query = PurchaseBook.objects.all()
    bill_query=Invoice_model.objects.all()
    csh_query = CashBook.objects.all()

    bill_tot = find_sum(bill_query)
    csh_tot = find_sum(csh_query)

    purch_tot = find_sum(purch_query)
    purchBook_tot = find_sum(purchBook_query)
    print()
    a=b=0
    d = mode(purchBook_query,purch_tot,purchBook_tot)
    d1= mode(csh_query,bill_tot,csh_tot)
    d3 = {key: d1.get(key, 0) - d.get(key, 0) for key in d.keys() | d1.keys()} 
    print(d3)
    print('balances',d3)
    payment_data = {
        "Cash": d3.get('cash',0), 
        "UPI": d3.get(' UPI'),    
        "Credit": d3.get('credit',0) 
    }
    print(payment_data)
    # If no products are available, handle empty data
    if not product_names:
        product_names = ["No products available"]
        balances = [0]

################LINE GRAPH####################

    sal_quesry = Invoice_model.objects.all()
    a1 = defaultdict(Decimal) 
    linex = []
    liney = []
    for s in sal_quesry:
        month_separate = s.date1  
        month = month_separate.month  
        amt = find_sum(sal_quesry)  
        a1[month] += amt  
    for month, total in a1.items():
        month_name = calendar.month_name[month]
        linex.append(month_name)
        liney.append(float(total))
    print(dict(a1)) 
################### PENDING PAYMENTS ##############################
    outflow = Purchase_model.objects.all()
    due_pay={}
    for o in outflow:
        get_date = o.date1
        print(get_date)
        purch_date = get_date 
        if isinstance(purch_date, str): 
            purch_date = datetime.strptime(purch_date, '%Y-%m-%d')

        supplier = o.selbuy_id
        supplier_name = o.selbuy
        due_sup = Seller.objects.filter(id=supplier)
        for d in due_sup:
            due_days = d.due_date  
            try:
                due_days = int(due_days) 
            except ValueError:
                print(f"Invalid due_days value: {due_days}. Expected an integer.")
                continue
            
            after_day = purch_date + timedelta(days=due_days)
            tconv_day = after_day.strftime('%Y-%m-%d')
            due_pay[supplier_name] = after_day

    return render(request, 'dashboard.html', {
        # 'head':head,
        'product_names': product_names,
        'balances': balances,
        'payment_data': payment_data,  # Add this line to pass payment data to the template
        'head':head,
        'linex': linex,  # These could represent the months or product names
        'liney': liney,  
        'due_pay':due_pay,
    })
############################ FILTERS ##########################################

#date
# def dateie(request,pk):
#     heading="Sales on "
#     d1,bal,pk = date_by(pk,Invoice_model,CashBook)
#     return render(request,'dateie.html',context={'d1':d1,'bal':bal,'pk':pk,'heading':heading})

# def purchdateie(request,pk):
#     heading="Purchase on" 
#     d1,bal,pk = date_by(pk,Purchase_model,PurchaseBook)
#     return render(request,'dateie.html',context={'d1':d1,'bal':bal,'pk':pk,'heading':heading})

#product
def prod(request,pk):
    pkk=pk
    if pk.isnumeric():
        amt_total,qty_total,name,pages= collect_values(request,pk,Invoice_model,'product_id','product')
        print('number')
    else:
        product_query = Add_item_model.objects.filter(product = pk)
        for p in product_query:
            pkk = p.id
            print(pk)
        amt_total,qty_total,name,pages= collect_values(request,pkk,Invoice_model,'product_id','product')
        print(amt_total,qty_total,name,pages)
    return render(request,'cashflow.html',context={'bill_query':pages,'totquant':qty_total,'name_pk':name,'totamt':amt_total,'sale':True,})


def prod_purch(request,pk):
    pkk=pk
    if pk.isnumeric():
        amt_total,qty_total,name,pages = collect_values(request,pkk,Purchase_model,'product_id','product')
    else:
        product_query = Add_item_model.objects.filter(product = pk)
        for p in product_query:
            pkk = p.id
            print(pk)
        amt_total,qty_total,name,pages = collect_values(request,pkk,Purchase_model,'product_id','product')
        print(amt_total,qty_total,name,pages)
    return render(request,'cashflow.html',context={'bill_query':pages,'totquant':qty_total,'name_pk':name,'totamt':amt_total,'sale':False,})


#selbuy
def seller(request,pk):
    amt_total,qty_total,name,pages = collect_values(request,pk,Invoice_model,'selbuy_id','selbuy')
    amt_total1,qty_total1,name1,pages1 = collect_values(request,pk,CashBook,'selbuy_id','selbuy')
    bal = Decimal(amt_total or 0) - Decimal(amt_total1 or 0)
    return render(request,'cashflow.html',context={'bill_query':pages,'totquant':qty_total,'name_pk':name,'totamt':amt_total,'sale':False,
    'cashquery':pages1,'totamt1':amt_total1,
    'bal':bal})


def seller_purch(request,pk):
    amt_total,qty_total,name,pages = collect_values(request,pk,Purchase_model,'selbuy_id','selbuy')
    amt_total1,qty_total1,name1,pages1 = collect_values(request,pk,PurchaseBook,'selbuy_id','selbuy')
    bal = Decimal(amt_total or 0) - Decimal(amt_total1 or 0)
    return render(request,'cashflow.html',context={'bill_query':pages,'totquant':qty_total,'name_pk':name,'totamt':amt_total,'sale':False,
    'cashquery':pages1,'totamt1':amt_total1,
    'bal':bal})

#mode
def mode_purch(request,pk):
    # cash_sold ,upi_sold,credit_sold,upi_query,cash_query = mode_total(CashBook,Invoice_model,need_query = True)
    cash_purch ,upi_purch,credit_purch,upi_query,cash_query,credit_query = mode_total(PurchaseBook,Purchase_model,need_query = True)
    print(cash_purch ,upi_purch,credit_purch,upi_query,cash_query,credit_query)
    if pk =='cash':
        cashquery = cash_query
        totamt1 = cash_purch
    elif pk =='UPI':
        cashquery = upi_query
        totamt1=upi_purch
    else :
        cashquery = credit_query
        totamt1=credit_purch

    return render(request,'cashflow.html',context={'name_pk':pk,'cashquery':cashquery,'totamt1':totamt1})



def mode(request,pk):
    cash_purch ,upi_purch,credit_purch,upi_query,cash_query,credit_query = mode_total(CashBook,Invoice_model,need_query = True)
    print(cash_purch ,upi_purch,credit_purch,upi_query,cash_query,credit_query)
    if pk =='cash':
        cashquery = cash_query
        totamt1 = cash_purch
    elif pk =='UPI':
        cashquery = upi_query
        totamt1=upi_purch
    else :
        cashquery = credit_query
        totamt1=credit_purch

    return render(request,'cashflow.html',context={'name_pk':pk,'cashquery':cashquery,'totamt1':totamt1})


