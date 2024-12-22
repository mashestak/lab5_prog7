from rest_framework import serializers
from polls.models import Question

class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ['id', 'title', 'date_created', 'popularity']
