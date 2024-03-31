from functools import wraps
from typing import Callable
import inspect


class CallbackFactory:
    def __init__(self, func: Callable, *args, **kwargs):
        """
        Initialize the CallbackFactory.

        Parameters:
            func (Callable): The callable function to be wrapped.
            *args: Positional arguments to be passed to the function.
            **kwargs: Keyword arguments to be passed to the function.

        Raises:
            TypeError: If `func` is not a callable object.
        """
        if not callable(func):
            raise TypeError("The 'func' argument must be callable")

        self.func = func
        self.kwargs = kwargs

        if len(args) > 0:
            func_args = inspect.getfullargspec(func).args
            self.kwargs.update({func_args[i]: a for i, a in enumerate(args)})

    def __call__(self, **override_kwargs):
        """
        Call the wrapped function with provided keyword arguments.
        If no arguments are provided during calling,
        then the stored ones (during instance creation) are used.

        Returns:
            The result of calling the wrapped function with provided arguments.
        """
        runtime_kwargs = {**self.kwargs, **override_kwargs}
        return self.func(**runtime_kwargs)


def callback_factory(func: Callable, *args, **kwargs):
    """
    Create a callback function that wraps the provided callable function.

    Parameters:
        func (Callable): The callable function to be wrapped.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        A wrapped function that calls the provided
        callable function with the specified arguments.

    Raises:
        TypeError: If `func` is not a callable object.
    """
    if not callable(func):
        raise TypeError("The 'func' argument must be callable")

    if len(args) > 0:
        func_args = inspect.getfullargspec(func).args
        kwargs.update({func_args[i]: a for i, a in enumerate(args)})

    @wraps(func)
    def wrapped_func(**override_kwargs):
        runtime_kwargs = {**kwargs, **override_kwargs}
        return func(**runtime_kwargs)

    return wrapped_func
