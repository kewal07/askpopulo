from django.contrib import admin
from polls.models import Choice, Question,Vote,Subscriber
from django.conf import settings

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
	
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Add Question', {'fields': ['user','question_text','description']}),
        ('Date information', {'fields': ['pub_date','expiry'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
admin.site.register(Subscriber)