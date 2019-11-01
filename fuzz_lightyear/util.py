from typing import Iterable
from typing import List
from typing import Optional
from typing import Union


def listify_decorator_args(
    argument: Optional[Union[str, Iterable[str]]],
) -> List[str]:
    """Converts a user-supplied "list" to an actual Python list.
    This helper supports a "string" list as follows:
        >>> listify_decorator_args('a,b,c')
        ['a', 'b', 'c']

    :param argument: The argument to listify.
    :return: A list of strings..
    """
    if not argument:
        return []

    if isinstance(argument, str):
        return [
            arg.strip()
            for arg in argument.split(',')
        ]

    return list(argument)
