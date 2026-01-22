

def generator_example(n):
    """
    Generate a sequence of numbers
    
    Args:
        n (TYPE): The number of elements in the sequence
    
    Raises:
        TypeError: If n is not an integer
        ValueError: If n is less than 0
    """
    """
    Generate a sequence
    
    :param n: number of elements to generate
    :type n: TYPE
    """
    """
    Generate a sequence of numbers
    
    Parameters
    ----------
    n : TYPE
        The number of items in the sequence
    """
    """
    Generate an example
    
    Args:
        n (TYPE): the number of examples to generate
    """
  
    for i in range(n):
        yield i


def raises_example(x):
    """
    Raises an exception based on the input value
    
    Args:
        x (TYPE): The input value to determine the exception type
    
    Raises:
        TypeError: If x is not a valid input type
        ValueError: If x is an invalid value
    """
    """
    Raise ValueError for negative input
    
    :param x: input value
    :type x: TYPE
    :raises ValueError: negative
    """
    """
    Raise ValueError for negative x
    
    Parameters
    ----------
    x : TYPE
        the input value
    
    Raises
    ------
    ValueError
        negative
    """
    """
    Raise ValueError for negative x
    
    Args:
        x (TYPE): the input value
    
    Raises:
        ValueError: negative
    """
    

    if x < 0:
        raise ValueError("negative")
    return x * 2

