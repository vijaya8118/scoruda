from django import forms
from .models import *
from django.core.exceptions import ValidationError
import re
from django.db import connection
from django.contrib.auth.hashers import make_password


class UploadForm(forms.Form):
    file = forms.FileField()

class TenantForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude=('domain_url',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add Company Name ...'}),
            'schema_name': forms.TextInput(attrs={'placeholder': 'Add Subdomain ...'}),
        }

    def clean_schema_name(self):
        schema_name = self.cleaned_data['schema_name'].lower()

        # Validate the format of the schema name
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', schema_name):
            raise ValidationError("Subdomains can only contain lowercase letters, numbers, and hyphens!")

        # Ensure uniqueness of the schema name
        if Client.objects.filter(schema_name__iexact=schema_name).exists():
            raise ValidationError("This subdomain is already taken.")
        
        # Optionally: Check if the schema already exists in the database
        if self.schema_exists(schema_name):
            raise ValidationError("This schema already exists in the database.")
        
        # Optionally: Prevent the use of certain reserved schema names
        reserved_names = ['admin', 'support', 'reserved']
        if schema_name in reserved_names:
            raise ValidationError("This subdomain name is reserved.")

        return schema_name

    def schema_exists(self, schema_name):
        """Check if the schema already exists in the database."""
        # This check is specific to PostgreSQL
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname = %s", [schema_name])
                return cursor.fetchone() is not None
        return False  # For other databases, you might need a different check


class MemberForm(forms.ModelForm):
    class Meta:
        model = Members
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_no', 'role', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['phone_no'].widget.attrs.update({'placeholder': 'Enter 10-digit phone number'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter email address'})
        self.fields['role'].help_text = "Choose the role of the member."

        # Make password field use password input widget
        self.fields['password'].widget = forms.PasswordInput()

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if len(phone_no) != 10 or not phone_no.isdigit():
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone_no

    def clean_password(self):
        password = self.cleaned_data.get('password')
        hashed_password = make_password(password)
        return hashed_password

    
################## ###################
class SetupCompany_form(forms.ModelForm):
    class Meta:
        model = SetupCompany
        fields='__all__'
        exclude=('user',)

# def SetupCompanyFormFactory(user):
#     SetupCompany = get_strategy(user).SetupCompany

#     class SetupCompanyForm(forms.ModelForm):
#         class Meta:
#             model = SetupCompany
#             fields = '__all__'
#             exclude = ('user',)

#     return SetupCompanyForm

class SearchForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Add_item_model_sale.objects.all(),initial=None,required=False)
    seller = forms.ModelChoiceField(queryset=Seller.objects.all(),initial=None,required=False)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(),initial=None,required=False)

class Add_item_purch_form(forms.ModelForm):
    class Meta:
        model=Add_item_model_purch
        fields='__all__'
        exclude=('user',)

class Add_item_sale_form(forms.ModelForm):
    class Meta:
        model=Add_item_model_sale
        fields='__all__'
        exclude=('user',)

class PurchaseCounter_form(forms.ModelForm):
    class Meta:
        model=Purchase_model
        fields=['qty','mode']
        exclude=('dis','amount','amt','product','selbuy','user','rate','user')

class Purchase_form(forms.ModelForm):
    class Meta:
        model=Purchase_model
        fields='__all__'
        exclude=('dis','user')


class Purchase_form2(forms.ModelForm):
    class Meta:
        model=Purchase_model
        fields=['mode','selbuy',]


class PurchaseManual_form(forms.ModelForm):
    class Meta:
        model=Purchase_model
        fields='__all__'
        exclude=('user','date','date1','gst',)

class CashReceipt_form(forms.ModelForm):
    # COMMENT_CHOICES = [
    #     ('Advance Paid', 'Advance Paid'),
    #     ('Balance Paid', 'Balance Paid'),
    #     ('Full Payment', 'Full Payment'),
    #     ('Other', 'Other'),
    # ]

    # comment = forms.ChoiceField(
    #     choices=COMMENT_CHOICES,
    #     required=False,
    #     widget=forms.Select(attrs={'id': 'id_comment'})
    # )

    class Meta:
        model = CashBook
        fields = '__all__'
        exclude = ('user',)


class InvoiceSecond_form(forms.ModelForm):
    class Meta:
        model=Invoice_model
        fields=['mode','selbuy','qty','amt',]

class InvoiceQty_form(forms.ModelForm):
    class Meta:
        model = Invoice_model
        fields = ('qty',)

class InvoiceMode_form(forms.ModelForm):
    class Meta:
        model = Invoice_model
        fields = ('mode',)     

class GenerateInvoice_form(forms.ModelForm):
    class Meta:
        model = Invoice_model
        fields = ('selbuy','rate')      
# class Invoice_form(forms.ModelForm):
#     class Meta:
#         model=Invoice_model
#         fields='__all__'
#         exclude=('user','date','date1','gst',)

class Customer_form(forms.ModelForm):
    class Meta:
        model=Customer
        fields='__all__'
        exclude=('user',)
       

class Seller_form(forms.ModelForm):
    class Meta:
        model=Seller
        fields='__all__'
        exclude=('user',)


class PurchaseBookForm(forms.ModelForm):
    # COMMENT_CHOICES = [
    #     ('Advance Received', 'Advance Received'),
    #     ('Balance Received', 'Balance Received'),
    #     ('Full Payment Received', 'Full Payment Received'),
    #     ('Other', 'Other'),
    # ]

    # comment = forms.ChoiceField(
    #     choices=COMMENT_CHOICES,
    #     required=False,
    #     widget=forms.Select(attrs={'id': 'id_comment'})
    # )

    class Meta:
        model = PurchaseBook
        fields = '__all__'
        exclude=('user',)

class SearchForm(forms.Form):
    datee = forms.DateField(
        label='Search Sale data by Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    datee1 = forms.DateField(
        label='Search Purchase data by Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    product = forms.ModelChoiceField(
        queryset=Add_item_model_sale.objects.all(),
        label='Product Sale',
        required=False
    )
    product_purch = forms.ModelChoiceField(
        queryset=Add_item_model_sale.objects.all(),
        label='Product Purchase',
        required=False
    )
    seller = forms.ModelChoiceField(
        queryset=Seller.objects.all(),
        label='Seller',
        required=False
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        label='Customer',
        required=False
    )
    billnumber = forms.CharField(
        label='Invoice Number',
        required=False
    )

class UploadFileForm(forms.Form):
    file = forms.FileField()
    
class ImageChoiceField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def option_label(self, choice):
        # This method is called to generate the label for each option
        # You can add your custom HTML here, for example, an image and text.
        product = choice
        return f'<img src="{product.image.url}" width="20" height="20" /> {product.name}'
        
    def create_option(self, name, value, label, attrs=None, selected=False, index=None, subindex=None):
        # Overriding to render custom HTML
        option = super().create_option(name, value, label, attrs, selected, index, subindex)
        option['label'] = label  # Modify label to include image HTML
        return option


# class ProductForm(forms.Form):
#     product = ImageChoiceField(queryset=Add_item_model.objects.all(), widget=forms.Select())


class TransportForm(forms.ModelForm):
    date_supply = forms.DateField(
        label='Date of Supply',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = Transportation
        fields = '__all__'
        exclude = ('user','bill',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class TransportForm1(forms.ModelForm):
    date_supply = forms.DateField(
        label='Date of Supply',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = Transportation
        fields = '__all__'
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

