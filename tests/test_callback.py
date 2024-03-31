from retry.utils.callback import CallbackFactory, callback_factory
import pytest


def test_CallbackFactory_callable_function():
    def dummy_func():
        pass

    _callback = CallbackFactory(dummy_func)
    assert callable(_callback.func)


def test_CallbackFactory_non_callable_function():
    with pytest.raises(TypeError):
        _ = CallbackFactory("not_callable")


def test_CallbackFactory_arguments_passing():
    def dummy_func(x, y):
        return x * y

    _callback = CallbackFactory(dummy_func, 2, 3)
    assert _callback() == 6


def test_CallbackFactory_keyword_arguments_passing():
    def dummy_func(x, y, z=1):
        return x + y + z

    _callback = CallbackFactory(dummy_func, 2, 3, z=4)
    assert _callback() == 9


def test_CallbackFactory_arguments_override():
    def dummy_func(x, y):
        return x * y

    _callback = CallbackFactory(dummy_func, 2, 3)
    assert _callback(x=3, y=3) == 9


def test_CallbackFactory_partial_arguments_override():
    def dummy_func(x, y, z=1):
        return x + y + z

    _callback = CallbackFactory(dummy_func, 2, 3, z=4)
    assert _callback(y=5) == 11


def test_callback_factory_callable_function():
    def dummy_func():
        pass

    _callback = callback_factory(dummy_func)
    assert callable(_callback)


def test_callback_factory_non_callable_function():
    with pytest.raises(TypeError):
        _ = callback_factory("not_callable")


def test_callback_factory_arguments_passing():
    def dummy_func(x, y):
        return x * y

    _callback = callback_factory(dummy_func, 2, 3)
    assert _callback() == 6


def test_callback_factory_keyword_arguments_passing():
    def dummy_func(x, y, z=1):
        return x + y + z

    _callback = callback_factory(dummy_func, 2, 3, z=4)
    assert _callback() == 9


def test_callback_factory_arguments_override():
    def dummy_func(x, y):
        return x * y

    _callback = callback_factory(dummy_func, 2, 3)
    assert _callback(x=3, y=3) == 9


def test_callback_factory_partial_arguments_override():
    def dummy_func(x, y, z=1):
        return x + y + z

    _callback = callback_factory(dummy_func, 2, 3, z=4)
    assert _callback(y=5) == 11
