__all__ = ["DesignerAgent"]


def __getattr__(name):
    if name == "DesignerAgent":
        from .designer_agent import DesignerAgent
        return DesignerAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
