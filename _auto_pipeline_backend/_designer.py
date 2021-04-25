from Utils.utils import object_instantiate


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
        inputs = dictionary[key].get('inputs', None)
        if inputs:
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
                other_inputs = dictionary[other_key].get('inputs')
                if other_inputs:
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


