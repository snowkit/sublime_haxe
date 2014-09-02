import sublime_plugin
import sublime

# import Default
# stexec = getattr( Default , "exec" )
# ExecCommand = stexec.ExecCommand

from ..haxe_completion import HaxeCompletionist

class HaxeCompletionCompleteCommand( sublime_plugin.WindowCommand  ):

    def run( self, on_complete=None, cwd='', fname='', offset=0, hxml=[], **kwargs ) :
        view = sublime.active_window().active_view()
        HaxeCompletionist.current.complete(on_complete, cwd, fname, offset, hxml)
