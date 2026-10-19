from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render
from django.contrib.admin import AdminSite

from .models import Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'response', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('message', 'response')
    ordering = ('-created_at',)


# Personnalisation de User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email')
    actions = ['deactivate_users', 'activate_users']

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "Activer les utilisateurs sélectionnés"


# Enregistrer la version personnalisée
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ChatbotAdminSite(AdminSite):
    site_header = "Administration du Chatbot"
    site_title = "Panneau d’administration"
    index_title = "Statistiques du Chatbot"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('stats/', self.admin_view(self.stats_view))
        ]
        return my_urls + urls

    def stats_view(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_messages = Chat.objects.count()

        context = dict(
            self.each_context(request),
            total_users=total_users,
            active_users=active_users,
            total_messages=total_messages
        )

        return render(request, "admin/chatbot_stats.html", context)