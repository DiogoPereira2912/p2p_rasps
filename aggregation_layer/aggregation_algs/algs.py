from collections import Counter

def aggregate_avg(params_dict):
    """
    Aggregate hyperparameters by calculating the average value for each parameter
    Args:
        params_dict: Dict of dictionaries containing hyperparameters from different nodes
    Returns:
        aggregated_params: Dictionary with averaged hyperparameters
    """
    aggregated_params = {}
    num_nodes = len(params_dict)
    for _, node_params in params_dict.items():
        for param, value in node_params.items():
            if param not in aggregated_params:
                aggregated_params[param] = 0
            aggregated_params[param] += value / num_nodes

    return aggregated_params


def aggregate_majority(params_dict):
    """
    Aggregate hyperparameters by selecting the majority value for each parameter
    Args:
        params_dict: Dict of dictionaries containing hyperparameters from different nodes
    Returns:
        aggregated_params: Dictionary with majority hyperparameters
    """
    aggregated_params = {}
    for _, node_params in params_dict.items():
        for param, value in node_params.items():
            if param not in aggregated_params:
                aggregated_params[param] = []
            aggregated_params[param].append(value)

    for param, values in aggregated_params.items():
        most_common_value, _ = Counter(values).most_common(1)[0]
        aggregated_params[param] = most_common_value

    return aggregated_params


ALGS_DICT = {
    "avg": aggregate_avg,
    "majority": aggregate_majority,
}
