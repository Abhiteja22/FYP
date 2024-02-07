from django.db import models

# Create your models here.

class Chat(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()

    class Meta:
        db_table = "t_message"