import os

os.environ['DJANGO_SETTINGS_MODULE'] = "askpopulo.settings"

import sendFeed

sendFeed.sendFeed()


