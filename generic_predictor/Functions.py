"""
Creates the math operation needed to build function terms
"""

def fetch(i):
    """
    Creates a lambda which fetches a particular input value

    x: the input vector
    i: the element in the vector to fetch
    returns: a lambda which returns the particular element from the array
    """
    return lambda x: x[i]


def mul(a, b):
    """
    Multiplies the results of two lambdas

    a: a lambda which returns a value that can be multiplied
    b: a lambda which returns a value that is a suitible RHS for multiplication with a
    returns: a lambda which gives the result of a(x) * b(x)
    """

    return lambda x: a(x) * b(x)

def power(a, b):
    """
    Raise the result of a lambda to the power of b

    a: the lambda
    b: the power
    returns: a lambda which gives the result of pow(a(x), b)
    """
    return lambda x: pow(a(x), b)

def one():
    """
    return a one
    """
    return lambda x: 1
