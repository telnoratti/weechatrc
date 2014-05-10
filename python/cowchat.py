#############################################################################
# Weechat cowsay plugin, sends messages with a low priority in the current
# buffer, used /cowchat <cowfile> <message>
#
# Written by telnoratti <telnoratti@telnor.org>
# 
# Copyright (c) 2013, Telnor Institute
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

SCRIPT_NAME        = "cowchat"
SCRIPT_AUTHOR    = "Calvin Winkowski <telnoratti@gmail.com>"
SCRIPT_VERSION    = "1.2"
SCRIPT_DESC        = "Wrapper to post cowsays into buffers."
SCRIPT_LICENSE    = "BSD"

import weechat
import re

pat = re.compile(r'([\'&"$#])')

weechat.register("cowchat", "cowchat", "1.1", "BSD", "Cowchat!", "", "utf-8")

def cowcall(data, buffer, args):
    cowfile, sep, say = args.partition(" ")
    if cowfile == "" or say == "":
        return weechat.WEECHAT_RC_ERROR
    say = re.sub(pat, r'\\\1', say)
    channel = weechat.buffer_get_string(buffer, "localvar_channel")
    server = weechat.buffer_get_string(buffer, "localvar_server")
    weechat.hook_process("cowsay -f {} {}".format(cowfile, say),
                         2000,
                         "cowchat",
                         "{};{}".format(server, channel))
    return weechat.WEECHAT_RC_OK

def cowchat(data, command, return_code, out, err):
    if return_code != 0:
        weechat.prnt(weechat.current_buffer(), "Cowchat error: {0}".format(return_code))
        for line in err.split("\n")[:-1]:
            weechat.prnt(weechat.current_buffer(), line)
        return weechat.WEECHAT_RC_ERROR
    lines = out.split("\n")
    cowchat_line("{}\n{}".format(data, out), len(lines) - 1)
    weechat.hook_timer(2000, 0, len(lines) - 1, "cowchat_line", "{}\n{}".format(data, out))
#    for line in out.split("\n"):
#        if len(line) > 1 and line[0] == '/':
#            line = '/' + line
#        weechat.hook_signal_send("irc_input_send", weechat.WEECHAT_HOOK_SIGNAL_STRING,
#                                 "{};2;;{}".format(data, line))
    return weechat.WEECHAT_RC_OK

def cowchat_line(data, remaining_calls):
    lines = data.split("\n")
    data = lines.pop(0)
    line = lines[-int(remaining_calls) - 1]
    if len(line) > 1 and line[0] == '/':
        line = '/' + line
    weechat.hook_signal_send("irc_input_send",
                             weechat.WEECHAT_HOOK_SIGNAL_STRING,
                             "{};2;;{}".format(data, line))
    return weechat.WEECHAT_RC_OK


hook = weechat.hook_command("cowchat", "Pastes a cowsay into the current buffer",
                            "word | text",
                            "<cow> <say>",
                            "",
                            "cowcall", "")
