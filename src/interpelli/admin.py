from django.contrib import admin

from django.utils import timezone


from .models import Interpello, Province


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["name", "active", "telegram_thread_id", "last_scraped_at"]
    list_editable = ["active"]
    list_filter = ["active"]
    search_fields = ["name"]
    readonly_fields = ["last_scraped_at", "created_at", "updated_at"]
    actions = ["activate_provinces", "deactivate_provinces"]


    @admin.action(description="Attiva le province selezionate", permissions=["change"])
    def activate_provinces(self, request, queryset):
        count = queryset.update(active=True, updated_at=timezone.now())
        self.message_user(request, f"Province attivate: {count}.")

    @admin.action(description="Disattiva le province selezionate", permissions=["change"])
    def deactivate_provinces(self, request, queryset):
        count = queryset.update(active=False, updated_at=timezone.now())
        self.message_user(request, f"Province disattivate: {count}.")


@admin.register(Interpello)
class InterpelloAdmin(admin.ModelAdmin):
    list_display = ["title", "province", "published_date", "notified", "notified_at"]
    list_filter = ["province", "notified"]
    search_fields = ["title", "description", "url"]
    list_select_related = ["province"]
    actions = ["mark_notified"]
    readonly_fields = [
        "notified", "notified_at", "telegram_message_id", "created_at", "updated_at",
    ]

    @admin.action(description="Segna come notificati gli interpelli selezionati", permissions=["change"])
    def mark_notified(self, request, queryset):
        count = queryset.filter(notified=False).update(
            notified=True, notified_at=timezone.now(),
        )
        self.message_user(request, f"Interpelli segnati come notificati: {count}.")
