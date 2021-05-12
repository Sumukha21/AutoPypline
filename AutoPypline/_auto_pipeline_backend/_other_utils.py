import importlib


def return_outputs(double_linked_graph, required_outputs):
    """
    Extracts the outputs of the required nodes from the double linked graph
    :param double_linked_graph:
    :param required_outputs:
    :return:
    """
    outputs = dict()
    if isinstance(required_outputs, dict):
        for output_name, required_node_name in required_outputs.items():
            if len(required_node_name.split(".")) > 1:
                node_name, _, specific_output_name = required_node_name.split(".")
                outputs[output_name] = double_linked_graph[node_name].outputs[specific_output_name]
            elif len(required_node_name.split(".")) == 1:
                outputs[output_name] = double_linked_graph[required_node_name].outputs
    elif isinstance(required_outputs, list):
        outputs = []
        for required_node_name in required_outputs:
            if len(required_node_name.split(".")) > 1:
                node_name, _, specific_output_name = required_node_name.split(".")
                outputs.append(double_linked_graph[node_name].outputs[specific_output_name])
            elif len(required_node_name.split(".")) == 1:
                outputs.append(double_linked_graph[required_node_name].outputs)
    elif isinstance(required_outputs, str):
        if len(required_outputs.split(".")) > 1:
            node_name, _, specific_output_name = required_outputs.split(".")
            outputs = double_linked_graph[node_name].outputs[specific_output_name]
        elif len(required_outputs.split(".")) == 1:
            outputs = double_linked_graph[required_outputs].outputs
    else:
        raise AttributeError("Required outputs should be provided in dictionary, list or string format")
    if isinstance(outputs, list):
        if len(outputs) <= 1:
            return outputs[0]
    return outputs


def supplant_dynamic_values_in_graph(graph, dynamic_inputs):
    for node in graph:
        if len(graph[node].dynamic_params):
            for param_name, dynamic_param_name in graph[node].dynamic_params.items():
                dynamic_param_value = dynamic_inputs.get(dynamic_param_name[0])
                if dynamic_param_value is None:
                    raise AttributeError("Error when updating dynamic parameters in node %s. Error when trying to find"
                                         " dynamic value for parameter %s. Please check the config file and provide"
                                         " the correct dynamic input name" % (node.name, param_name))
                else:
                    graph[node].dynamic_params[param_name] = dynamic_param_value
    return graph


def object_instantiate(module_name, package=None):
    """
    Imports the module and returns the object of the attribute required
    :param module_name:
        Type: str
        The path to the factory/function
    :param package:
        Type: str
        The path to the project directory which can be used as root
    :return:
    """
    try:
        module_name, attribute_name = module_name.rsplit(".", 1)
        module_init = importlib.import_module(module_name, package=package)
        return getattr(module_init, attribute_name)
    except ModuleNotFoundError as e:
        print("Provided module path %s does not correspond to a valid module" % module_name)


def instance_generator(function=None, factory=None, params=None, package=None):
    """
    Returns an instantiation of the function/factory
    :param function:
        Type: str
        Relative path to the function
    :param factory:
        Type: str
        Relative path to the factory
    :param params:
        Type: dict
        Parameters of the class/function
    :param package:
        Type: str
        The path to the project folder which is used as root when instanntiating
    :return: Instance of the factory/function
    """
    if factory is not None:
        if function is not None:
            raise AttributeError("Either factory path or function path have to be provided, not both")
        if params is None:
            params = dict()
        factory_obj = object_instantiate(module_name=factory, package=package)
        return factory_obj(**params)
    elif function is not None:
        return object_instantiate(module_name=function, package=package)


