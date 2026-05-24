from random import sample


LOTTO_MIN = 1
LOTTO_MAX = 45
LOTTO_COUNT = 6


def generate_numbers():
    return sorted(sample(range(LOTTO_MIN, LOTTO_MAX + 1), LOTTO_COUNT))


def parse_numbers(value):
    if isinstance(value, (list, tuple)):
        numbers = [int(number) for number in value]
    else:
        normalized = str(value).replace(",", " ")
        numbers = [int(part) for part in normalized.split()]

    if len(numbers) != LOTTO_COUNT:
        raise ValueError("로또 번호는 6개여야 합니다.")
    if len(set(numbers)) != LOTTO_COUNT:
        raise ValueError("로또 번호는 중복될 수 없습니다.")
    if any(number < LOTTO_MIN or number > LOTTO_MAX for number in numbers):
        raise ValueError("로또 번호는 1부터 45 사이여야 합니다.")
    return sorted(numbers)


def numbers_to_text(numbers):
    return ",".join(str(number) for number in sorted(numbers))


def text_to_numbers(value):
    return parse_numbers(value)


def evaluate_rank(ticket_numbers, winning_numbers, bonus_number):
    matched = len(set(ticket_numbers) & set(winning_numbers))
    bonus_matched = bonus_number in ticket_numbers

    if matched == 6:
        return "1등", matched, bonus_matched
    if matched == 5 and bonus_matched:
        return "2등", matched, bonus_matched
    if matched == 5:
        return "3등", matched, bonus_matched
    if matched == 4:
        return "4등", matched, bonus_matched
    if matched == 3:
        return "5등", matched, bonus_matched
    return "낙첨", matched, bonus_matched
