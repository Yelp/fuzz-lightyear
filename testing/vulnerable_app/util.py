def get_name(name):
    """
    Blueprint names must be unique, and cannot contain dots.
    This converts filenames to blueprint names.

    e.g. vulnerable_app.views.basic => basic

    :type name: str
    """
    return name.split('.')[-1]
