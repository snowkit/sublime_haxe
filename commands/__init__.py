__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

from .completion_init import HaxeCompletionInitCommand
from .completion_reset import HaxeCompletionResetCommand
from .completion_shutdown import HaxeCompletionShutdownCommand

print("Haxe Completion Server : load commands")

__all__ = [
    'HaxeCompletionInitCommand',
    'HaxeCompletionResetCommand',
    'HaxeCompletionShutdownCommand'
]
