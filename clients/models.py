from django.db import models
from django.core.validators import MinLengthValidator

class registration(models.Model):
    clientid = models.AutoField(primary_key=True)
    firstname=models.CharField(max_length=50)
    lastname=models.CharField(max_length=50)
    contactno=models.CharField(max_length=10)
    gender=models.CharField(max_length=1)
    email=models.EmailField(unique=True,max_length=254)
    password=models.CharField(max_length=100,validators=[MinLengthValidator(8)])
    dateofbirth=models.DateField(verbose_name='date of birth')
    failed_attempts=models.IntegerField(default=0)
    lockout_time=models.DateTimeField(null=True,blank=True)
    

    def __str__(self):
        return self.email
    

class Room(models.Model):
    roomid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    roomdescription=models.TextField()
    updatetime=models.DateTimeField(auto_now=True,null=True)
    createdtime=models.DateTimeField(auto_now_add=True)
    clientid=models.ForeignKey(registration,on_delete=models.CASCADE)
    capacity = models.IntegerField(null=True, blank=True)
    participants=models.ManyToManyField(registration,related_name='participants')

    def __str__(self):
        return self.name
    
    def parcipants_count(self):
        return self.participants.count()
    



