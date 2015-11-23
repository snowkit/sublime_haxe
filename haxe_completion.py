# -*- coding: utf-8 -*-

import sys, os, subprocess, re, shlex

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

        print("[haxe completion] __init__")

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
            print("[haxe completion] load custom port as {}".format(self.port))
        if settings.has("haxe_path") is True:
            self.haxe_path = settings.get("haxe_path")
            print("[haxe completion] load custom haxe path as {}".format(self.haxe_path))

        print("[haxe completion] trying to start cache server `" + self.haxe_path + "` port:" + str(self.port))

        #this only starts the completion cache host from haxe,
        #then each request is faster, in get()

        try:
            self.process = run_process_bg([self.haxe_path, "-v", "--wait", str(self.port)])
            #Popen( [ self.haxe_path, "-v", "--wait", str(self.port) ], env = os.environ.copy(), startupinfo=STARTUP_INFO)
            print("[haxe completion] started with `" + self.haxe_path + "` port:" + str(self.port))

        except(OSError, ValueError) as e:
            reason = u'[haxe completion] error starting server and connecting to it: \n%s' % e
            print(reason)
            return None

    def complete(self, cwd='', fname='', offset=0, hxml=[]):

        print("[haxe completion] complete")

        self.init()
        view = sublime.active_window().active_view()

        haxe_cmd = [
            self.haxe_path,
            "--no-output",
            "--cwd", cwd,
            "--connect", "127.0.0.1:" + str(self.port),
            "--display", fname + "@" + str(offset)
        ]

        print("[haxe completion] haxe complete args " + str(haxe_cmd+hxml))

        _proc, _result_buffer = run_process( haxe_cmd+hxml )
        _result = ""

        if _result_buffer:
            _result = _result_buffer.decode('utf-8')
            if _result:
                _result = _result.strip()

        if _proc:
            try:
                _proc.kill();
                _proc.wait();
            except:
                pass

        return _result

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

    _proc = run_process_bg(args)
    return _proc, _proc.communicate()[0]

def run_process_bg( args ):

    _proc = None

    #this shell_cmd is not used by windows
    shell_cmd = ""
    for arg in args:
        #make sure lines from the hxml file don't trip up the shell
        shell_cmd += shlex.quote(arg) + " "

    if sys.platform == "win32":
        _proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=STARTUP_INFO)

    elif sys.platform == "darwin":
        # Use a login shell on OSX, otherwise the users expected env vars won't be setup
        _proc = subprocess.Popen(["/bin/bash", "-l", "-c", shell_cmd], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, startupinfo=STARTUP_INFO, shell=False,
            preexec_fn=os.setsid)
    elif sys.platform == "linux":
        # Explicitly use /bin/bash on Linux, to keep Linux and OSX as
        # similar as possible. A login shell is explicitly not used for
        # linux, as it's not required
        _proc = subprocess.Popen(["/bin/bash", "-c", shell_cmd], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, startupinfo=STARTUP_INFO, shell=False,
            preexec_fn=os.setsid)

    return _proc



class HaxeCompletionResetCommand( sublime_plugin.WindowCommand ):

    def run( self ) :
        global _completionist_

        view = sublime.active_window().active_view()
        _completionist_.reset()
