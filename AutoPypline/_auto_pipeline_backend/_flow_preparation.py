def flow_generator(local_graph, global_graph=None):
    """
    Generates all the parallel flows in the local graph
    :return: Parallel flows
    """
    graph_leaves = [i for i in list(local_graph.keys()) if
                    local_graph[i].leaf is True]
    independent_graph_nodes = [i for i in list(local_graph.keys()) if
                               local_graph[i].independent is True]
    parallel_flows = []
    for leaf in graph_leaves:
        flow = [leaf]
        parallel_flows.append(path_finder(flow, local_graph, global_graph=global_graph))
    for node in independent_graph_nodes:
        parallel_flows.append([node])
    return parallel_flows


def path_finder(flow_list, local_graph, node_name=None, global_graph=None):
    """
    1) If node name is not given we start from the root and directly go to its predecessors.
    2) Start with one predecessor at a time by modifying the flow_list as [predecessor1, leaf]
    3) With node name as predecessor, repeat step 1 and 2
    4) The process is repeated till all the nodes in the flow are covered
    :param local_graph:
        Type: Dict
        Graph Data Structure constructed using user config
    :param flow_list:
        Type: list
        List of node nameswhich are dependent on one another
    :param node_name:
        Type: str
        Name of the node which has to be added to the flow in the right order
    :param global_graph:
        Type: dict
    :return: Updated flow list (Ordered from predecessors to successors)
    """
    if node_name is None:
        node_name = flow_list[0]
        inputs = local_graph[node_name].predecessors
    else:
        inputs = local_graph[node_name].predecessors

    inputs = [inputs[i].split('.')[0] for i in list(inputs.keys())]
    for input_name in inputs:
        if input_name in global_graph and input_name not in local_graph:
            continue
        node_index = flow_list.index(node_name)
        if input_name not in flow_list:
            flow_list.insert(node_index, input_name)
            path_finder(flow_list, local_graph, input_name, global_graph)
        elif input_name in flow_list and (node_index < flow_list.index(input_name)):
            flow_list.remove(input_name)
            flow_list.insert(node_index, input_name)
    return flow_list
