import multiprocessing as mp
import copy
from AutoPypline._auto_pipeline_backend._designer import graph_designer
from AutoPypline._auto_pipeline_backend._flow_preparation import flow_generator
from AutoPypline._auto_pipeline_backend._sample_generator_related import AutomatedGenerator
from AutoPypline._auto_pipeline_backend._executor import execute_graph


class AutoPipeline:
    def __init__(self, config, generator_inputs=None, global_graph=None, store_output_as="List"):
        """
        Given a config file path containing the project modules and the link between the modules,
        a graph is created and the flow indicated by the graph is executed
        :param config:
            Type: dict
            Dictionary containing the project flow
        :param generator_inputs:
            Type: Dict
            Dictionary containing parameters of the generator function.
        :param global_graph:
            Type: Dict or None
            In case of multi level graphs, executed outer level nodes of the graph is sent as parameter
        """
        self.required_outputs = None
        if config.get("outputs", None) is not None:
            self.required_outputs = config.pop("outputs")
        self.local_graph, self.global_graph = graph_designer(config, global_graph)
        self.directed_flows = flow_generator(self.local_graph, self.global_graph)
        self.local_graph_backup = copy.deepcopy(self.local_graph)
        self.global_graph_backup = copy.deepcopy(self.global_graph)
        self.multi_threading = False
        self.generator = None
        self.output_format = store_output_as
        if generator_inputs is not None:
            iterators = generator_inputs.get("iterator_dict")
            if iterators is not None:
                for iterator_name, iterator_value in iterators.items():
                    if len(iterator_value.split(".")) == 1:
                        iterators[iterator_name] = self.global_graph[iterator_value].outputs
                    elif len(iterator_value.split(".")) == 3:
                        node_name, _, specific_output = iterator_value.split(".")
                        iterators[iterator_name] = self.global_graph[node_name].outputs[specific_output]
                generator_inputs["iterator_dict"] = iterators
            self.generator = AutomatedGenerator(**generator_inputs)
            if generator_inputs["batch_size"] > 1:
                self.multi_threading = True

    @staticmethod
    def search_for_key(list_of_elements):
        key = None
        for group_element in list_of_elements:
            for element_name, element_value in group_element.items():
                if isinstance(element_value, str):
                    key = element_value
                if key is not None:
                    return key
        if key is None:
            for group_element in list_of_elements:
                for element_name, element_value in group_element.items():
                    if isinstance(element_value, int) or isinstance(element_value, float):
                        key = str(element_value)
                    if key is not None:
                        return key
        if key is None:
            return None

    def reset(self):
        self.local_graph = copy.deepcopy(self.local_graph_backup)
        self.global_graph = copy.deepcopy(self.global_graph_backup)

    def __call__(self, external_inputs=None):
        if self.generator is not None and callable(self.generator):
            if self.output_format.lower() == "list":
                outputs = []
            elif self.output_format.lower() == "dict":
                outputs = dict()
            else:
                raise AttributeError("Output formats supported: [List, Dict], Provided 'store_output_as': ",
                                     self.output_format)
            if self.multi_threading:
                pool = mp.Pool()
                j = 0
                for i in range(self.generator.__len__()):
                    self.reset()
                    batch_sample = self.generator(i)
                    batch_input = [tuple([copy.deepcopy(self.global_graph), self.directed_flows,
                                         batch_sample_i, self.required_outputs]) for batch_sample_i in batch_sample]
                    batch_results = pool.starmap(execute_graph, batch_input)
                    for sample, batch_result in zip(batch_sample, batch_results):
                        j += 1
                        if isinstance(outputs, list):
                            outputs.append(batch_result)
                        else:
                            output_key = self.search_for_key([sample])
                            if output_key is None:
                                output_key = "input_%d" % j
                            outputs[output_key] = batch_result
                pool.close()
                pool.join()
            else:
                for i in range(self.generator.__len__()):
                    self.reset()
                    batch_sample = self.generator(i)
                    batch_results = execute_graph(copy.deepcopy(self.global_graph), self.directed_flows,
                                                  *batch_sample, self.required_outputs)
                    if isinstance(outputs, list):
                        outputs.append(batch_results)
                    else:
                        output_key = self.search_for_key(batch_sample)
                        if output_key is None:
                            output_key = "input_%d" % i
                        outputs[output_key] = batch_results

        else:
            outputs = execute_graph(self.global_graph, self.directed_flows, external_inputs,
                                    self.required_outputs)
            self.reset()
        if isinstance(outputs, list):
            if len(outputs) <= 1:
                return outputs[0]
        return outputs
