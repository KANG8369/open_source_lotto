from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import TicketPurchaseForm
from .models import Draw, Ticket


class LottoModelTests(TestCase):
    def test_auto_ticket_generates_six_numbers(self):
        ticket = Ticket.objects.create(buyer_name="Kim", purchase_type=Ticket.AUTO, numbers="")

        self.assertEqual(len(ticket.number_list()), 6)
        self.assertTrue(all(1 <= number <= 45 for number in ticket.number_list()))

    def test_draw_creates_first_rank_result(self):
        ticket = Ticket.objects.create(
            buyer_name="Lee",
            purchase_type=Ticket.MANUAL,
            numbers="1,2,3,4,5,6",
        )
        draw = Draw.objects.create(round_number=1, winning_numbers="1,2,3,4,5,6", bonus_number=7)

        draw.create_results()
        result = ticket.results.get(draw=draw)

        self.assertEqual(result.rank, "1등")
        self.assertEqual(result.match_count, 6)


class LottoFormTests(TestCase):
    def test_manual_form_rejects_duplicate_numbers(self):
        form = TicketPurchaseForm(
            data={
                "buyer_name": "Park",
                "purchase_type": Ticket.MANUAL,
                "manual_numbers": "1 1 2 3 4 5",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("manual_numbers", form.errors)


class LottoViewTests(TestCase):
    def test_purchase_manual_ticket(self):
        response = self.client.post(
            reverse("lotto:purchase_ticket"),
            {
                "buyer_name": "Choi",
                "purchase_type": Ticket.MANUAL,
                "manual_numbers": "3 11 18 24 32 41",
            },
        )

        ticket = Ticket.objects.get(buyer_name="Choi")
        self.assertRedirects(response, ticket.get_absolute_url())
        self.assertEqual(ticket.numbers, "3,11,18,24,32,41")

    def test_staff_draw_requires_login(self):
        response = self.client.get(reverse("lotto:create_draw"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_staff_can_create_draw(self):
        User.objects.create_superuser("admin", "admin@example.com", "pass12345")
        self.client.login(username="admin", password="pass12345")
        Ticket.objects.create(buyer_name="Han", purchase_type=Ticket.MANUAL, numbers="1,2,3,4,5,6")

        response = self.client.post(
            reverse("lotto:create_draw"),
            {
                "round_number": 1,
                "winning_numbers": "1 2 3 4 5 6",
                "bonus_number": 7,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Draw.objects.count(), 1)
        self.assertEqual(Draw.objects.first().results.count(), 1)
