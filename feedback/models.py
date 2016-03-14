from django.db import models
from polls.models import Question
from django.conf import settings

# Create your models here.
class Feedback(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	add_comment = models.BooleanField(default=0)
	template_name = models.CharField(max_length=20)
	def __str__(self):
		return self.question.question_text+"_"+self.template_name