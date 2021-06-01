from AutoPypline._auto_pipeline_backend._execution_utils import sequential_flow_executor
from AutoPypline._auto_pipeline_backend._other_utils import supplant_dynamic_values_in_graph, return_outputs_recursive


def execute_graph(graph, directed_flows, dynamic_inputs=None, required_outputs=None):
    if dynamic_inputs is not None:
        graph = supplant_dynamic_values_in_graph(graph, dynamic_inputs)
    graph = sequential_flow_executor(directed_flows, graph)
    if required_outputs is not None:
        return return_outputs_recursive(graph, required_outputs)
    else:
        return None

