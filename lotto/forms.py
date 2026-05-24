from django import forms

from .lotto_utils import generate_numbers, numbers_to_text, parse_numbers
from .models import Draw, Ticket


class TicketPurchaseForm(forms.ModelForm):
    purchase_type = forms.ChoiceField(
        label="구매 방식",
        choices=Ticket.PURCHASE_TYPE_CHOICES,
        widget=forms.RadioSelect,
    )
    manual_numbers = forms.CharField(
        label="수동 번호",
        required=False,
        help_text="예: 3 11 18 24 32 41 또는 3,11,18,24,32,41",
    )
    numbers = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Ticket
        fields = ["buyer_name", "purchase_type", "numbers"]
        widgets = {
            "purchase_type": forms.RadioSelect,
        }

    def clean(self):
        cleaned_data = super().clean()
        purchase_type = cleaned_data.get("purchase_type")
        manual_numbers = cleaned_data.get("manual_numbers")

        if purchase_type == Ticket.MANUAL:
            if not manual_numbers:
                self.add_error("manual_numbers", "수동 구매는 번호 6개를 입력해야 합니다.")
            else:
                try:
                    cleaned_data["numbers"] = numbers_to_text(parse_numbers(manual_numbers))
                except ValueError as exc:
                    self.add_error("manual_numbers", str(exc))
        elif purchase_type == Ticket.AUTO:
            cleaned_data["numbers"] = numbers_to_text(generate_numbers())
        if cleaned_data.get("numbers"):
            self.instance.numbers = cleaned_data["numbers"]
        return cleaned_data

    def save(self, commit=True):
        ticket = super().save(commit=False)
        ticket.numbers = self.cleaned_data["numbers"]
        if commit:
            ticket.save()
        return ticket


class TicketCheckForm(forms.Form):
    ticket_code = forms.CharField(label="복권 번호", max_length=12)


class DrawForm(forms.ModelForm):
    class Meta:
        model = Draw
        fields = ["round_number", "winning_numbers", "bonus_number"]
        help_texts = {
            "winning_numbers": "예: 1 7 13 21 35 44",
            "bonus_number": "당첨 번호와 겹치지 않는 1~45 번호",
        }
