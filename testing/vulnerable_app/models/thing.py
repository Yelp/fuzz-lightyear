from ..core.database import Base


class Thing(Base):
    """
    This is separate from Widget since reusing it causes flakiness.
    """
    pass
