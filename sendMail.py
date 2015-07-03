import os

os.environ['DJANGO_SETTINGS_MODULE'] = "askpopulo.settings"

import polls.views

polls.views.sendFeed()
