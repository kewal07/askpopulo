from django.contrib import admin
from polls.models import Choice, Question,Vote,Subscriber,QuestionWithCategory,Survey,Survey_Question,SurveyVoted,VoteText,EmailTemplates, PollsReferred, SurveysReferred, UsersReferred, VoteApi
from django.conf import settings
from categories.models import Category

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class CategoryInline(admin.TabularInline):
    model = QuestionWithCategory
    extra = 5

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Add Question', {'fields': ['user','question_text','description','featuredPoll','privatePoll','que_slug','home_visible',]}),
        ('Date information', {'fields': ['pub_date','expiry'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline,CategoryInline]

admin.site.register(Choice)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
admin.site.register(Subscriber)
admin.site.register(Category)
admin.site.register(Survey)
admin.site.register(Survey_Question)
admin.site.register(SurveyVoted)
admin.site.register(VoteText)
admin.site.register(EmailTemplates)
admin.site.register(PollsReferred)
admin.site.register(SurveysReferred)
admin.site.register(UsersReferred)
admin.site.register(VoteApi)
