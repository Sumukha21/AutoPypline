import numpy as np


class ListIterator:
    def __init__(self, batch_size, input_iterator, sample_name=None):
        self.batch_size = batch_size
        self.input_iterator = input_iterator
        self.input_length = int(np.ceil(len(input_iterator) / batch_size))
        self.sample_name = sample_name

    def __call__(self, index):
        return [{"input": i} for i in self.input_iterator[index * self.batch_size: (index + 1) * self.batch_size]]
