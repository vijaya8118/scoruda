# Generated by Django 5.1.8 on 2025-06-08 14:30

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import django_tenants.postgresql_backend.base
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Add_item_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=100)),
                ('rate', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Selling rate')),
                ('rate_purch', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Purchase rate')),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema_name', models.CharField(db_index=True, max_length=63, unique=True, validators=[django_tenants.postgresql_backend.base._check_schema_name])),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('email', models.EmailField(max_length=255)),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('domain_url', models.CharField(blank=True, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='n/a', max_length=40, verbose_name='Name')),
                ('address', models.TextField(default='n/a', max_length=90, verbose_name='address')),
                ('phone', models.CharField(default='n/a', max_length=10, verbose_name='Phone Number')),
                ('gst', models.CharField(default='n/a', max_length=15, verbose_name='GST Number')),
                ('bank', models.CharField(default='n/a', max_length=20, verbose_name='Bank name')),
                ('account', models.CharField(default='n/a', max_length=20, verbose_name='Account Number')),
                ('ifsc', models.CharField(default='n/a', max_length=15, verbose_name='IFSC code')),
                ('due_date', models.CharField(default=0, help_text='Enter in days', max_length=5, verbose_name='Payment Duration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='n/a', max_length=40, verbose_name='Name')),
                ('address', models.TextField(default='n/a', max_length=90, verbose_name='address')),
                ('phone', models.CharField(default='n/a', max_length=10, verbose_name='Phone Number')),
                ('gst', models.CharField(default='n/a', max_length=15, verbose_name='GST Number')),
                ('bank', models.CharField(default='n/a', max_length=20, verbose_name='Bank name')),
                ('account', models.CharField(default='n/a', max_length=20, verbose_name='Account Number')),
                ('ifsc', models.CharField(default='n/a', max_length=15, verbose_name='IFSC code')),
                ('due_date', models.CharField(default=0, help_text='Enter in days', max_length=5, verbose_name='Payment Duration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SetupCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='n/a', max_length=40, verbose_name='Name')),
                ('address', models.TextField(default='n/a', max_length=90, verbose_name='address')),
                ('phone', models.CharField(default='n/a', max_length=10, verbose_name='Phone Number')),
                ('gst', models.CharField(default='n/a', max_length=15, verbose_name='GST Number')),
                ('bank', models.CharField(default='n/a', max_length=20, verbose_name='Bank name')),
                ('account', models.CharField(default='n/a', max_length=20, verbose_name='Account Number')),
                ('ifsc', models.CharField(default='n/a', max_length=15, verbose_name='IFSC code')),
                ('due_date', models.CharField(default=0, help_text='Enter in days', max_length=5, verbose_name='Payment Duration')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('phone_no', models.CharField(max_length=10)),
                ('role', models.CharField(blank=True, choices=[('manager', 'Manager'), ('admin', 'Admin'), ('employee', 'Employee')], default='admin', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CashBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('date1', models.DateField(auto_now_add=True, verbose_name='date')),
                ('amt', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Amount Paid')),
                ('mode', models.CharField(choices=[('cash', 'cash'), ('UPI', 'UPI')], default='cash', max_length=15, verbose_name=' mode')),
                ('comment', models.TextField(max_length=150, null=True, verbose_name='narration')),
                ('selbuy', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='scoapp.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(db_index=True, max_length=253, unique=True)),
                ('is_primary', models.BooleanField(db_index=True, default=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='scoapp.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice_model',
            fields=[
                ('num', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='Bill num')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date1', models.DateField(auto_now_add=True)),
                ('billnum', models.IntegerField(verbose_name='Bill Number')),
                ('mode', models.CharField(choices=[('cash', 'cash'), ('UPI', 'UPI'), ('credit', 'credit')], default='cash', max_length=15, verbose_name='Mode')),
                ('qty', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='quantity')),
                ('rate', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Rate')),
                ('amt', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Amt')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='item', to='scoapp.add_item_model', verbose_name='prod:')),
                ('selbuy', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='scoapp.customer')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date1', models.DateField(auto_now_add=True)),
                ('amt', models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Amount Paid')),
                ('mode', models.CharField(choices=[('cash', 'cash'), ('UPI', 'UPI')], default='cash', max_length=15, verbose_name=' mode')),
                ('comment', models.TextField(max_length=150, null=True, verbose_name='narration')),
                ('selbuy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='scoapp.seller')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase_model',
            fields=[
                ('num', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('date1', models.DateField(auto_now_add=True)),
                ('mode', models.CharField(blank=True, choices=[('cash', 'cash'), ('UPI', 'UPI'), ('credit', 'credit')], default='cash', max_length=15, null=True, verbose_name='Mode')),
                ('qty', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Quantity')),
                ('rate', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Rate')),
                ('amt', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Amt')),
                ('product', models.ForeignKey(default='name', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Product1:+', to='scoapp.add_item_model')),
                ('selbuy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='scoapp.seller')),
            ],
        ),
    ]
