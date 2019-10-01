import os

from .app import get_current_application
from .core.database import Base
from .core.database import create_engine
from .core.database import get_database_file
from .core.routes import configure_routes


def main():
    app = get_current_application()
    app.config['RESTPLUS_MASK_SWAGGER'] = False

    configure_routes(app)

    # Ensure every run will be fresh.
    path_to_db = get_database_file()
    if os.path.exists(path_to_db):
        os.unlink(path_to_db)

    Base.metadata.create_all(create_engine())

    app.run(
        '127.0.0.1',
        port=int(os.environ.get('PORT', 5000)),
    )
