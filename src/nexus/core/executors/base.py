from nexus.core.trackers.logging_utils import DummyLogger
from nexus.core.trackers.main_tracker import PipelineContext
### TODO: REMOVE

def base(title=None):
    """
    Warning: From update 2.3.0, 'base' is depreciated.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            ctx = PipelineContext.get_ctx()
            local_logger = ctx.logger if ctx.logger is not None else DummyLogger()
            local_title = title if title is not None else ""

            if title is not None:
                local_logger.info(f"Running: {local_title}")

            return func(*args, **kwargs)


        return wrapper
    return decorator
