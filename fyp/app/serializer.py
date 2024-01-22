from rest_framework import serializers
from .models import *

class ReactSerializer(serializers.ModelSerializer):
    model = Profile
    fields = ['risk_aversion', 'investment_time_period']