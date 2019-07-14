import importlib.util
import os


def import_fixtures(path: str):
    """Recursively imports all python files from a path."""
    if os.path.isfile(path):
        import_module_from_path(path)
        return

    for root, _, filenames in os.walk(path):
        for filename in filenames:
            path = os.path.join(root, filename)
            if not path.endswith('.py'):
                continue

            import_module_from_path(path)


def import_module_from_path(path: str):
    """
    Source: https://stackoverflow.com/a/67692

    :param path: path to python file to import
    """
    # I think this just needs to be unique.
    module_name = path.rstrip('.py').replace('/', '.')

    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )
    if not spec:
        return

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
