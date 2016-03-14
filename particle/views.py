from django.shortcuts import render
from login.views import BaseViewList,BaseViewDetail
from particle.models import Particle
# Create your views here.

class ParticleView(BaseViewList):
	context_object_name = 'particles'
	
	def get_template_names(self, **kwargs):
		template_name = 'particle/particle.html'
		return [template_name]

	def get_queryset(self):
		context = {}
		particleList = Particle.objects.order_by('-pub_date')
		primer = Particle.objects.filter(is_prime=1).latest()
		context['primer'] = primer
		featuredParticles = []
		for x in particleList:
			if x.is_featured == 1 and x != primer:
				featuredParticles.append(x)
				if len(featuredParticles) == 4:
					break
		featuredParticles1 = featuredParticles[:2]
		featuredParticles2 = featuredParticles[2:]
		context['featuredParticles'] = featuredParticles
		context['featuredParticles1'] = featuredParticles1
		context['featuredParticles2'] = featuredParticles2
		particleList = [x for x in particleList if x not in featuredParticles and x != primer]
		context['particles'] = particleList
		return context

class  ParticleDetailView(BaseViewDetail):
	model = Particle
	template_name = 'particle/particle-detail.html'

