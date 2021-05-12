from AutoPypline.Utils import object_instantiate


class CreateGraphNode:
    def __init__(self, key):
        """
        Instantiates a node of a double linked graph
        :param key: The identifier for the node
        """
        self.name = key
        self.callable_object = None
        self.params = None
        self.dynamic_params = dict()
        self.predecessors = dict()
        self.successors = []
        self.outputs = None
        self.node_executed = False
        self.root = False
        self.leaf = False
        self.independent = False
        self.internal_graph = None


def graph_designer(dictionary, global_graph=None):
    """
    Generates a double linked graph for the dictionary containing the project flow
    :param global_graph:
    :param dictionary:
        Type: dict
        Dictionary containing the project flow
    :return: double linked graph representation of the dictionary
    """
    local_graph = dict()
    if global_graph is not None:
        global_graph_keys = list(global_graph.keys())
        common_keys = [i for i in global_graph_keys if i in list(dictionary.keys())]
        if len(common_keys):
            raise ValueError("Duplicate keys are not allowed in the configuration definition. Duplicate keys: ",
                             common_keys)
    else:
        global_graph_keys = None
        global_graph = dict()
    dictionary_keys = list(dictionary.keys())
    for key in dictionary_keys:
        node = CreateGraphNode(key)
        if dictionary[key].get("internal_graph", None):
            node.internal_graph = dictionary[key]["internal_graph"]
        else:
            node = node_initiator(dictionary[key], node)
        if global_graph_keys is not None:
            probable_inputs = global_graph_keys + dictionary_keys
        else:
            probable_inputs = dictionary_keys
        inputs = get_inputs(dictionary, key)
        if inputs.get("hidden_inputs") is not None:
            hidden_inputs = set_inputs(inputs["hidden_inputs"], probable_inputs)
            inputs = {**inputs["specified_inputs"], **hidden_inputs}
        else:
            inputs = {**inputs["specified_inputs"]}
        if len(inputs):
            if isinstance(inputs, dict):
                for input_key in list(inputs.keys()):
                    if inputs[input_key].split('.')[0] == key:
                        raise ValueError("Inputs to a module cannot be the module itself :"
                                         " ('key': %s, 'inputs: %s')" % (key, inputs[input_key].split('.')[0]))
                    elif inputs[input_key].split('.')[0] not in dictionary_keys:
                        if len(global_graph):
                            if inputs[input_key] in global_graph_keys:
                                node.predecessors[input_key] = inputs[input_key]
                        else:
                            raise ValueError("Error in Inputs '%s' for module '%s' " % (input_key, key))
                    else:
                        node.predecessors[input_key] = inputs[input_key]
            else:
                raise AttributeError("Input parameters for any node should be provided in the form of a dictionary"
                                     " (key indicating the parameter name and value corresponding to the parameter"
                                     " value). Error caught while finding predecessors. Given format for node %s is %s"
                                     % (key, type(inputs)))
        else:
            node.root = True
        successors = []
        for other_key in dictionary_keys:
            if not other_key == key:
                other_inputs = get_inputs(dictionary, other_key)
                if other_inputs.get("hidden_inputs") is not None:
                    hidden_inputs = set_inputs(other_inputs["hidden_inputs"], probable_inputs)
                    other_inputs = {**other_inputs.get("specified_inputs", {}), **hidden_inputs}
                else:
                    other_inputs = {**other_inputs.get("specified_inputs", {})}
                if len(other_inputs):
                    if isinstance(other_inputs, dict):
                        other_inputs = [other_inputs[i].split('.')[0] for i in list(other_inputs.keys())]
                        if key in other_inputs:
                            successors.append(other_key)
                    else:
                        raise ValueError("Input parameters for any node should be provided in the form of a dictionary"
                                         " (key indicating the parameter name and value corresponding to the parameter"
                                         "value). Error caught while finding successors. Given format for node %s is %s"
                                         % (other_key, type(other_inputs)))
        if not(len(successors)):
            node.leaf = True
        else:
            node.successors = successors
        if node.leaf and node.root:
            node.independent = True
            node.leaf = False
            node.root = False
        local_graph[key] = node
    global_graph = {**global_graph, **local_graph}
    return local_graph, global_graph


def node_initiator(dictionary, node):
    if dictionary.get('params', None):
        params = dictionary["params"]
    else:
        params = None
    remove_params = None
    if params is not None:
        if isinstance(params, dict):
            for param_name, param_value in params.items():
                if isinstance(param_value, str):
                    if len(param_value.split(".")) == 2 and param_value.split(".")[0].lower() == "dynamic":
                        if not len(node.dynamic_params):
                            remove_params = []
                        node.dynamic_params[param_name] = tuple([param_value.split(".")[1]])
                        remove_params.append(param_name)
            if remove_params is not None:
                for remove_param_name in remove_params:
                    params.pop(remove_param_name)
        else:
            raise AttributeError("Input parameters for any node should be provided in the form of a dictionary"
                                 " (key indicating the parameter name and value corresponding to the parameter value)"
                                 " Given format for node '%s' is %s" % (node.name, type(params)))
    if dictionary.get('function', None) and dictionary.get('factory', None):
        raise AttributeError("Either factory path or function path has to be given not both. Error caught while"
                             " processing node '%s'" % node.name)
    elif dictionary.get('function', None):
        callable_obj = object_instantiate(dictionary["function"])
        node.callable_object = callable_obj
        node.params = params
    elif dictionary.get('factory', None):
        callable_attr = object_instantiate(dictionary["factory"])
        if params is None:
            params = {}
        node.callable_object = callable_attr(**params)
    else:
        raise AttributeError("Either factory path or function path has to be given. Neither was provide for node '%s'"
                             % node.name)
    return node


def get_inputs(dictionary, node_name):
    if dictionary[node_name].get("internal_graph") is not None:
        next_lvl_dictionary = dictionary[node_name]["internal_graph"]["control_flow"]
        specified_inputs = dictionary[node_name].get("inputs", {})
        inputs = []
        node_names_i = list(next_lvl_dictionary.keys())
        for node_name_i in node_names_i:
            if node_name_i == "outputs":
                continue
            inputs_i = get_inputs(next_lvl_dictionary, node_name_i)
            for key, val in inputs_i.items():
                if isinstance(val, list):
                    inputs.extend(val)
                else:
                    inputs.append(val)
        generator = dictionary[node_name]["internal_graph"].get("generator_inputs")
        if generator is not None:
            generator_inputs = generator.get("iterator_dict", {})
            inputs.append(generator_inputs)
        return {"specified_inputs": specified_inputs, "hidden_inputs": inputs}
    else:
        return {"specified_inputs": dictionary[node_name].get('inputs', {})}


def set_inputs(inputs_list, probable_keys):
    inputs_values = []
    final_inputs = dict()
    for input_i in inputs_list:
        for key_i, value_i in input_i.items():
            inputs_values.append(value_i)
    inputs_values = list(set(inputs_values))
    inputs_values = [i for i in inputs_values if i in probable_keys]
    for i, val_i in enumerate(inputs_values):
        final_inputs["input_%d" % i] = val_i
    return final_inputs
