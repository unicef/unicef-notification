from django.contrib import admin
from django.urls import re_path

urlpatterns = [
    # re_path(r'^sample/', include('demo.sample.urls')),
    # re_path(r'^notification/', include('unicef_notification.urls')),
    re_path(r'^admin/', admin.site.urls),
]
