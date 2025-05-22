from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import TeacherUsersStats, TeacherTopic
from .filters import CustomUpdatedAtFilter

admin.site.unregister(User)
admin.site.unregister(Group)

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'updated_at', 'get_topics', 
        'juda_ham_qoniqaman', 'ortacha_qoniqaman',
        'asosan_qoniqaman', 'qoniqmayman', 'umuman_qoniqaman',
        'telegram_id'
    )
    list_filter = ('full_name', CustomUpdatedAtFilter)
    change_list_template = 'teacherusersstats_change_list.html'

    def get_topics(self, obj):
        return ", ".join([t.topic_name for t in obj.topics.all()])
    get_topics.short_description = "Fanlar"  

admin.site.register(TeacherUsersStats, UserAdmin)


@admin.register(TeacherTopic)
class TeacherTopicAdmin(admin.ModelAdmin):
    list_display = ('topic_name',)
    list_filter = ('topic_name',)
    search_fields = ('topic_name',)

