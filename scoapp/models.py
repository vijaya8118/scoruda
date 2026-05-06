from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

#################################

class Members(AbstractUser):
    username = models.CharField(max_length = 50, blank = False, null = False, unique = True)
    email = models.EmailField(_('email address'), unique = True)
    phone_no = models.CharField(max_length = 10)
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, default='admin') 

    def __str__(self):
        return self.username
    
#############################
class Common_InfoShop(models.Model):
    name=models.CharField('Name',max_length=40,default='',null=True)
    address=models.TextField('address',max_length=90,default='',null=True)
    phone=models.CharField('Phone Number',max_length=10,default='',null=True)
    gst=models.CharField('GST Number',max_length=15,default='',null=True)
    bank = models.CharField('Bank name',max_length=20,default='',null=True)
    account = models.CharField('Account Number',max_length=20,default='',null=True)
    ifsc = models.CharField('IFSC code',max_length=15,default='',null=True)
    due_date = models.CharField('Payment Duration', max_length=5,default=0,help_text='Enter in days',null=True)
    user = models.ForeignKey(Members,on_delete=models.DO_NOTHING,null=True)
    class Meta:
        abstract=True

    def __str__(self):
        return self.name
############### USER REGISTRATION ###########################
class Client(TenantMixin):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255)  # Email field
    contact_number = models.CharField(max_length=15, blank=True, null=True)  # Contact number (can store numbers and optional)
    auto_create_schema = True
    domain_url = models.CharField(max_length=255, unique=True, blank=True)

    BASE_DOMAIN = "domain.com"  # Change this to your actual domain

    def generate_unique_domain_url(self):
        base_slug = slugify(self.name)
        domain_candidate = f"{base_slug}.{self.BASE_DOMAIN}"
        suffix = 1

        # Ensure uniqueness by checking existing domain_urls
        while Client.objects.filter(domain_url=domain_candidate).exclude(pk=self.pk).exists():
            domain_candidate = f"{base_slug}-{suffix}.{self.BASE_DOMAIN}"
            suffix += 1

        return domain_candidate

    def save(self, *args, **kwargs):
        if not self.domain_url:
            self.domain_url = self.generate_unique_domain_url()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
  
class Domain(DomainMixin):
    pass


################## models ####################

class SetupCompany(Common_InfoShop):
    STATUS = (
        ('0',_('GST Exempted')),
        ('5',_('5%')),
        ('24',_('24%')),
        ('18',_('18%')),
    )
    gsttype=models.CharField('Gst Type',max_length=50,null=True,choices=STATUS,default='Essential Goods')
    

    def __str__(self):
        return self.name
 
#########################################################################################################
# class Add_item_model(models.Model):
#     product=models.CharField(max_length=100)
#     rate = models.DecimalField('Purchased rate',decimal_places=2,max_digits=10,null=False,default=0)
#     image = models.ImageField(null=True, blank=True)

#     def __str__(self):
#         return self.product
    
# class Add_item_model(models.Model):
#     product=models.CharField(max_length=100)
#     rate = models.DecimalField('Selling rate',decimal_places=2,max_digits=10,null=False,default=0)
#     image = models.ImageField(null=True, blank=True)

#     def __str__(self):
#         return self.product
    
class Add_item_model(models.Model):
    class ProductType(models.TextChoices):
        PURCHASE_ONLY = 'purchase_only', 'Purchase Only'
        SALE_ONLY     = 'sale_only',     'Sale Only'
        BOTH          = 'both',          'Both'

    product          = models.CharField(max_length=100)
    product_type  = models.CharField(max_length=20, choices=ProductType.choices, default=ProductType.BOTH)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_rate     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image         = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.product
    
#########################################################################################################
class Customer(Common_InfoShop):
    def __str__(self):
        return self.name
    
class Seller(Common_InfoShop):
    def __str__(self):
        return self.name

class Offer(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    date1=models.DateField(auto_now_add=True)
    class OfferType(models.TextChoices):
        PERC_BILL = 'perc_bill', 'Percentage deducted on Bill'
        AMT_BILL     = 'amt_bill',     'Amount deducted on Bill'
        PERC_PROD          = 'perc_prod',          'Percentage deducted on Product'
        AMT_PROD = 'amt_prod', 'Amount deducted on Product'
        BUY_GET = 'buy_get', 'Buy One Get One'

    offer_type = models.CharField(max_length=20, choices=OfferType.choices, default=OfferType.PERC_BILL)

    offer_name = models.CharField('Offer Name', max_length=50, null=False, blank=False)
    valid_till = models.DateField('Valid Till', null=False, blank=False)
    product = models.ForeignKey(
    Add_item_model,
    on_delete=models.DO_NOTHING,
    null=True,
    blank=True,
    limit_choices_to={
        'product_type__in': [
            Add_item_model.ProductType.SALE_ONLY,
            Add_item_model.ProductType.BOTH
        ]
    }
)
    val  = models.DecimalField('Discount Value', decimal_places=2, max_digits=10, null=False, default=0)

    buyOne = models.CharField('Buy How many Product', max_length=50, null=True, blank=True)
    getOne = models.CharField('Get How many Product', max_length=50, null=True, blank=True)
    def __str__(self):
        return self.offer_name


class Purchase_model(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    date1=models.DateField(auto_now_add=True)
    selbuy = models.ForeignKey(Seller,on_delete=models.DO_NOTHING,null=True)
    num=models.AutoField(auto_created = True,primary_key = True,serialize = False, verbose_name ='Bill num')
    billnum= models.IntegerField("Bill Number",null=True)
    
    STATUS = (
        ('cash',_('cash')),
        ('Bank',_('Bank')),
        ('credit',_('credit')),

    )
    mode=models.CharField('Mode',max_length=15,null=True,choices=STATUS,blank=True)
    ####
    product=models.ForeignKey(Add_item_model,on_delete=models.DO_NOTHING,null=True,related_name="Product1:+",default='name')
    qty = models.DecimalField('Quantity',decimal_places=2,max_digits=10,null=False,default=0)
    rate = models.DecimalField('Rate',decimal_places=2,max_digits=10,null=False,default=0)
    gst = models.DecimalField("GST",null=False,max_digits=10,decimal_places=2,default=0)

    amt = models.DecimalField("Amt",null=False,max_digits=10,decimal_places=2,default=0)
    user = models.ForeignKey(Members,on_delete=models.DO_NOTHING,null=True)

    def __str__(self):
        return str(self.billnum)


class PurchaseBook(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    date1=models.DateField(auto_now_add=True)
    selbuy = models.ForeignKey(Seller,on_delete=models.DO_NOTHING,null=True)

    amt= models.DecimalField('Amount Paid',null=False,max_digits=10,decimal_places=2,default=0)

    STATUS = (
        ('cash',_('cash')),
        ('Bank',_('Bank')),
    )
    mode=models.CharField(' mode',max_length=15,null=False,choices=STATUS,default='cash')
    DROP_CHOICES = [
        ('Advance Paid', 'Advance Paid'),
        ('Balance Paid', 'Balance Paid'),
        ('Full Payment', 'Full Payment'),
        ('Cash in Hand', 'Cash in Hand'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Other', 'Other'),
    ]
    comment = models.TextField("narration",choices=DROP_CHOICES,max_length=150,null=True)
    user = models.ForeignKey(Members,on_delete=models.DO_NOTHING,null=True)


class CashBook(models.Model):
    date = models.DateTimeField("Date",auto_now_add=True)
    date1=models.DateField( 'date',auto_now_add=True)
    selbuy = models.ForeignKey(Customer,on_delete=models.DO_NOTHING,null=False,blank=False)

    amt= models.DecimalField('Amount Paid',null=False,max_digits=10,decimal_places=2,default=0)

    STATUS = (
        ('cash',_('cash')),
        ('Bank',_('Bank')),
    )
    mode=models.CharField(' mode',max_length=15,null=False,choices=STATUS,default='cash')
    DROP_CHOICES = [
        ('Advance Paid', 'Advance Paid'),
        ('Balance Paid', 'Balance Paid'),
        ('Full Payment', 'Full Payment'),
        ('Cash in Hand', 'Cash in Hand'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Other', 'Other'),
    ]
    comment = models.TextField("narration",choices=DROP_CHOICES,max_length=150,null=True)
    user = models.ForeignKey(Members,on_delete=models.DO_NOTHING,null=True)

class Invoice_model(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    date1=models.DateField(auto_now_add=True)
    selbuy = models.ForeignKey(Customer,on_delete=models.DO_NOTHING,null=False,blank=False)
    num=models.AutoField(auto_created = True,primary_key = True,serialize = False, verbose_name ='Bill num')
    billnum= models.IntegerField("Bill Number",null=True)
    STATUS = (
        ('cash',_('cash')),
        ('Bank',_('Bank')),
        ('credit',_('credit')),

    )
    mode=models.CharField('Mode',max_length=15,null=False,blank=False,choices=STATUS)
    ####
    product=models.ForeignKey(Add_item_model,related_name='item',on_delete=models.DO_NOTHING,null=True,blank=False,verbose_name="prod:")
    qty = models.DecimalField('quantity',decimal_places=2,max_digits=10,null=False,default=0)
    rate = models.DecimalField("Rate",null=False,max_digits=10,decimal_places=2,default=0)
    gst = models.DecimalField("GST",null=False,max_digits=10,decimal_places=2,default=0)
    amt = models.DecimalField("Amt",null=False,max_digits=10,decimal_places=2,default=0)

    ###
    transport_amt = models.DecimalField("Transportation Amt",null=False,max_digits=10,decimal_places=2,default=0)
    offer= models.ForeignKey(Offer,on_delete=models.DO_NOTHING,null=True,blank=True)
    user = models.ForeignKey(Members,on_delete=models.DO_NOTHING,null=True)

    def __str__(self):
        return str(self.billnum)

class Transportation(models.Model):
    date=models.DateTimeField(auto_now_add=True)
    date1=models.DateField(auto_now_add=True)
    receipt_num = models.CharField('Receipt Number', max_length=50, unique=True, null=False, blank=False)
    vehicle_no = models.CharField('Vehicle Number', max_length=20, null=False, blank=False)
    bill = models.ForeignKey(Invoice_model,on_delete=models.DO_NOTHING,null=True,blank=True)
    purchase = models.ForeignKey(Purchase_model ,on_delete=models.DO_NOTHING,null=True,blank=True)
    def __str__(self):
        return self.receipt_num
    
