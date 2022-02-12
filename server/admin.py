from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class KhaganateAdminSite(admin.AdminSite):
    site_header = "Khaganate admin"
    site_title = "Khaganate admin"


class KhaganateAdminConfig(AdminConfig):
    default_site = "server.admin.KhaganateAdminSite"
