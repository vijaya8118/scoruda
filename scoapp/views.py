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
from weasyprint import HTML
from django.template.loader import render_to_string
from tenant_schemas.utils import schema_context, get_tenant_model
from django.db import IntegrityError

#views 
## User defines functions
def formFunction(request,heading,formvar,redirectpage,context_data):
    form = formvar(request.POST or None)
    if request.method=='POST':
        if form.is_valid():
            form.save()
            return redirect(redirectpage)
    return render(request, 'agriform.html', context={'form': form, 'heading': heading,**context_data})

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
        
        return render(request, "agriform.html", context={'form': form, 'shopnav': True})

    def edit_using_id(request, pk):
        obj = get_object_or_404(Modelvar, id=pk)
        if request.method == 'POST':
            form = Formvar(request.POST, request.FILES, instance=obj)
        else:
            form = Formvar(instance=obj)        
        if form.is_valid():
            form.save()
            return redirect(redirect_view)
        
        return render(request, "agriform.html", context={'form': form, 'shopnav': True})

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
        return render(request, "deleteAgri.html", context={'shopnav': True})

    def delete_using_id(request, pk):
        instance = get_object_or_404(Modelvar, id=pk)
        if request.method == 'POST':
            instance.delete()
            return redirect(redirect_view)
        return render(request, "deleteAgri.html", context={'shopnav': True})

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
##filter functions

def mode(query,a,b):
    try:
        credit=0
        csh = query.filter(mode = 'cash')
        cash_dict =csh.aggregate(Sum('amt'))
        cash = cash_dict['amt__sum']
        if (cash == None):
            cash=0

        upi = query.filter(mode = 'UPI')
        upiVal_dict =upi.aggregate(Sum('amt'))
        upiVal = upiVal_dict['amt__sum']
        if (upiVal == None):
            upiVal=0

        credit = int(a or 0) - int(b or 0)
        # credit_dict =cred.aggregate(Sum('amount'))
        # credit = credit_dict['amount__sum']
        if (credit == None):
            credit=0
    except ValueError as ve:
        print("error")

    dict = {
    "cash": cash,
    " UPI": upiVal,
    "credit": credit,
    }
    return dict

def find_sum(query):
        sum_dict = query.aggregate(Sum('amt'))
        sum =sum_dict['amt__sum']
        return sum

def find_quantity(qs):
    dict_total_quantity= qs.aggregate(Sum('qty'))
    total_quantity=dict_total_quantity['qty__sum']
    if total_quantity==None:
        total_quantity=0
    tot =float(total_quantity)
    return tot

def date_by(pk,model1,model2):
        bill_query = model1.objects.filter(date1=pk).order_by('-date')
        bill_sum = find_sum(bill_query)
        csh_query = model2.objects.filter(date1=pk).order_by('-date')
        cash_sum = find_sum(csh_query)
        d1 = mode(bill_query,bill_sum,cash_sum)
        bal = int(bill_sum or 0)- int(cash_sum or 0)
        return d1,bal,pk

def quant_using_prod(request,pk,model):
        lname=pk
        name = "no Entry"
        ppq = model.objects.filter(product_id=lname).order_by('-date')
        for p in ppq:
                name=p.product
        billtot = ppq.aggregate(Sum('qty'))  # total_amount is the key for the aggregate result
        totqty = billtot['qty__sum']
        billtot_amt = ppq.aggregate(Sum('amt'))  # total_amount is the key for the aggregate result
        totamt = billtot_amt['amt__sum']
        paginator = Paginator(ppq, 10)
        page_number = request.GET.get("page")
        pq = paginator.get_page(page_number)
        return totqty,name,pq,totamt

def using_seller_id(model,arg,var):
        query = model.objects.filter(selbuy_id = arg).order_by(var)
        sum = find_sum(query)
        return query,sum

def filter_display(request,query):
    paginator = Paginator(query, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj

####Code
##@allowed_users(allowed_roles=['admin'])
def Add_item(request):
    heading = "Add Product"
    form = Add_item_form(request.POST or None, request.FILES or None)  # Make sure to include request.FILES
    if request.method == 'POST':
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect("additem")  # Redirect after successful form submission
    context = {'form': form, 'heading': heading}
    return render(request, 'agriform.html', context)

def setupCompany(request):
  heading = "Please complete your company profile to continue."
  context_data = {'shopnav': True}
  return formFunction(request,heading,SetupCompany_form,redirectpage='kyc',context_data=context_data)


##@allowed_users(allowed_roles=['admin'])
def seller(request):
  heading = "Add Seller"
  context_data = {'shopnav': True}
  return formFunction(request,heading,Seller_form,redirectpage='seller',context_data=context_data)

#@allowed_users(allowed_roles=['customer'])
def cashbook(request):
  heading = "Cash Receipt"
  context_data = {'shopnav': True}
  return formFunction(request,heading,CashReceipt_form,redirectpage='cashbook',context_data=context_data)

def purchasebook(request):
  heading = "Purchase Receipt"
  context_data = {'shopnav': True}
  return formFunction(request,heading,PurchaseBookForm,redirectpage='purchasebook',context_data=context_data)

##@allowed_users(allowed_roles=['admin'])
def customer(request):
  heading = "Add Customer"
  context_data = {'shopnav': True}
  return formFunction(request,heading,Customer_form,redirectpage='customer',context_data=context_data)

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

# price_edit = edit_view_decorator(Add_item_model, 'item',Add_item_form, use_edit_view=False)

def price_edit(request, pk):
        obj = get_object_or_404(Add_item_model, id = pk)
        form = Add_item_form(request.POST or None, instance = obj)
        if form.is_valid():
            form.save()
            return redirect('prodlist')
        return render(request, "aform.html", context={'form': form,'shopnav': True})

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


##Bills and Purchases
# views.py

def b2c(request):
    head="Sale"
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='')  
    d1 = {}  # Initialize the dictionary for sold products
    d2 = {}  # Initialize the dictionary for stock balance
    d={}
    for p in items:
        prod = p.id
        prod_name = p.product
        purchased = total_quantity(Purchase_model, prod)
        d[prod_name] = purchased
        sold = total_quantity(Invoice_model, prod)
        d1[prod_name] = sold
        bal = purchased - sold
        d2[prod_name] = bal
    in_stock_items = {prod_name: bal for prod_name, bal in d2.items() if bal > 0}
    items_in_stock = [p for p in items if p.product in in_stock_items]
    if Invoice_model.objects.exists():
        query = Invoice_model.objects.latest('date')
        chk = query.billnum
    else:
        chk = 1  # or some fallback value

    form = InvoiceQty_form(request.POST or None)   
    if request.method == "POST":
        invoice = form.save(commit=False)  
        invoice.billnum = chk + 1 
        print('after save',invoice.billnum)
        invoice.save()
    return render(request, 'invoiceb2c.html', {'items':items_in_stock,'form':form,'chk':chk,'head':head})

def process_b2c(request):
    print("enter view")
    if request.method == 'POST':
        print('post')
        try:
            print('enter post try')
            selected_products = json.loads(request.body.decode('utf-8'))
            print(selected_products)
            total_amount = 0            

            # Get the latest bill number
            query = Invoice_model.objects.all().latest('date')
            bill_number = query.billnum + 1
            print('billnumber', bill_number)

            for product in selected_products:
                product_id = product.get('productId')
                themodee = product.get('mode')
                modee = str(themodee)
                print('Mode', modee)
                
                # Parse and calculate quantity
                quantity = product.get('quantity')  # Remove any leading/trailing whitespace
                print('quantity',quantity)

                product_list = Add_item_model.objects.filter(id=product_id)
                
                for p in product_list:
                    ratee = p.rate  
                    print('rate', ratee)
                    try:
                        amt = float(quantity) * float(ratee)
                        print('quantity float',quantity)     
                        print('amount', amt)
                    except Exception as e:
                        print(f"Error calculating amount: {e}")
                        continue
                    
                    # Create new Invoice_model entry with the same bill_number
                    new_data = Invoice_model(
                        product_id=product_id,
                        selbuy_id=2,  # Assuming selbuy_id is static or predefined
                        qty=quantity,
                        rate=ratee,
                        amt=amt,
                        billnum=bill_number,  # Use the same billnum for all entries
                        mode=modee, 
                    )                    
                    new_data.save()
                    print(f"Data saved to the database: {new_data}")
                    if modee in ['cash', 'UPI']:
                        try:
                            cash_book_entry = CashBook(
                                selbuy_id=2,  # Link to the customer or seller/buyer (adjust if needed)
                                amt=amt,  # Amount paid
                                mode=modee,  # Payment mode (cash/UPI)
                                comment=f"Payment for Invoice {bill_number}" , # Optional comment
                            )
                            cash_book_entry.save()
                            print(f"CashBook entry saved: {cash_book_entry}")
                        except Exception as e:
                            print(f"Error saving CashBook entry: {e}")
            
            return redirect('invoice')  # Redirect to the b2c page after processing
        except Exception as e:
            print(f"Error processing order: {e}")
            return render(request, 'port.html', context={})
    return render(request, 'invoiceb2c.html', context={})

def b2b(request):
    head = "Bill"
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='')  
    d1 = {}  # Initialize the dictionary for sold products
    d2 = {}  
    d={}
    for p in items:
        prod = p.id
        prod_name = p.product
        purchased = total_quantity(Purchase_model, prod)
        d[prod_name] = purchased
        sold = total_quantity(Invoice_model, prod)
        d1[prod_name] = sold
        bal = purchased - sold
        d2[prod_name] = bal
    form = InvoiceSecond_form(request.POST or None)
    print(items)
    return render(request, 'invoiceb2b.html', context={'items': items, 'head': head, 'form': form})

@require_POST
@csrf_exempt
def process_b2b(request):
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
                latest_invoice = Invoice_model.objects.latest('date')
                bill_number = latest_invoice.billnum + 1
            except Invoice_model.DoesNotExist:
                # If no invoices exist, set the initial bill number to 1
                bill_number = 1
            print('Bill number:', bill_number)
            for product in selected_products:  
                if not isinstance(product, dict):
                    print(f"Skipping invalid product: {product}")
                    continue
                product_id = product.get('productId')
                payment_mode = product.get('mode')  # Payment mode
                quantity = product.get('qty', 1)  # Default quantity is 1 if not provided
                seller_buyer_id = product.get('customer')  
            
                seller_buyer = Customer.objects.get(id=seller_buyer_id)
                print('Mode:', payment_mode)                              
                print('Quantity:', quantity)  
                print("Seller/Buyer:", seller_buyer)
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
                        amount = float(quantity) * float(ratee)  # Calculate the amount
                        print('Amount:', amount)
                    except Exception as e:
                        print(f"Error calculating amount: {e}")
                        continue
                    new_invoice = Invoice_model(
                        product_id=product_id,
                        qty=quantity,
                        rate = ratee,
                        amt=amount,
                        billnum=bill_number,  # Ensure all products have the same billnum
                        mode=payment_mode,
                        selbuy=seller_buyer,  # Now passing the actual Customer instance
                    )
                    new_invoice.save()
                    print(f"Invoice data saved: {new_invoice}")
                    total_amount += amount

                    # If the payment mode is cash or UPI, create an entry in the CashBook model
                    if payment_mode in ['cash', 'UPI']:
                        try:
                            cash_book_entry = CashBook(
                                selbuy=seller_buyer,  # Link to the customer
                                amt=amount,  # Amount paid
                                mode=payment_mode,  # Payment mode (cash/UPI)
                                comment=f"Payment for Invoice {bill_number}"  # Optional comment
                            )
                            cash_book_entry.save()
                            print(f"CashBook entry saved: {cash_book_entry}")
                        except Exception as e:
                            print(f"Error saving CashBook entry: {e}")
            
            return redirect('invoice')
        except Exception as e:
            print(f"Error processing order: {e}")
    return render(request, 'invoiceb2b.html', context={})

       

def purchase_auto(request):
    head="Purchase "
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='')  
    return render(request,'invoice_purchAuto.html',context={'items':items,'head':head})


def purchaseauto_process(request):
    print("enter Purchase view")
    if request.method == 'POST':
        print('POST request received')
        
        try:
            print('Entering POST try block')
            
            # Parse JSON data from the request body
            selected_products = json.loads(request.body.decode('utf-8'))
            print("Selected Products:", selected_products)

            # Validate that selected_products is a list
            if not isinstance(selected_products, list):
                raise ValueError("Expected a list of products, got something else.")
                
            total_amount = 0
            
            # Iterate through each selected product
            for product in selected_products: 
                print(f"Inspecting product: {product}")
                
                if not isinstance(product, dict):
                    print(f"Skipping invalid product: {product}")
                    continue
                
                # Extract product details
                product_id = product.get('productId')
                payment_mode = product.get('mode')  # Payment mode
                quantityy = product.get('quantity')  # Quantity
                print(f"Product ID: {product_id}, Payment Mode: {payment_mode}, Raw Quantity: {quantityy}")
                
                # Handle quantity: convert string to float if necessary
                if isinstance(quantityy, str):
                    print('Quantity is a string')
                    quantityy = quantityy.strip()  # Strip any whitespace
                    try:
                        quantity = float(quantityy)
                        print("Converted Quantity:", quantity)
                    except ValueError:
                        print(f"Error processing order: invalid literal for float: '{quantityy}'")
                        quantity = None  # If invalid, set quantity to None
                else:
                    quantity = quantityy
                
                print(f"Processed Quantity: {quantity} (Type: {type(quantity)})")
                
                # Assume seller_buyer_id = 1 for now, this might be dynamic in your case
                seller_buyer_id = 1
                print(f"Seller ID: {seller_buyer_id}")
                
                try:
                    seller_buyer = Seller.objects.get(id=seller_buyer_id)
                    print(f"Seller found: {seller_buyer}")
                except Seller.DoesNotExist:
                    print(f"Seller with ID {seller_buyer_id} not found.")
                    continue  # Skip to the next product if the seller is not found
                
                # Check if product_id is valid
                if not product_id:
                    print("Missing product ID, skipping this product.")
                    continue
                
                # Query for product details
                product_list = Add_item_model.objects.filter(id=product_id)
                if not product_list.exists():
                    print(f"Product with ID {product_id} not found.")
                    continue
                
                for p in product_list:
                    ratee = p.rate_purch  # Product rate
                    print(f"Product Rate: {ratee} (Type: {type(ratee)})")
                    
                    try:
                        # Calculate the amount for this product
                        amount = float(quantity) * float(ratee)
                        print(f"Calculated Amount: {amount}")
                    except Exception as e:
                        print(f"Error calculating amount: {e}")
                        continue
                    
                    # Create a new purchase record (invoice)
                    new_invoice = Purchase_model(
                        product_id=product_id,
                        qty=quantity,
                        rate=ratee,
                        amt=amount,
                        mode=payment_mode,
                        selbuy=seller_buyer,  # Assign the actual Seller instance
                    )

                    # Save the invoice to the database
                    new_invoice.save()
                    print(f"Invoice data saved: {new_invoice}")
                    
                    # Update the total amount for all products
                    total_amount += amount
                    
                    # If payment mode is cash or UPI, log it in the PurchaseBook
                    if payment_mode in ['cash', 'UPI']:
                        try:
                            purchase_book_entry = PurchaseBook(
                                selbuy=seller_buyer,  # Link to the seller
                                amt=amount,  # Amount paid
                                mode=payment_mode,  # Payment mode (cash/UPI)
                            )
                            purchase_book_entry.save()
                            print(f"PurchaseBook entry saved: {purchase_book_entry}")
                        except Exception as e:
                            print(f"Error saving PurchaseBook entry: {e}")

            # If processing is successful, redirect to 'purchaseprod'
            return redirect('purchaseprod')

        except Exception as e:
            # Log any errors that occur during the processing
            print(f"Error processing order: {e}")
            # Return an error message to the user
            return render(request, 'port.html', context={'error_message': 'Error processing order.'})

    # If it's a GET request, render the invoice page
    return render(request, 'invoice_purchAuto.html', context={})


def purchase(request):
    head="Purchase"
    items = Add_item_model.objects.exclude(image__isnull=True).exclude(image__exact='') 
    form = Purchase_form2(request.POST or None) 
    return render(request,'invoice_purch.html',context={'items':items,'head':head,'form':form,})


import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Purchase_model, Seller, Add_item_model, PurchaseBook


@require_POST
def process_purchase(request):
    print("enter Purchase view")
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
                return JsonResponse({'status': 'error', 'message': 'No products received.'})

            try:
                latest_invoice = Purchase_model.objects.latest('date')
                bill_number = latest_invoice.num + 1
            except Purchase_model.DoesNotExist:
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

                try:
                    seller_buyer = Seller.objects.get(id=seller_buyer_id)
                except Seller.DoesNotExist:
                    print(f"Seller with ID {seller_buyer_id} not found.")
                    continue

                if not product_id:
                    print("Missing product ID, skipping this product.")
                    continue

                product_list = Add_item_model.objects.filter(id=product_id)
                if not product_list.exists():
                    print(f"Product with ID {product_id} not found.")
                    continue

                for p in product_list:
                    rate = p.rate_purch
                    try:
                        amount = float(quantity) * float(rate)
                    except Exception as e:
                        print(f"Error calculating amount: {e}")
                        continue

                    new_invoice = Purchase_model(
                        product_id=product_id,
                        qty=quantity,
                        amt=amount,
                        mode=payment_mode,
                        selbuy=seller_buyer,
                        rate=rate,
                        num=bill_number
                    )
                    new_invoice.save()
                    total_amount += amount
                    print(f"Saved invoice: {new_invoice}")

                    if payment_mode in ['cash', 'UPI']:
                        try:
                            purchase_book_entry = PurchaseBook(
                                selbuy=seller_buyer,
                                amt=amount,
                                mode=payment_mode,
                                comment=f"Payment for Purchase Invoice {bill_number}"
                            )
                            purchase_book_entry.save()
                            print(f"PurchaseBook entry saved: {purchase_book_entry}")
                        except Exception as e:
                            print(f"Error saving PurchaseBook entry: {e}")

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"Error processing order: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error processing order.'})
    return render(request, 'invoice_purch.html', context={})

###overviews
##@allowed_users(allowed_roles=['admin'])
def sumAmt(model, cmpVal):
    # Fetch the queryset for the given product_id and order it by 'num' in descending order
    q = model.objects.filter(product_id=cmpVal).order_by('-num')
    sum_amount = 0
    discount = None

    # Iterate over the queryset to calculate the sum_amount and get the latest discount
    for item in q:
        discount = item.product
        sum_amount += item.amt

    return sum_amount, q, discount

def productAnalysis(request):
        head = "profit/Loss per Product"
        tot={}
        g ={}
        d={}
        d1={}
        d2={}   # initialtion done before the calculation
        main_query = Add_item_model.objects.all()
        for m in main_query:
            products = m.id
            prod =m.product
            purch_query=Purchase_model.objects.all().filter(product_id = products)
            bill_query=Invoice_model.objects.all().filter(product_id = products)
            sold = find_sum(bill_query)
            purchased = find_sum(purch_query)
            d1[prod]=sold
            d[prod]=purchased
        for key in d1.keys():
            value1 = d1.get(key, Decimal(0))
            value2 = d.get(key, Decimal(0))

            # Ensure value1 and value2 are not None
            if value1 is None:
                value1 = Decimal(0)
            if value2 is None:
                value2 = Decimal(0)

            # Perform the subtraction
            d2[key] = value1 - value2
        context={
                "d":d,"d1":d1,
                "d2":d2,'head':head,
        }
        return render(request,'mode.html',context)


##@allowed_users(allowed_roles=['admin'])
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
            response = invoice1(request,billnumber)
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


##@allowed_users(allowed_roles=['admin'])
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

        # # Check if prod_name (or prod if you want to check ID) is in d2
        # if prod_name in d2:  # Assuming you're checking by product name (prod_name)
        #     print(prod_name)  # Key exists
        # else:
        #     print('nope')  # Key doesn't exist

    return render(request,'mode.html',context={'d':d,'d1':d1,'d2':d2,'head':head,'products':products})

def scout(request):
        head = "SCOUT"
        purch_query=display(request,Purchase_model,'-date')
        bill_query = display(request,Invoice_model,'-date')
            
        context={
            'purch_query':purch_query,'bill_query':bill_query,'head':head,'shopnav':True,
        }
        return render(request,'scoutAgri.html',context)


from django.shortcuts import render
from .models import Invoice_model

def invoice(request):
    # Fetch the latest invoice and related products
    query = Invoice_model.objects.all().latest('date')
    latest_invoices = Invoice_model.objects.filter(billnum=query.billnum)

    # Initialize variables
    products = []
    invoice_num = invoice_to = created = payment = ""
    
    if latest_invoices.exists():
        # Get the first invoice details
        first_invoice = latest_invoices[0]
        invoice_num = first_invoice.billnum
        invoice_to = first_invoice.selbuy
        created = first_invoice.date1
        payment = first_invoice.mode
        
        # Prepare products list
        for qs in latest_invoices:
            products.append({
                'commodity': qs.product,
                'quantity': qs.qty,
                'price': qs.rate,  # Assuming price is a field in the Invoice model
                'current_price': qs.amt,
            })

    # Prepare the context for rendering
    context = {
        'products': products,
        'invoice_num': invoice_num,
        'invoice_to': invoice_to,
        'created': created,
        'payment': payment,
    }
    
    return render(request, 'billdis.html', context)



def invoice1(request,chk):
    latest_invoices = Invoice_model.objects.filter(billnum=chk)

    # Initialize variables
    products = []
    invoice_num = invoice_to = created = payment = ""
    
    if latest_invoices.exists():
        # Get the first invoice details
        first_invoice = latest_invoices[0]
        invoice_num = first_invoice.billnum
        invoice_to = first_invoice.selbuy
        created = first_invoice.date1
        payment = first_invoice.mode
        
        # Prepare products list
        for qs in latest_invoices:
            products.append({
                'commodity': qs.product,
                'quantity': qs.qty,
                'price': qs.rate,  # Assuming price is a field in the Invoice model
                'current_price': qs.amt,
            })

    # Prepare the context for rendering
    context = {
        'products': products,
        'invoice_num': invoice_num,
        'invoice_to': invoice_to,
        'created': created,
        'payment': payment,
    }
    
    return render(request, 'billdis.html', context)


##filters
def dateie(request,pk):
    heading="Sales on "
    d1,bal,pk = date_by(pk,Invoice_model,CashBook)
    return render(request,'dateie.html',context={'d1':d1,'bal':bal,'pk':pk,'shopnav':True,'heading':heading})

def purchdateie(request,pk):
    heading="Purchase on" 
    d1,bal,pk = date_by(pk,Purchase_model,PurchaseBook)
    return render(request,'dateie.html',context={'d1':d1,'bal':bal,'pk':pk,'shopnav':True,'heading':heading})

def prod(request,pk):
    bill,name ,pq,totamt= quant_using_prod(request,pk,Invoice_model)
    return render(request,'bill.html',context={'bill_query':pq,'totquant':bill,'name_pk':name,'totamt':totamt,'shopnav':True})

def purchprod(request,pk):
    bill,name ,pq,totamt= quant_using_prod(request,pk,Purchase_model)
    return render(request,'purchase.html',context={'purchase_query':pq,'totquant':bill,'name_pk':name,'totamt':totamt,'shopnav':True,})


def purchseller_shop(request,pk):
    name_pk="Seller"
    purchase_query_query = Purchase_model.objects.filter(selbuy_id = pk).order_by('-date')
    for b in purchase_query_query:
        name_pk =b.selbuy
    totamt = find_sum(purchase_query_query) 
    purchtot=find_quantity(purchase_query_query)
    paginator = Paginator(purchase_query_query, 10)
    page_number = request.GET.get("page")
    purchase_query = paginator.get_page(page_number) 

    csh_query_query,cash_sum = using_seller_id(PurchaseBook,pk,'-date')
    csh_query = filter_display(request,csh_query_query)
    bal = int(totamt or 0) - int(cash_sum or 0)
    return render(request,'purchase.html',context={'purchase_query':purchase_query,'totamt':totamt,
    'bal':bal,'purchbook_query':csh_query,'purchtot':cash_sum,'shopnav':True,'totquant':purchtot,'name_pk':name_pk,
                                        })

def sellershop(request,pk):
    name_pk = 'Customer'
    bill_query_query = Invoice_model.objects.filter(selbuy_id = pk).order_by('-date')
    for b in bill_query_query:
        name_pk =b.selbuy
    totamt = find_sum(bill_query_query)
    billtot=find_quantity(bill_query_query)
    print('billtot')
    paginator = Paginator(bill_query_query, 10)
    page_number = request.GET.get("page")
    bill_query = paginator.get_page(page_number) 


    csh_query_query,cash_sum = using_seller_id(CashBook,pk,'-date')
    csh_query = filter_display(request,csh_query_query)

    bal = int(totamt or 0) - int(cash_sum or 0)
    return render(request,'bill.html',context={'bill_query':bill_query,'totamt':totamt,
    'bal':bal,'cashquery':csh_query,'cashtot':cash_sum,'shopnav':True,'totquant':billtot,'name_pk':name_pk,
                                        })

def date_by_query(request,pk,factor):
    if(factor=='sale'):
        bill_query_query = Invoice_model.objects.filter(date1 = pk).order_by('-date')
        billtot = find_sum(bill_query_query) 
        paginator = Paginator(bill_query_query, 10)
        page_number = request.GET.get("page")
        bill_query = paginator.get_page(page_number) 

        cash_query_query = CashBook.objects.filter(date1 = pk).order_by('-date')
        cashtot = find_sum(cash_query_query) 
        paginator = Paginator(cash_query_query, 10)
        page_number = request.GET.get("page")
        csh_query = paginator.get_page(page_number)
        bal = int(billtot or 0) - int(cashtot or 0)
        return render(request,'bill.html',context={'bill_query':bill_query,'billtot':billtot,
        'bal':bal,'cashquery':csh_query,'cashtot':cashtot,'shopnav':True,'pk':pk,
                                            })
    else:
        purchase_query_query = Purchase_model.objects.filter(date1 = pk).order_by('-date')
        purchtot = find_sum(purchase_query_query) 
        paginator = Paginator(purchase_query_query, 10)
        page_number = request.GET.get("page")
        purchase_query = paginator.get_page(page_number) 

        cash_query_query = PurchaseBook.objects.filter(date1 = pk).order_by('-date')
        cash_sum = find_sum(cash_query_query) 
        paginator = Paginator(cash_query_query, 10)
        page_number = request.GET.get("page")
        csh_query = paginator.get_page(page_number)
        bal = int(purchtot or 0) - int(cash_sum or 0)
        return render(request,'purchase.html',context={'purchase_query':purchase_query,'purchtot':purchtot,
        'bal':bal,'purchbook_query':csh_query,'cashtot':cash_sum,'shopnav':True,
                                            })    

def purchmode_shop(request,pk):
    if (pk =='credit'):
                print('hello purchase')
                d1={}
                a={}
                b={}# creating dict
                customer_query = Seller.objects.all()
                for c in customer_query:
                    name_arg = c.id
                    name_for_dict = c.name
                    var = Purchase_model.objects.all().filter(selbuy =name_arg )
                    bill_quer,bill =using_seller_id(Purchase_model,name_arg,'-num')
                    cash_receipt,cash =using_seller_id(PurchaseBook,name_arg,'-date')
                    bal = int(bill or 0) - int(cash or 0)
                    d1[name_arg]=name_for_dict #dict created
                    a[name_for_dict]=bal #dict created
                    print('purchase',d1)
                b = Purchase_model.objects.all()
                c =PurchaseBook.objects.all()
                bil = find_sum(b)
                cas = find_sum(c)
                tot_bal = int(bil or 0)- int(cas or 0)
                return render(request,'creditpurch.html',context={'d1':d1,'tot_bal':tot_bal,'name_arg':name_arg,'a':a,'pk':pk})
    else:
        print(pk)
        purchaseBook_query = PurchaseBook.objects.filter(mode =pk)
        paginator = Paginator(purchaseBook_query, 10)
        page_number = request.GET.get("page")
        purchbook_query = paginator.get_page(page_number) 
        purchtot = find_sum(purchaseBook_query) 
    return render(request,'purchase.html',context={'purchbook_query':purchbook_query,'purchtot':purchtot,'pk':pk})



def mode_shop(request,pk):
    if (pk =='credit'):
                print("hello sale")
                d1={}
                a={}
                b={}# creating dict
                customer_query = Customer.objects.all()
                for c in customer_query:
                    name_arg = c.id
                    name_for_dict = c.name
                    var = Invoice_model.objects.all().filter(selbuy =name_arg )
                    bill_quer,bill =using_seller_id(Invoice_model,name_arg,'-num')
                    cash_receipt,cash =using_seller_id(CashBook,name_arg,'-date')
                    bal = int(bill or 0) - int(cash or 0)
                    d1[name_arg]=name_for_dict #dict created
                    a[name_for_dict]=bal #dict created
                    print(d1)
                b = Invoice_model.objects.all()
                c =CashBook.objects.all()
                bil = find_sum(b)
                cas = find_sum(c)
                tot_bal = int(bil or 0)- int(cas or 0)
                return render(request,'creditsale.html',context={'d1':d1,'tot_bal':tot_bal,'name_arg':name_arg,'a':a,'pk':pk})
    else:
        
        purchaseBook_query = CashBook.objects.filter(mode =pk).order_by('-date')
        purchbook_query = filter_display(request,purchaseBook_query)
        purchtot = find_sum(purchaseBook_query) 
    return render(request,'bill.html',context={'cashquery':purchbook_query,'cashtot':purchtot,'pk':pk})

from django.db.models import Q

def credit(request,pk):
    name_pk = 'Customer'
    SaleBook_query = Invoice_model.objects.filter(Q(mode='credit') & Q(selbuy_id=pk)).order_by('-date')
    for p in SaleBook_query:
        name_pk = p.selbuy
    bill_query = filter_display(request,SaleBook_query)
    totamt= find_sum(SaleBook_query)
    totquant=find_quantity(SaleBook_query)
    print(SaleBook_query)
    return render(request,'bill.html',context={'bill_query':bill_query,'totamt':totamt,'totquant':totquant,'name_pk':name_pk})

def credit1(request,pk):
    name_pk = 'Seller'
    purchaseBook_query = Purchase_model.objects.filter(Q(mode='credit') & Q(selbuy_id=pk)).order_by('-date')
    for p in purchaseBook_query:
        name_pk = p.selbuy
    totamt= find_sum(purchaseBook_query)
    totquant=find_quantity(purchaseBook_query)
    purchase_query = filter_display(request,purchaseBook_query)
    return render(request,'purchase.html',context={'purchase_query':purchase_query,'totamt':totamt,'totquant':totquant,
                                                   'name_pk':name_pk})

def cash_balance(request):
        head = "CASH BALANCE"
        tot={}
        g ={}
        d={}
        d1={}
        d2={}   # initialtion done before the calculation

        purch_query=Purchase_model.objects.all()
        purchBook_query = PurchaseBook.objects.all()
        bill_query=Invoice_model.objects.all()
        csh_query = CashBook.objects.all()

        bill_tot = find_sum(bill_query)
        csh_tot = find_sum(csh_query)

        purch_tot = find_sum(purch_query)
        purchBook_tot = find_sum(purchBook_query)
        ###change when purchase modele
        print()
        a=b=0
        d = mode(purchBook_query,purch_tot,purchBook_tot)
        # d1 = mode(bill_query)
        d1= mode(csh_query,bill_tot,csh_tot)


        # tot = {key: d1[key] + d3.get(key, 0)
        #                    for key in d1.keys()}

        d2 = {key: d1[key] - d.get(key, 0)
                        for key in d1.keys()}

        context={
                "d":d,"d1":d1,
                "d2":d2,'a':a,'head':head,
        }
        return render(request,'mode.html',context)

##user Authentication
def frontPage(request):
    return render(request,'frontpage.html',context={})


import csv
from django.core.files.storage import FileSystemStorage

# def upload_users(request):
#     form = UploadFileForm(request.POST, request.FILES)
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)
#         file_path = fs.path(filename)
#         try:
#                 # Try opening the file with UTF-8 encoding
#                 with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
#                     reader = csv.DictReader(csvfile)
#                     for row in reader:
#                         for row in reader:
#                             Invoice_model.objects.create(
#                              date=row['date'],
#                             date1=row['date1'],
#                             num=row['num'],
#                             billnum=row['billnum'],
#                             mode=row['mode'],
#                             product=row['product'],
#                             qty=row['qty'],
#                             rate=row['rate'],
#                             amt =row['amt'],
#                                 # Add other fields as needed
#                             )
#                             print('sucess1')
#         except UnicodeDecodeError:
#                 # If UTF-8 encoding fails, try another encoding (e.g., ISO-8859-1)
#                 with open(file_path, 'r', newline='', encoding='ISO-8859-1') as csvfile:
#                     reader = csv.DictReader(csvfile)
#                     for row in reader:
#                         Invoice_model.objects.create(
#                             date=row['date'],
#                             date1=row['date1'],
#                             num=row['num'],
#                             billnum=row['billnum'],
#                             mode=row['mode'],
#                             product=row['product'],
#                             qty=row['qty'],
#                             rate=row['rate'],
#                             amt =row['amt'],
#                         )
#                         print('sucess2')

#     return render(request, 'file.html', {'form': form})


from django.http import JsonResponse
import redis

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# def serial_data(request):
    # data = redis_client.get('serial_data')

    # if data:
    #     try:
    #         decoded_data = data.decode('utf-8', errors='ignore')  
    #         if decoded_data == data.decode('utf-8', errors='ignore'):
    #             hex_data = data.hex()
    #             hex_data = hex_data
    #         else:
    #             hex_data=hex_data
    #     except Exception as e:
    #         hex_data = "Error decoding the data"
    # else:
    #     hex_data = "Waiting for data"
    # form = TestForm(request.POST or None) 
    # if request.method == 'POST':
    #     # The form is being submitted via POST
    #     data = request.POST.get('data')  # Get the 'data' value from the form

    #     if data:
    #         # Create a new ReceivedData instance and save it
    #         new_data = Test_model(rate=data)
    #         new_data.save()
    #           # Redirect to a success page or another view
    
    # return render(request,'port.html',context={})




def index(request):
    return render(request,'index.html',context={})

####receiving serial data 
def serial_data(request):
    
    product_list = Add_item_model.objects.filter(id=6)
    query = Invoice_model.objects.all().latest('date')
    bill_number = query.billnum
    if request.method == 'POST':
        print("POST request received.")
        quant_hexa = request.POST.get('data')
        quant= quant_hexa.split('4\x04')[0]
        print(f"Data received from form: {quant}")        
        if quant:
            for p in product_list:
                ratee = p.rate  # Get the rate for the current product
                quantity = int(quant)  # Ensure quantity is an integer
                new_data = Invoice_model(
                    product_id=p.id,
                    selbuy_id=2,  # Assuming '2' is a fixed value; you may want to update this dynamically
                    qty=quantity,
                    amt=quantity * ratee,
                    billnum=bill_number,
                )
                new_data.save()
                print(f"Data saved to the database: {new_data}")                
            return redirect('b2c')
        else:
            print("No data received from the form.")    
    return render(request, 'port_conn.html', context={})


##################### REGISTRATION AND LOGIN ####################
def createCompany(request):
    form = TenantForm()  # Default form for GET requests
    print('Before POST')

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
    
    return render(request, 'form.html', context={'form': tenant_form if request.method == 'POST' else form})


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
            if role == 'admin':
                group = Group.objects.get(name='admin')
            elif role == 'manager':
                group = Group.objects.get(name='manager')
            elif role == 'employee':
                group = Group.objects.get(name='employee')
            else:
                group = Group.objects.get(name='employee')  
            new_member.groups.add(group)
            login(request, new_member)#auto login

            messages.success(request, f"Member {role} created successfully!")
            return redirect('profile')  
        else:
            messages.error(request, "There was an error creating the member.")
    else:
        form = MemberForm()
    return render(request, 'agriform.html', {'form': form,'heading':heading})

def loginPage(request):
    if request.user.is_authenticated:
            return redirect('show')
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username = username,password = password)
        if user is not None:
            login(request,user)
            request.session.set_expiry(1209600)
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

def kyc(request):
    # Fetch all users from the Members model
    users = Members.objects.all()  # Retrieve all users from the database
    company_query = SetupCompany.objects.all()

    return render(request, 'kyc.html', {'users': users,'company_query':company_query,})

from datetime import datetime, timedelta

#############################

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

def landing(request):
    return render(request,'landing.html',context={})


#########################   Add onns     #####################################
def download_pdf(request):
    html_content = render_to_string('pdf_template.html', {'data': 'some_data'})
    pdf = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'

    return response



def handle_csv_upload(request, model, field_mappings):
    """
    Handles file upload, form validation, and saves CSV data to the given model.

    :param request: Django HttpRequest object
    :param model: Django model class
    :param field_mappings: Dict mapping model fields to CSV columns
    :return: Tuple (success: bool, form instance)
    """
    form = UploadFileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            _parse_and_save(file_path, model, field_mappings, encoding='utf-8')
        except UnicodeDecodeError:
            _parse_and_save(file_path, model, field_mappings, encoding='ISO-8859-1')

        return True, form  # Indicate success

    return False, form  # Return form with errors if not valid


def _parse_and_save(file_path, model, field_mappings, encoding):
    with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        print('111111111111111111')
        for row in reader:
            data = {
                model_field: row[csv_column]
                for model_field, csv_column in field_mappings.items()
            }
            print(data)
            model.objects.create(**data)


def upload_items(request):
    field_mappings = {
        'product': 'product',
        'rate_purch': 'rate_purch',
        'rate': 'rate',
    }
    success, form = handle_csv_upload(request, Add_item_model, field_mappings)
    return render(request, 'file.html', {'form': form, 'success': success})

def upload_customer(request):
    field_mappings = {
        'name': 'name',
        'address': 'address',
        'phone': 'phone',
        'bank':'bank',
        'account':'account',
        'ifsc':'ifsc',
    }
    success, form = handle_csv_upload(request, Customer, field_mappings)
    return render(request, 'file.html', {'form': form, 'success': success})

def upload_seller(request):
    field_mappings = {
        'name': 'name',
        'address': 'address',
        'phone': 'phone',
        'bank':'bank',
        'account':'account',
        'ifsc':'ifsc',
    }
    success, form = handle_csv_upload(request, Seller, field_mappings)
    return render(request, 'file.html', {'form': form, 'success': success})

##################
def parse_csv(file):
    return csv.DictReader(file.read().decode('utf-8').splitlines())

# Helper: get model instance by ID
def get_instance(model, pk):
    try:
        return model.objects.get(id=pk)
    except model.DoesNotExist:
        return None

def handle_csv_upload1(request, model_class, selbuy_model, product_model=None):
    invalid_rows = []  # Declare at a higher level so it's always available

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            reader = parse_csv(request.FILES['file'])

            for idx, row in enumerate(reader, start=1):
                try:
                    customer = get_instance(selbuy_model, int(row['selbuy'].strip()))
                    if not customer:
                        raise ValueError(f"Invalid customer ID: {row['selbuy']}")

                    data = {
                        'date': datetime.fromisoformat(row['date']),
                        'date1': datetime.strptime(row['date1'], '%Y-%m-%d').date(),
                        'selbuy': customer,
                        'mode': row['mode'],
                        'amt': float(row['amt']),
                        
                    }

                    if 'comment' in row:
                        data['comment'] = row['comment']
                    if 'billnum' in row:
                        data['billnum'] = int(row['billnum'])

                    if product_model and 'product' in row:
                        product = get_instance(product_model, int(row['product'].strip()))
                        if not product:
                            raise ValueError(f"Invalid product ID: {row['product']}")
                        data.update({
                            'product': product,
                            'qty': float(row['qty']),
                            'rate': float(row['rate']),
                        })

                    model_class.objects.create(**data)

                except Exception as e:
                    invalid_rows.append({'row': idx, 'data': row, 'error': str(e)})

            if invalid_rows:
                messages.warning(request, "Some rows were skipped due to errors.")
            else:
                messages.success(request, "CSV processed successfully.")
    else:
        form = UploadFileForm()

    return render(request, 'file.html', {
        'form': form,
        'invalid_rows': invalid_rows
    })


def upload_invoice(request):
    return handle_csv_upload1(request, Invoice_model, Customer, Add_item_model)

def upload_purchase(request):
    return handle_csv_upload1(request, Purchase_model, Seller, Add_item_model)

def upload_cashebook(request):
    return handle_csv_upload1(request, CashBook, Customer)

def upload_purchasebook(request):
    return handle_csv_upload1(request, PurchaseBook, Seller)
