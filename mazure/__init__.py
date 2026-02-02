import warnings
# Suppress pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

import inspect
import functools

from .proxy import Mazure
from .api_client import MazureAPI


def mazure(*fargs, **fkwargs):
    def interface(func):
        @functools.wraps(func)
        def action(*args, **kwargs):
            with Mazure(targets, fkwargs.get('allow')):
                func(*args, **kwargs)
        return action

    targets = [arg for arg in fargs if not inspect.isfunction(arg)]
    return interface


__all__ = ['mazure', 'Mazure', 'MazureAPI']
