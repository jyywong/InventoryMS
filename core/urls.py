# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),    
    path("api/", include("api.urls")),    
    path("", include("authentication.urls")),
    path("", include('inventory.urls')), # Auth routes - login / register
    # path("", include("app.urls")),

                 # UI Kits Html files
]
