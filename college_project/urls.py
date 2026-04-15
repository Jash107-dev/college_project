from django.contrib import admin
from django.urls import path, include

# main url config - all apps are included here
urlpatterns = [
    path('admin/', admin.site.urls),       # django default admin panel
    path('', include('accounts.urls')),    # login logout home
    path('employee/', include('employee.urls')),  # all employee related urls
]
