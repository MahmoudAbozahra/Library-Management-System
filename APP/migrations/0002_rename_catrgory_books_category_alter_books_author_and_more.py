# Generated by Django 5.1.5 on 2025-02-06 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APP', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='books',
            old_name='catrgory',
            new_name='category',
        ),
        migrations.AlterField(
            model_name='books',
            name='author',
            field=models.CharField(blank=True, default='MAHMOzz', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='pages',
            field=models.IntegerField(blank=True, default=300, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=500, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='retal_period',
            field=models.IntegerField(blank=True, default=8, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='retal_price_day',
            field=models.DecimalField(blank=True, decimal_places=2, default=4.5, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='status',
            field=models.CharField(blank=True, choices=[('sold', 'sold'), ('availble', 'availble'), ('rental', 'rental')], default='availble', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='books',
            name='title',
            field=models.CharField(default='boooook', max_length=250),
        ),
    ]
