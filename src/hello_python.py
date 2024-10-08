import pandas as pd
import numpy as np


def layer_sizes(X, Y):
    """
    Arguments:
    X -- input dataset of shape (input size, number of examples)
    Y -- labels of shape (output size, number of examples)

    Returns:
    n_x -- the size of the input layer
    n_h -- the size of the hidden layer
    n_y -- the size of the output layer
    """
    # (≈ 3 lines of code)
    # n_x = ...
    # n_h = ...
    # n_y = ...
    # YOUR CODE STARTS HERE

    n_x = X.shape[0]  # number of features -> rows of X
    n_h = 4  # number of neurons in layer 1 = 4
    n_y = Y.shape[
        0
    ]  # number of rows in the Y vector -> 1 in our case, note that Expected output in not using our dataset, so output differs!

    # YOUR CODE ENDS HERE
    return (n_x, n_h, n_y)


data = {"Name": ["Alice", "Bob"], "Age": [24, 55], "NameCity": ["London", "Paris"]}
df = pd.DataFrame(data)
df.resample
a = 1
b = 2
c = b + a

np.sqrt()

print(c)
