def exponential_backoff(wait_time, exponential_rate):
    def wait_func():
        nonlocal wait_time
        wait_time *= exponential_rate
        return wait_time

    return wait_func
