# -*- coding: utf-8 -*-

import sys, os

import sublime, sublime_plugin


#plugin location
plugin_file = __file__
plugin_filepath = os.path.realpath(plugin_file)
plugin_path = os.path.dirname(plugin_filepath)


print("hello haxe completion")

hxc_settings = None
hxc_server = None

class HaxeCompletionServer( sublime_plugin.EventListener ):

    def __init__(self):
        global hxc_server, hxc_settings
        hxc_server = self
        hxc_settings = sublime.load_settings('haxe_completion.sublime-settings')
        print("[haxe completion] __init__")

    def __del__(self) :
        self.shutdown()
        print("[haxe completion] __del__")

    def init(self):
        print("[haxe completion] init")
        port = HaxeCompletionServer.settings.get("port", 6110)
        print(port)
        # cmd = [haxepath , "--wait" , str(self.serverPort) ]
        # print("Starting Haxe server on port "+str(self.serverPort))

        # self.serverProc = Popen(cmd, env = merged_env, startupinfo=STARTUP_INFO)
        # self.serverProc.poll()

    # except(OSError, ValueError) as e:
    #     err = u'Error starting Haxe server %s: %s' % (" ".join(cmd), e)
    #     sublime.error_message(err)

    def reset(self):
        print("[haxe completion] reset")

    def shutdown(self):
        print("[haxe completion] shutdown")
