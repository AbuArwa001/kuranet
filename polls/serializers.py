from rest_framework import serializers
from .models import Poll, PollOption, Vote
from users.serializers import UserSerializer

class PollOptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PollOption
        fields = ['id', 'text', 'vote_count']
    
    def get_vote_count(self, obj):
        # return obj.votes.count()
        # Assuming Vote model has a ForeignKey to PollOption
        return obj.vote_set.count()  

class VoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'user', 'voted_at']

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True)
    user = UserSerializer(read_only=True)
    votes = VoteSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'id', 'user', 'title', 'description', 
            'created_at', 'closes_at', 'status', 
            'options', 'votes'
        ]
    def create(self, validated_data):
        # Extract the options data from the validated data
        options_data = validated_data.pop('options')
        
        # Create the Poll instance first
        poll = Poll.objects.create(**validated_data)
        
        # Iterate over the options data and create PollOption instances
        for option_data in options_data:
            PollOption.objects.create(poll=poll, **option_data)
            
        return poll
class PollOptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['text']