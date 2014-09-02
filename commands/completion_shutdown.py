import sublime_plugin
import sublime

from ..haxe_completion import HaxeCompletionist

class HaxeCompletionShutdownCommand( sublime_plugin.WindowCommand ):

    def run( self ) :
        view = sublime.active_window().active_view()
        HaxeCompletionist.current.shutdown()