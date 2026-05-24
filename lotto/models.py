import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .lotto_utils import (
    evaluate_rank,
    generate_numbers,
    numbers_to_text,
    parse_numbers,
    text_to_numbers,
)


class Ticket(models.Model):
    MANUAL = "manual"
    AUTO = "auto"
    PURCHASE_TYPE_CHOICES = [
        (MANUAL, "수동"),
        (AUTO, "자동"),
    ]

    ticket_code = models.CharField("복권 번호", max_length=12, unique=True, blank=True)
    buyer_name = models.CharField("구매자", max_length=50)
    purchase_type = models.CharField("구매 방식", max_length=10, choices=PURCHASE_TYPE_CHOICES)
    numbers = models.CharField("선택 번호", max_length=30, blank=True)
    created_at = models.DateTimeField("구매 일시", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.purchase_type == self.AUTO and not self.numbers:
            self.numbers = numbers_to_text(generate_numbers())
        try:
            self.numbers = numbers_to_text(parse_numbers(self.numbers))
        except ValueError as exc:
            raise ValidationError({"numbers": str(exc)}) from exc

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = uuid.uuid4().hex[:12].upper()
        self.full_clean()
        super().save(*args, **kwargs)

    def number_list(self):
        return text_to_numbers(self.numbers)

    def get_absolute_url(self):
        return reverse("lotto:ticket_detail", args=[self.ticket_code])

    def __str__(self):
        return f"{self.ticket_code} - {self.buyer_name}"


class Draw(models.Model):
    round_number = models.PositiveIntegerField("회차", unique=True)
    winning_numbers = models.CharField("당첨 번호", max_length=30)
    bonus_number = models.PositiveIntegerField("보너스 번호")
    drawn_at = models.DateTimeField("추첨 일시", auto_now_add=True)

    class Meta:
        ordering = ["-round_number"]

    def clean(self):
        try:
            self.winning_numbers = numbers_to_text(parse_numbers(self.winning_numbers))
        except ValueError as exc:
            raise ValidationError({"winning_numbers": str(exc)}) from exc
        if self.bonus_number < 1 or self.bonus_number > 45:
            raise ValidationError({"bonus_number": "보너스 번호는 1부터 45 사이여야 합니다."})
        if self.bonus_number in self.number_list():
            raise ValidationError({"bonus_number": "보너스 번호는 당첨 번호와 중복될 수 없습니다."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def number_list(self):
        return text_to_numbers(self.winning_numbers)

    def create_results(self):
        results = []
        for ticket in Ticket.objects.all():
            rank, match_count, bonus_matched = evaluate_rank(
                ticket.number_list(),
                self.number_list(),
                self.bonus_number,
            )
            result, _ = TicketResult.objects.update_or_create(
                ticket=ticket,
                draw=self,
                defaults={
                    "rank": rank,
                    "match_count": match_count,
                    "bonus_matched": bonus_matched,
                },
            )
            results.append(result)
        return results

    def __str__(self):
        return f"{self.round_number}회차"


class TicketResult(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="results")
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE, related_name="results")
    rank = models.CharField("당첨 등수", max_length=10)
    match_count = models.PositiveIntegerField("일치 개수")
    bonus_matched = models.BooleanField("보너스 일치", default=False)
    checked_at = models.DateTimeField("확인 일시", auto_now=True)

    class Meta:
        unique_together = ("ticket", "draw")
        ordering = ["draw", "rank", "-match_count"]

    def __str__(self):
        return f"{self.ticket.ticket_code} / {self.draw.round_number}회차 / {self.rank}"
