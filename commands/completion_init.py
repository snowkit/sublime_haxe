import sublime_plugin
import sublime

from ..haxe_completion import hxc_server, hxc_settings

class HaxeCompletionInitCommand( sublime_plugin.WindowCommand ):

    def run( self ) :
        view = sublime.active_window().active_view()
        hxc_server.init()
