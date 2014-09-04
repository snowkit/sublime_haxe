# -*- coding: utf-8 -*-

import sys, os, subprocess, socket, re

from subprocess import Popen, PIPE

import sublime, sublime_plugin


#plugin location
plugin_file = __file__
plugin_filepath = os.path.realpath(plugin_file)
plugin_path = os.path.dirname(plugin_filepath)

import Default
stexec = getattr( Default , "exec" )
ExecCommand = stexec.ExecCommand
AsyncProcess = stexec.AsyncProcess

try:
  STARTUP_INFO = subprocess.STARTUPINFO()
  STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
  STARTUP_INFO.wShowWindow = subprocess.SW_HIDE
except (AttributeError):
    STARTUP_INFO = None

print("hello haxe completion")


_completionist_ = None

def plugin_unloaded():
    if _completionist_:
        _completionist_.shutdown()

class HaxeCompletionist( sublime_plugin.EventListener ):

    def __init__(self):
        HaxeCompletionist.current = self
        global _completionist_
        _completionist_ = self

        self.process = None
        self.socket = None
        self.on_complete = None

        print("[haxe completion] __init__")


    def derp(self, fn):
        fn("hello")

    def init(self, forced=False):

        if not forced:
            if self.process is not None:
                return;

        print("[haxe completion] init")

        settings = sublime.load_settings('haxe_completion.sublime-settings')

        #kill any existing server
        self.shutdown(True)

        #defaults
        self.haxe_path = "haxe"
        self.port = 6110

        if settings.has("port") is True:
            self.port = settings.get("port")
        if settings.has("haxe_path") is True:
            self.haxe_path = settings.get("haxe_path")

        return

        print("[haxe completion] trying to start cache server " + self.haxe_path + ":" + str(self.port))

        #this only starts the completion cache host from haxe,
        #then each request is faster, in get()

        try:
            self.process = Popen( [ self.haxe_path, "-v", "--wait", str(self.port) ], env = os.environ.copy(), startupinfo=STARTUPINFO)

        except(OSError, ValueError) as e:
            reason = u'[haxe completion] error starting server and connecting to it: %s' % e
            print(reason)
            return None

    def on_result(self, output):
        print("[haxe completion] on_result")

        if self.on_complete is not None:
                #fire callback
            self.on_complete( output )

        self.on_complete = None

    def complete(self, on_complete=None, cwd='', fname='', offset=0, hxml=[]):
        print("[haxe completion] complete")

        self.init()
        view = sublime.active_window().active_view()
        self.on_complete = on_complete

        haxe_cmd = [
            self.haxe_path,
            "--no-output",
            "--cwd", cwd,
            "--connect", "127.0.0.1:" + str(self.port),
            "--display", fname + "@" + str(offset)
        ]

        view.window().run_command("haxe_completion_exec", {
            "cmd": haxe_cmd + hxml,
            "working_dir": cwd
        })

    def reset(self):
        print("[haxe completion] reset")
        self.shutdown()
        self.init()

    def shutdown(self, forced=False):

        if(forced == False):
            print("[haxe completion] shutdown")

        if self.process is not None :
            self.process.terminate()
            self.process.kill()
            self.process.wait()

        self.process = None

def run_process( args ):
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=STARTUP_INFO).communicate()[0]

class HaxeCompletionResetCommand( sublime_plugin.WindowCommand ):

    def run( self ) :
        global _completionist_

        view = sublime.active_window().active_view()
        _completionist_.reset()

class HaxeCompletionExec( ExecCommand ):

    def run( self, cmd = [],  shell_cmd = None, file_regex = "", line_regex = "", working_dir = "",
            encoding = None, env = {}, quiet = False, kill = False, **kwargs):

        if kill:
            if self.proc:
                self.proc.kill()
                self.proc = None
                self.append_data(None, "[Cancelled]")
            return

        if encoding is None:
            encoding = sys.getfilesystemencoding()

        self.output_view = self.window.get_output_panel("haxe_completion_panel")
        self.debug_text = " ".join(cmd)
        self.encoding = encoding
        self.quiet = quiet
        self.proc = None

        if working_dir != "":
            os.chdir(working_dir)

        if not quiet:
            print( "Running " + " ".join(cmd) )

        sublime.status_message("Fetching completion...")
        # self.show_output_panel()

        try:
            self.proc = AsyncProcess( cmd, None, os.environ.copy(), self, **kwargs)
        except OSError as e:
            print(e)

    def show_output_panel(self):
        show_panel_on_build = sublime.load_settings("Preferences.sublime-settings").get("show_panel_on_build", True)
        if show_panel_on_build:
            self.window.run_command("show_panel", {"panel": "output.exec"})

    def finish(self, *args, **kwargs):
        global _completionist_

        super(HaxeCompletionExec, self).finish(*args, **kwargs)
        output = self.output_view.substr(sublime.Region(0, self.output_view.size()))
        #remove "Finished in" timing
        output = re.sub('(\[Finished in.*\])', '', output)
        _completionist_.on_result( output.strip() )
