import functools


def api_logger(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    # Log the API call
    print(f"API Call: {func.__name__} - args: {args}, kwargs: {kwargs}")

    # Call the original function
    return func(*args, **kwargs)

  return wrapper
