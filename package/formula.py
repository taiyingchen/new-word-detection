from math import log2


def pmi(xy, x, y):
    """Pointwise mutual information
    """
    try:
        return log2(xy/(x*y))
    except (ZeroDivisionError, ValueError) as e:
        return 0


def npmi(xy, x, y):
    """Normalized pointwise mutual information
    """
    return pmi(xy, x, y) / (-log2(xy))


def entropy(neighbors):
    """Compute entropy of a list of items

    Parameters
    ----------
    neighbors : dict or list
        Store term frequency
        dict - key is str, value is frequency
        list - value is frequency
    """
    if type(neighbors) == dict:
        total = sum(neighbors.values())
        return sum([-v/total*log2(v/total) for v in neighbors.values()])
    elif type(neighbors) == list:
        total = sum(neighbors)
        return sum([-v/total*log2(v/total) for v in neighbors])
