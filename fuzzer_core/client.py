from bravado.client import SwaggerClient

from fuzzer_core.util import cached_result


@cached_result
def get_client(url, schema):
    """
    :type url: str
    :param url: server URL

    :type schema: dict
    """
    return SwaggerClient.from_spec(
        schema,
        origin_url=url,
    )
