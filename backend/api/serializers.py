from rest_framework import serializers
from .models import User, Subject, Mark

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        return user

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class MarkSerializer(serializers.ModelSerializer):
    grade = serializers.ReadOnlyField()

    class Meta:
        model = Mark
        fields = ['id', 'student', 'subject', 'score', 'grade']

    def validate(self, data):
        requesting_user = self.context['request'].user
        subject = data.get('subject')

        if requesting_user.role == User.Role.TEACHER:
            if subject.teacher != requesting_user:
                raise serializers.ValidationError(
                    "You are not assigned to this subject and cannot add marks for it."
                )
        return data

class ReportSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name')
    grade = serializers.ReadOnlyField()

    class Meta:
        model = Mark
        fields = ['subject', 'score', 'grade']

class StudentAnalyticsSerializer(serializers.ModelSerializer):
    average_score = serializers.FloatField()
    overall_grade = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score', 'overall_grade']

    def get_overall_grade(self, obj):
        average = obj.get('average_score') if isinstance(obj, dict) else obj.average_score
        
        if average is None: return 'N/A'
        if average >= 90: return 'A'
        elif average >= 80: return 'B'
        elif average >= 70: return 'C'
        elif average >= 60: return 'D'
        else: return 'F'