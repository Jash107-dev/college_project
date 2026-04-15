from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),                      # django admin panel
    path('', include('accounts.urls')),                   # login logout
    path('employee/', include('employee.urls')),          # all employee and leave urls
]
