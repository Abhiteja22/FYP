from django.contrib import admin
from .models import *
# Register your models here.
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")

class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "input", "output")

# Register your models here.
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)