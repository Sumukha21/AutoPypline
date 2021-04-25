import math
from test_scripts.random_generators import random_value_generator_seedless


def encode_value(input_value):
    return int((input_value ** 2) / 10)


def decode_value(input_value):
    return math.ceil(math.sqrt(input_value * 10))


def remove_negative_value(input_value):
    if input_value > 0:
        return input_value
    return 0


def insert_dummy_values_on_both_sides(input_value):
    input_value = [input_value]
    start_value = random_value_generator_seedless()
    end_value = random_value_generator_seedless()
    input_value.insert(0, start_value)
    input_value.append(end_value)
    return input_value


def remove_dummy_values_on_both_sides(input_val):
    return input_val[1:-1]
