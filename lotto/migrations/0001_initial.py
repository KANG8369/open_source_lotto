# Generated for the Open Source Lotto assignment.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Draw",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("round_number", models.PositiveIntegerField(unique=True, verbose_name="회차")),
                ("winning_numbers", models.CharField(max_length=30, verbose_name="당첨 번호")),
                ("bonus_number", models.PositiveIntegerField(verbose_name="보너스 번호")),
                ("drawn_at", models.DateTimeField(auto_now_add=True, verbose_name="추첨 일시")),
            ],
            options={
                "ordering": ["-round_number"],
            },
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ticket_code", models.CharField(blank=True, max_length=12, unique=True, verbose_name="복권 번호")),
                ("buyer_name", models.CharField(max_length=50, verbose_name="구매자")),
                (
                    "purchase_type",
                    models.CharField(
                        choices=[("manual", "수동"), ("auto", "자동")],
                        max_length=10,
                        verbose_name="구매 방식",
                    ),
                ),
                ("numbers", models.CharField(blank=True, max_length=30, verbose_name="선택 번호")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="구매 일시")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TicketResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rank", models.CharField(max_length=10, verbose_name="당첨 등수")),
                ("match_count", models.PositiveIntegerField(verbose_name="일치 개수")),
                ("bonus_matched", models.BooleanField(default=False, verbose_name="보너스 일치")),
                ("checked_at", models.DateTimeField(auto_now=True, verbose_name="확인 일시")),
                (
                    "draw",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="lotto.draw",
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="lotto.ticket",
                    ),
                ),
            ],
            options={
                "ordering": ["draw", "rank", "-match_count"],
                "unique_together": {("ticket", "draw")},
            },
        ),
    ]
