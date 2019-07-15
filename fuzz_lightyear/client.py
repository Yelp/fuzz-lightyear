from typing import Any
from typing import Dict
from typing import Optional

from bravado.client import SwaggerClient

from fuzz_lightyear.util import cached_result


@cached_result
def get_client(
    url: str,
    schema: Optional[Dict[str, Any]] = None,
):
    """
    :param url: server URL
    """
    if not schema:
        return SwaggerClient.from_url(url)

    return SwaggerClient.from_spec(
        schema,
        origin_url=url,
    )
