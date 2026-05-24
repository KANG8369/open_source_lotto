from django.urls import path

from . import views


app_name = "lotto"

urlpatterns = [
    path("", views.home, name="home"),
    path("purchase/", views.purchase_ticket, name="purchase_ticket"),
    path("ticket/<str:ticket_code>/", views.ticket_detail, name="ticket_detail"),
    path("check/", views.check_ticket, name="check_ticket"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/draw/", views.create_draw, name="create_draw"),
    path("staff/draw/<int:draw_id>/", views.draw_detail, name="draw_detail"),
]
