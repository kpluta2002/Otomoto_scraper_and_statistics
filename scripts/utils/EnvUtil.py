import os
from typing import Any

from dotenv import load_dotenv

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv(dotenv_path=f"{root}/.env")
load_dotenv(dotenv_path=f"{root}/.env.secrets")

def get_var(name: str, cast: type = str) -> Any:
    """
    Fetches the environment variable `name`.
    If it’s not set, or if casting fails, raise a RuntimeError.

    Args:
        name: the name of the env var to read
        cast: a type (like int, float, str) used to convert the string value.
              Defaults to str (i.e., no casting beyond “it must be non-None”).
    Returns:
        The typed value (e.g. int(value) if cast=int).
    Raises:
        RuntimeError if the var is missing or if cast(...) fails.
    """
    raw = os.getenv(name)
    if raw is None:
        raise RuntimeError(f"Environment variable {name!r} is required but not set.")

    if cast is str:
        return raw

    try:
        return cast(raw)
    except (ValueError, TypeError) as e:
        raise RuntimeError(
            f"Environment variable {name!r} could not be cast to {cast.__name__!r}: {e!s}"
        ) from e
