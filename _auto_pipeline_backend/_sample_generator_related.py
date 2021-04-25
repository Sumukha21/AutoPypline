import math
from Utils.utils import file_reader, pickle_reader, csv_reader


class AutomatedGenerator:
    def __init__(self, batch_size, iterator_dict=None, paths_to_files_containing_iterator_dict=None):
        self.iterators = dict()
        if paths_to_files_containing_iterator_dict is not None:
            for iterator_name, file_path in paths_to_files_containing_iterator_dict.items():
                iterator = self.file_reader(file_path)
                self.iterators[iterator_name] = assign_generator(iterator, iterator_name, batch_size)
        if iterator_dict is not None:
            for iterator_name, iterator in iterator_dict.items():
                self.iterators[iterator_name] = assign_generator(iterator, iterator_name, batch_size)

    def __len__(self):
        return int(math.ceil(self.iterators[list(self.iterators.keys())[0]].__len__()))

    def __call__(self, batch_id):
        batch_inputs = []
        for iterator_name, generator in self.iterators.items():
            batch_inputs.append(generator(batch_id))
        batch_inputs_final = []
        for i in range(len(batch_inputs[0])):
            batch_input = {}
            for j in range(len(batch_inputs)):
                for key, value in batch_inputs[j][i].items():
                    batch_input[key] = value
            batch_inputs_final.append(batch_input)
        return batch_inputs_final

    @staticmethod
    def file_reader(file_path):
        if file_path.endswith(".txt"):
            return file_reader(file_path)
        elif file_path.endswith(".pckl") or file_path.endswith(".pickle"):
            return pickle_reader(file_path)
        elif file_path.endswith(".csv"):
            return csv_reader(file_path)
        else:
            raise NotImplementedError("Currently only text, pickle and csv files are supported."
                                      " Provided path: ", file_path)


def assign_generator(iterator, iterator_key, batch_size):
    if isinstance(iterator, dict):
        return D(iterator_key, iterator, batch_size)
    elif isinstance(iterator, list) or isinstance(iterator, tuple):
        return LT(iterator_key, iterator, batch_size)


class LT:
    def __init__(self, iterator_key, iterator, batch_size):
        self.iterator = iterator
        self.iterator_key = iterator_key
        self.batch_size = batch_size

    def __len__(self):
        return math.ceil(len(self.iterator) / self.batch_size)

    def __call__(self, batch_index):
        batch_samples = list(self.iterator[batch_index * self.batch_size: (batch_index + 1) * self.batch_size])
        return [{self.iterator_key: i} for i in batch_samples]


class D:
    def __init__(self, iterator_key, iterator, batch_size):
        self.iterator = iterator
        self.iterator_key = iterator_key
        self.batch_size = batch_size

    def __len__(self):
        return math.ceil(len(self.iterator) / self.batch_size)

    def __call__(self, batch_index):
        batch_keys = list(self.iterator.keys())[batch_index * self.batch_size: (batch_index + 1) * self.batch_size]
        batch_values = [self.iterator[i] for i in batch_keys]
        batch_samples = []
        for key, value in zip(batch_keys, batch_values):
            batch_samples.append({self.iterator_key + "_key": key, self.iterator_key + "_value": value})
        return batch_samples
