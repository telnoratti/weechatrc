# Script Name: figlet
# Author: Lucian Adamson <lucian.adamson@yahoo.com>
# Version: RC
# Script License: GPL
# Script Description: Utilizes the command-line figlet application to send macros to channel buffer.
#=============================
#TODO:
# -Implement a /figlet list feature to list installed figlet fonts **DONE**
# -Implement a /figlet [font] [text] **DONE**
# -Implement /fig-get to mass-download figlet fonts from figlet.org

SCRIPT_NAME        = "figlet"
SCRIPT_AUTHOR    = "Lucian Adamson <lucian.adamson@yahoo.com>"
SCRIPT_VERSION    = "1.0"
SCRIPT_LICENSE    = "GPL"
SCRIPT_DESC        = "Utilizes the command-line figlet application to send macros to channel buffer."

import_ok = True

settings = {
    "text_width": "80"
}
try:
    import weechat
except ImportError:
    print "This script must be run under WeeChat."
    print "Get WeeChat now at: http://www.weechat.org"
    import_ok = False

import os
import time

class Command(object):

    """Run a command and capture it's output string, error string and exit status"""

    def __init__(self, command):
        self.command = command

    def run(self, shell=True):
        import subprocess as sp
        process = sp.Popen(self.command, shell = shell, stdout = sp.PIPE, stderr = sp.PIPE)
        self.pid = process.pid
        self.output, self.error = process.communicate()
        self.failed = process.returncode
        return self

    @property
    def returncode(self):
        return self.failed

figfonts=""

def list():
    global figfonts
    #figfonts=""
    figfontdir = Command("figlet -I2").run()
    figfontdir = figfontdir.output.rstrip("\n")
    inst_fonts = Command("ls " + figfontdir).run()
    inst_fonts=inst_fonts.output

    for each in inst_fonts.split("\n"):
        if each.lower().endswith(".flf") == True:
            name, _, extension = each.rpartition(".")
            if name not in figfonts.split("\n"):
                figfonts = figfonts + name + "\n"

    return figfonts

def figlet_completion(data, completion_item, buffer, completion):
    global figfonts
    for eachfig in figfonts.split("\n"):
        weechat.hook_completion_list_add(completion, eachfig, 0, weechat.WEECHAT_LIST_POS_SORT)
    return weechat.WEECHAT_RC_OK

def macro(data, buffer, args):
    global figfonts
    example=False
    arg_array=args.split(" ")
    opt=arg_array[0]
    if opt.lower() == "example":
        arg_array.remove(opt)
        example=True
        opt=arg_array[0]

    if opt.lower() == "list":
        weechat.prnt("", "Available Figlet Fonts")
        weechat.prnt("", list())
        return weechat.WEECHAT_RC_OK
    else:
        returnOK=False
        for eachfont in figfonts.split("\n"):
            if eachfont.lower().strip() == opt.lower().strip():
                returnOK = True
                break
    
    thetext=""
    
    if returnOK == True:
        for rest in arg_array[1:]:
            thetext=thetext+rest+" "
    else:
        for rest in arg_array[0:]:
            thetext=thetext+rest+" "
            opt="standard"
    
    thetext=thetext.rstrip(" ")
    
    channel = weechat.buffer_get_string(buffer, "localvar_channel")
    server = weechat.buffer_get_string(buffer, "localvar_server")
    weechat.hook_process("figlet -w " + weechat.config_get_plugin("text_width") + " -f " + opt + " '" + thetext + "'",
                         2000,
                         "figlet_return",
                         "{};{}".format(server, channel))

    return weechat.WEECHAT_RC_OK

def figlet_return(data, command, return_code, out, err):
    lines = out.split("\n")
    figlet_line("{}\n{}".format(data, out), len(lines) - 1)
    weechat.hook_timer(1000, 0, len(lines) - 1, "figlet_line", "{}\n{}".format(data, out))
    return weechat.WEECHAT_RC_OK

def figlet_line(data, remaining_calls):
    lines = data.split("\n")
    data = lines.pop(0)
    line = lines[-int(remaining_calls) - 1]
    if len(line) > 1 and line[0] == '/':
        line = '/' + line
    weechat.hook_signal_send("irc_input_send",
                             weechat.WEECHAT_HOOK_SIGNAL_STRING,
                             "{};2;;{}".format(data, line))
    return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
        for option, default_value in settings.iteritems():
            if weechat.config_get_plugin(option) == "":
                weechat.config_set_plugin(option, default_value)
        weechat.hook_command(SCRIPT_NAME, SCRIPT_DESC, '', 
        'Usage:\n'
        'The argument [font] shown below is an optional argument\n'
        '/figlet list - Lists available fonts in figlet directory\n'
        '/figlet example [font] [text] - Show example macro in server buffer.\n'
        '/figlet [text] - Scrolls macro of [text] to channel buffer using default font\n'
        '/figlet [font] [text] - Scrolls macro of [text] using [font] to channel buffer\n'
        '\n'
        'Examples:\n'
        '/figlet hello\n'
        '/figlet smkeyboard hello\n', 
        'list'
        '|| example %(figlet_completion)'
        '|| %(figlet_completion)', 'macro', '')
        #weechat.prnt("", list())
        list()
        weechat.hook_completion("figlet_completion", "list of fonts in figlet fonts", "figlet_completion", "")
