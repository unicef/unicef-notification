from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    # url(r'^sample/', include('demo.sample.urls')),
    # url(r'^notification/', include('unicef_notification.urls')),
    url(r'^admin/', admin.site.urls),
]
