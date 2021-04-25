import random


def random_number_generator(start_value, end_value, no_elements):
    return [random.randint(start_value, end_value) for i in range(no_elements)]


def random_number_generator2(start_value, end_value, no_elements):
    a = [{"input_%d" % i: random.randint(start_value, end_value)} for i in range(no_elements)]
    b = {}
    for i in a:
        b = {**b, **i}
    return b


def random_value_generator(seed_value):
    return random.randint(-seed_value, seed_value)


def random_value_generator_seedless():
    return random.randint(1, 200)
