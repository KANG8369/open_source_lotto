from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import DrawForm, TicketCheckForm, TicketPurchaseForm
from .models import Draw, Ticket, TicketResult


def home(request):
    latest_draw = Draw.objects.first()
    recent_tickets = Ticket.objects.all()[:5]
    return render(
        request,
        "lotto/home.html",
        {
            "purchase_form": TicketPurchaseForm(initial={"purchase_type": Ticket.AUTO}),
            "check_form": TicketCheckForm(),
            "latest_draw": latest_draw,
            "recent_tickets": recent_tickets,
        },
    )


@require_http_methods(["POST"])
def purchase_ticket(request):
    form = TicketPurchaseForm(request.POST)
    if form.is_valid():
        ticket = form.save()
        messages.success(request, "복권 구매가 완료되었습니다.")
        return redirect(ticket)
    latest_draw = Draw.objects.first()
    return render(
        request,
        "lotto/home.html",
        {
            "purchase_form": form,
            "check_form": TicketCheckForm(),
            "latest_draw": latest_draw,
            "recent_tickets": Ticket.objects.all()[:5],
        },
        status=400,
    )


def ticket_detail(request, ticket_code):
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code.upper())
    results = ticket.results.select_related("draw").order_by("-draw__round_number")
    latest_result = results.first()
    return render(
        request,
        "lotto/ticket_detail.html",
        {
            "ticket": ticket,
            "latest_result": latest_result,
            "results": results,
        },
    )


@require_http_methods(["POST"])
def check_ticket(request):
    form = TicketCheckForm(request.POST)
    if form.is_valid():
        return redirect("lotto:ticket_detail", ticket_code=form.cleaned_data["ticket_code"].upper())
    messages.error(request, "복권 번호를 확인해 주세요.")
    return redirect("lotto:home")


@staff_member_required
def staff_dashboard(request):
    tickets = Ticket.objects.all()
    draws = Draw.objects.all()
    results = TicketResult.objects.select_related("ticket", "draw")[:20]
    sales_count = tickets.count()
    manual_count = tickets.filter(purchase_type=Ticket.MANUAL).count()
    auto_count = tickets.filter(purchase_type=Ticket.AUTO).count()
    return render(
        request,
        "lotto/staff_dashboard.html",
        {
            "tickets": tickets[:30],
            "draws": draws,
            "results": results,
            "sales_count": sales_count,
            "manual_count": manual_count,
            "auto_count": auto_count,
        },
    )


@staff_member_required
def create_draw(request):
    if request.method == "POST":
        form = DrawForm(request.POST)
        if form.is_valid():
            draw = form.save()
            draw.create_results()
            messages.success(request, f"{draw.round_number}회차 추첨과 당첨 확인이 완료되었습니다.")
            return redirect("lotto:draw_detail", draw_id=draw.id)
    else:
        next_round = (Draw.objects.order_by("-round_number").first().round_number + 1) if Draw.objects.exists() else 1
        form = DrawForm(initial={"round_number": next_round})
    return render(request, "lotto/create_draw.html", {"form": form})


@staff_member_required
def draw_detail(request, draw_id):
    draw = get_object_or_404(Draw, id=draw_id)
    results = draw.results.select_related("ticket")
    summary = {
        rank: results.filter(rank=rank).count()
        for rank in ["1등", "2등", "3등", "4등", "5등", "낙첨"]
    }
    return render(
        request,
        "lotto/draw_detail.html",
        {
            "draw": draw,
            "results": results,
            "summary": summary,
        },
    )
