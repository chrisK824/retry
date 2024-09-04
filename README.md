# retry
A simple, yet powerful, generic retry decorator in Python for retrying functions with various backoff and callback strategies.


## Install
`pip install retry-reloaded`

## Features:

- **Exception Handling**: Retry based on specific exceptions. If not specified then the default behaviour is to retry on all exceptions.
- **Excluded Exceptions**: Specify exceptions that should not trigger retries. If an exception listed in excluded_exceptions is raised, the retry mechanism will not retry and will raise the exception immediately. Useful use case for this is to target the generic (and default) Exception in `exceptions` parameter and opt-out from retrying on specific exceptions.
- **Maximum Retries**: Set the maximum number of retry attempts.
- **Timeout**: Specify the maximum time in seconds to spend on retries. Timeout check happens right before retry execution of the wrapped function.
- **Deadline**: Define a deadline in seconds for retries to complete. Deadline check happens right after the retry execution of the wrapped function.
- **Backoff Strategies**: Choose from various backoff strategies: fixed, exponential, linear, random
- **Retry Callback**: Execute a callback function between retry attempts.
- **Successful Retry Callback**: Perform an action after a successful retry.
- **Failure Callback**: Define a callback function after failing all retries.
- **Logging control**: Define which logger (or no logger) to use for logging retries and exceptions.
- **Exception Re-raising**: Optionally re-raise the last original exception that occured after all retries have been exhausted.

## API
- Decorator: `retry`
- Retry exceptions: `MaxRetriesException`, `RetriesTimeoutException`, `RetriesDeadlineException`
- Callback factory: `CallbackFactory`, `callback_factory`
- Backoff strategies: `FixedBackOff`, `LinearBackOff`, `ExponentialBackOff`, `RandomUniformBackOff`


## Examples

```python
# public API
from retry_reloaded import (
    retry,
    callback_factory,
    CallbackFactory,
    FixedBackOff,
    LinearBackOff,
    ExponentialBackOff,
    RandomUniformBackOff,
    MaxRetriesException,
    RetriesTimeoutException,
    RetriesDeadlineException
)
```

```python
# Retry until maximum retries are reached
# no backoff strategy means the default will apply,
# which is 0 delay between retries
@retry((AssertionError,), max_retries=3)
def cause_max_retries_error():
    assert False
```

```python
# Retry until timeout error after 2 seconds
# Fixed backoff strategy for 1 second delay between retries
@retry((ValueError,), timeout=2, backoff=FixedBackOff(base_delay=1))
def cause_timeout_error():
    raise ValueError
```

```python
# Retry until deadline error after 3 seconds
# Not really retrying here, this will just execute once
# as the execution will take longer than deadline
@retry(deadline=3)
def cause_deadline_error():
    sleep(4)
```

```python
# Retry until deadline error after 2 seconds
# Fixed backoff strategy for 1 second delay between retries
# Expected to retry twice and then succeed but restricted by deadline
@retry(
        (ValueError,),
        deadline=2,
        backoff=FixedBackOff(base_delay=1)
)
def cause_deadline_error_after_retries():
    if not hasattr(cause_deadline_error_after_retries, "call_count"):
        cause_deadline_error_after_retries.call_count = 0
    cause_deadline_error_after_retries.call_count += 1
    if cause_deadline_error_after_retries.call_count < 2:
        raise ValueError
    else:
        sleep(1)
```

```python
# Retry until maximum retries are reached
# Random backoff strategy with an initial delay and
# limits for min and max delay in next retries
# Callback function between retries by passing a callable function
def retry_callback():
    logger.debug("Calling between retries")


@retry(
        (ValueError,),
        max_retries=3,
        backoff=RandomUniformBackOff(base_delay=0.3, min_delay=0.1, max_delay=0.5),
        retry_callback=retry_callback
)
def retry_with_callback():
    raise ValueError
```


```python
# Retry indefinetely as there is no max retries, timeout
# or deadline specified
# Exponential backoff strategy with an initial delay of 1 second
# Parametrized callback with utility of package to call after successful retry
# Successful callback is expected after successful retry on 3rd round
def successful_retry_callback(value):
    logger.debug(f"Calling on successful retry with value: {value}")

successful_retry_callback_ = callback_factory(successful_retry_callback, "phew")

@retry(
        (ValueError,),
        backoff=ExponentialBackOff(base_delay=1),
        successful_retry_callback=successful_retry_callback_
)
def successful_retry_with_callback():
    if not hasattr(successful_retry_with_callback, "call_count"):
        successful_retry_with_callback.call_count = 0
    successful_retry_with_callback.call_count += 1
    if successful_retry_with_callback.call_count < 3:
        raise ValueError
```

```python
# Retry until maximum retries are reached
# Linear backoff strategy with an initial delay of 0.1 second and 0.1 second as step
# Parametrized callback with utility of package to call after failure of all retries
# Failure callback is expected after failing all 3 retries
def failure_callback(value):
    logger.debug(f"Calling after failure of all retries with value: {value}")

failure_callback_ = CallbackFactory(failure_callback, value="wasted")

@retry(
        max_retries=3,
        backoff=LinearBackOff(base_delay=0.1, step=0.1),
        failure_callback=failure_callback_
)
def fail_with_callback():
    raise ValueError
```


```python
# Retry with re-raising the original exception after all retries
# Retry 2 times and then raise the original exception (ValueError)
@retry(
        (ValueError,),
        max_retries=2,
        reraise_exception=True
)
def retry_with_reraise():
    raise ValueError("Original exception to be re-raised")
```

```python
# Retry on all exceptions, except from ValueError
@retry(excluded_exceptions=(ValueError,))
def give_up_on_value_error():
    random_int = randint(1, 10)

    if random_int >= 5:
        raise RuntimeError
    else:
        raise ValueError("Give up on the error, do not retry.")

```