from retry import retry


@retry((AssertionError,), max_retries=3)
def cause_trouble():
    assert False


if __name__ == "__main__":
    cause_trouble()
