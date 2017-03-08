import fileinput

ALL_DIGITS = set(range(10))
OUTPUT_LINE_PATTERN = 'Case #{case_number}: {result}'
NUMBER_OF_TEST_CASES_DOMAIN = range(1, 101)
CHOSEN_NUMBERS_DOMAIN = range(0, 201)


def positive_integer_digits(integer, base=10):
    while integer > 0:
        yield integer % 10
        integer //= 10


def bleatrix_trotter_number(chosen_number):
    if chosen_number == 0:
        last_number_named = None
    else:
        last_number_named = 0
        digits_seen = set()
        while digits_seen != ALL_DIGITS:
            last_number_named += chosen_number
            digits_seen.update(positive_integer_digits(last_number_named))
    return last_number_named


std_input = fileinput.input()
number_of_test_cases = int(std_input.readline())

# Validate number of test cases
if number_of_test_cases not in NUMBER_OF_TEST_CASES_DOMAIN:
    raise Exception('Number of test cases {number} out of {domain}'.format(
        number=number_of_test_cases,
        domain=NUMBER_OF_TEST_CASES_DOMAIN
    ))

for case_number in range(1, number_of_test_cases + 1):
    chosen_number = int(std_input.readline())

    # Validate chosen number
    if chosen_number not in CHOSEN_NUMBERS_DOMAIN:
        raise Exception('Chosen number {number} out of {domain}'.format(
            number=chosen_number,
            domain=CHOSEN_NUMBERS_DOMAIN
        ))

    result = bleatrix_trotter_number(chosen_number) or 'INSOMNIA'
    print(OUTPUT_LINE_PATTERN.format(case_number=case_number, result=result))
