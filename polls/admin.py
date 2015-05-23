from django.contrib import admin
from polls.models import Choice, Question,Vote,Subscriber,QuestionWithCategory
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
        ('Add Question', {'fields': ['user','question_text','description']}),
        ('Date information', {'fields': ['pub_date','expiry'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline,CategoryInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
admin.site.register(Subscriber)
admin.site.register(Category)