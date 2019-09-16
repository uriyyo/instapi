import inspect
import logging
import types
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Type
from typing import cast

from autologging import logged
from autologging import traced

from instapi.types import StrDict


class LoggingMeta(type):
    def __new__(
            mcs,
            name: str,
            bases: Tuple[Type],
            namespace: StrDict,
            *,
            logger: Optional[logging.Logger] = None,
    ) -> Any:
        if logger is None:
            current_frame = cast(types.FrameType, inspect.currentframe())
            frame = current_frame.f_back

            try:
                logger = logging.getLogger(frame.f_globals['__name__'])
            finally:
                del frame
                del current_frame

        cls = super().__new__(mcs, name, bases, namespace)
        return logged(logger)(traced(logger))(cls)


__all__ = [
    'LoggingMeta',
]
