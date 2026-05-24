from django.contrib import admin

from .models import Draw, Ticket, TicketResult


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_code", "buyer_name", "purchase_type", "numbers", "created_at")
    search_fields = ("ticket_code", "buyer_name")
    list_filter = ("purchase_type", "created_at")
    readonly_fields = ("ticket_code", "created_at")


@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    list_display = ("round_number", "winning_numbers", "bonus_number", "drawn_at")
    search_fields = ("round_number",)
    readonly_fields = ("drawn_at",)


@admin.register(TicketResult)
class TicketResultAdmin(admin.ModelAdmin):
    list_display = ("ticket", "draw", "rank", "match_count", "bonus_matched", "checked_at")
    list_filter = ("draw", "rank", "bonus_matched")
    search_fields = ("ticket__ticket_code", "ticket__buyer_name")
    readonly_fields = ("checked_at",)
