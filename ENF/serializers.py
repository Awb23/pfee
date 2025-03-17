from rest_framework import serializers
from .models import User, LettersProgress, WordsProgress, Reward

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'age']

class LettersProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LettersProgress
        fields = '__all__'

class WordsProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordsProgress
        fields = '__all__'

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'