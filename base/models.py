from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField( max_length=200)
    
    def __str__(self):
        return self.name
    
    


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)      #A room has only one topic
    name = models.CharField( max_length=200)                #max_length()is required for charfield
    description = models.TextField(null=True, blank=True)   #null=true means it can be blank, blank=True not compulsory
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated', '-created']  #Ordering per time posted
    
    
    def __str__(self):
        return self.name
        #return str(self.name)
        
# Difference between auto_now and auto_now_add:
#     auto_now : Takes a snapshot on every time we save the item
#     auto_now_add : Only takes a time stamp when we first save or create the instance
   
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # One to many relationship
    #Creating a one to many relattionship , specify the attributes
    # room = models.ForeignKey(Room, on_delete=models.SET_NULL) -- If a room gets deleted all the messages stay in the db
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # All messages will be deleted from the db
    body = models.TextField() 
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['-updated', '-created']  #Ordering per time posted

    
    def __str__(self):
        return self.body[0:50] #The first characters in preview
    
    
    
    

