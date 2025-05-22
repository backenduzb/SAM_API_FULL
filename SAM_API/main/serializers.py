from .models import TeacherUsersStats, TeacherTopic
from rest_framework import serializers
from django.core.validators import MinValueValidator

__all__ = [
    'TeacherUsersStatsSerializer',
    'TeacherEditSerializer',
    'TopicsSerializer',
    'TopicedTeachersSerializer',
    'TeacherTopicSerializer'
]


class TeacherTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTopic
        fields = ['topic_name']


class TeacherUsersStatsSerializer(serializers.ModelSerializer):
    topic_name = TeacherTopicSerializer(source='topic', many=True, read_only=True)
    
    class Meta:
        model = TeacherUsersStats
        fields = [
            'juda_ham_qoniqaman', 
            'ortacha_qoniqaman', 
            'asosan_qoniqaman', 
            'qoniqmayman', 
            'umuman_qoniqaman', 
            'updated_at', 
            'topic_name'
        ]


class TopicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTopic
        fields = ['topic_name']

class TopicedTeachersSerializer(serializers.ModelSerializer):
    topics = TeacherTopicSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherUsersStats
        fields = ["id", "full_name", "topics", "telegram_id"]


class TeacherEditSerializer(serializers.ModelSerializer):
    juda_ham_qoniqaman = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    ortacha_qoniqaman = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    asosan_qoniqaman = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    qoniqmayman = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])
    umuman_qoniqaman = serializers.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        model = TeacherUsersStats
        fields = [
            'juda_ham_qoniqaman',
            'ortacha_qoniqaman',
            'asosan_qoniqaman',
            'qoniqmayman',
            'umuman_qoniqaman'
        ]

    def validate(self, data):
        total = (
            data.get('juda_ham_qoniqaman', 0) +
            data.get('ortacha_qoniqaman', 0) +
            data.get('asosan_qoniqaman', 0) +
            data.get('qoniqmayman', 0) +
            data.get('umuman_qoniqaman', 0)
        )
        # Agar xohlasangiz, shu yerda total uchun validatsiya qo'shishingiz mumkin
        return data
