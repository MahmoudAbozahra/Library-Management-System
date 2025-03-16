from django.db import models

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name



class Books(models.Model):
    
    book_status=[
        ('sold','sold'),
        ('availble','availble'),
        ('rental','rental'),
    ]
    
    
    title= models.CharField(max_length=250 , default='boooook')
    author= models.CharField(max_length=250 , null=True , blank=True, default='MAHMOzz')
    photo_book=models.ImageField(upload_to='photos' ,null=True , blank=True)
    photo_author= models.ImageField(upload_to='photos' ,null=True , blank=True)
    pages=models.IntegerField(null=True,blank=True , default=300)
    price=models.DecimalField(max_digits=5 ,decimal_places=2 , null=True ,blank=True , default=500)
    retal_price_day=models.DecimalField(null=True , blank=True,max_digits=5, decimal_places=2 , default=4.5)
    retal_period=models.IntegerField(null=True , blank=True ,default=8)
    total_rental =models.DecimalField(max_digits=5 ,decimal_places=2 , null=True ,blank=True ) 
    active=models.BooleanField(default=True)
    status=models.CharField(max_length=50, choices=book_status,null=True,blank=True , default='availble')
    category=models.ForeignKey(Category,on_delete=models.PROTECT,null=True,blank=True)
    
    class Meta:
        permissions = [
            ("can_view_books", "Can view books"),
            ("can_change_book_status", "Can change book status"),
        ]
    
    def __str__(self):
        return self.title
    
    
    
