#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
Some const and simple wrap of the ascii char to terminal. It include
the color and font style, the IAC , the cursor control and some
keycode.
'''

# Color

esc = '\x1b'

w = lambda code: '\x1b[' + str(code) +'m'

reset   = w(0)

black   = w(30)
red     = w(31)
green   = w(32)
yellow  = w(33)
blue    = w(34)
magenta = w(35)
cyan    = w(36)
white   = w(37)

delay = lambda x : '\x1b[%dM' % x

font = {
    None:'',
    "black":black,
    "red":red,
    "green":green,
    "yellow":yellow,
    "blue":blue,
    "magenta":magenta,
    "cyan":cyan,
    "white":white,
    }

bg_black   = w(40)
bg_red     = w(41)
bg_green   = w(42)
bg_yellow  = w(43)
bg_blue    = w(44)
bg_magenta = w(45)
bg_cyan    = w(46)
bg_white   = w(47)
bg_default = w(49)

background = {
    None:'',
    "black":bg_black,
    "red":bg_red,
    "green":bg_green,
    "yellow":bg_yellow,
    "blue":bg_blue,
    "magenta":bg_magenta,
    "cyan":bg_cyan,
    "white":bg_white,
    "default":bg_default,
    }

bold       = w(1)
underscore = w(4)
inverted   = w(7)
italic     = w(3)
blink      = w(5)

outlook = lambda *x : '\x1b[%sm' % ';'.join(x)

art_code = {
    "black":"30","red":"31","green":"32","yellow":"33","blue":"34",
    "magenta":"35","cyan":"36","white":"37","default":"39",
    "bg_black":"40","bg_red":"41","bg_green":"42","bg_yellow":"44","bg_blue":"44",
    "bg_magenta":"45","bg_cyan":"46","bg_white":"47","bg_default":"49",
    "bold":"1","underscore":"4","italic":"3","inverted":"7","blink":"5",
    "reset":"0",
    }

# Control characters

bell = chr(7)

# IAC and her firends

print_ab = chr(32)

IAC  = chr(255) # "Interpret As Command"
DO   = chr(253)
WONT = chr(252)
WILL = chr(251)
theNULL = chr(0)

SE  = chr(240)  # Subnegotiation End
NOP = chr(241)  # No Operation
DM  = chr(242)  # Data Mark
BRK = chr(243)  # Break
IP  = chr(244)  # Interrupt process
AO  = chr(245)  # Abort output
AYT = chr(246)  # Are You There
EC  = chr(247)  # Erase Character
EL  = chr(248)  # Erase Line
GA  = chr(249)  # Go Ahead
SB =  chr(250)  # Subnegotiation Begin

BINARY = chr(0) # 8-bit data path
ECHO = chr(1) # echo
RCP = chr(2) # prepare to reconnect
SGA = chr(3) # suppress go ahead
NAMS = chr(4) # approximate message size
STATUS = chr(5) # give status
TM = chr(6) # timing mark
RCTE = chr(7) # remote controlled transmission and echo
NAOL = chr(8) # negotiate about output line width
NAOP = chr(9) # negotiate about output page size
NAOCRD = chr(10) # negotiate about CR disposition
NAOHTS = chr(11) # negotiate about horizontal tabstops
NAOHTD = chr(12) # negotiate about horizontal tab disposition
NAOFFD = chr(13) # negotiate about formfeed disposition
NAOVTS = chr(14) # negotiate about vertical tab stops
NAOVTD = chr(15) # negotiate about vertical tab disposition
NAOLFD = chr(16) # negotiate about output LF disposition
XASCII = chr(17) # extended ascii character set
LOGOUT = chr(18) # force logout
BM = chr(19) # byte macro
DET = chr(20) # data entry terminal
SUPDUP = chr(21) # supdup protocol
SUPDUPOUTPUT = chr(22) # supdup output
SNDLOC = chr(23) # send location
TTYPE = chr(24) # terminal type
EOR = chr(25) # end or record
TUID = chr(26) # TACACS user identification
OUTMRK = chr(27) # output marking
TTYLOC = chr(28) # terminal location number
VT3270REGIME = chr(29) # 3270 regime
X3PAD = chr(30) # X.3 PAD
NAWS = chr(31) # window size
TSPEED = chr(32) # terminal speed
LFLOW = chr(33) # remote flow control
LINEMODE = chr(34) # Linemode option
XDISPLOC = chr(35) # X Display Location
OLD_ENVIRON = chr(36) # Old - Environment variables
AUTHENTICATION = chr(37) # Authenticate
ENCRYPT = chr(38) # Encryption option
NEW_ENVIRON = chr(39) # New - Environment variables
# the following ones come from
# http://www.iana.org/assignments/telnet-options
# Unfortunately, that document does not assign identifiers
# to all of them, so we are making them up
TN3270E = chr(40) # TN3270E
XAUTH = chr(41) # XAUTH
CHARSET = chr(42) # CHARSET
RSP = chr(43) # Telnet Remote Serial Port
COM_PORT_OPTION = chr(44) # Com Port Control Option
SUPPRESS_LOCAL_ECHO = chr(45) # Telnet Suppress Local Echo
TLS = chr(46) # Telnet Start TLS
KERMIT = chr(47) # KERMIT
SEND_URL = chr(48) # SEND-URL
FORWARD_X = chr(49) # FORWARD_X
PRAGMA_LOGON = chr(138) # TELOPT PRAGMA LOGON
SSPI_LOGON = chr(139) # TELOPT SSPI LOGON
PRAGMA_HEARTBEAT = chr(140) # TELOPT PRAGMA HEARTBEAT
EXOPL = chr(255) # Extended-Options-List
NOOPT = chr(0)

#Codes used in SB SE data stream for terminal type negotiation
IS = chr(0)
SEND = chr(1)

# Wrap for command

CMD_CHAR_PER =  IAC+WILL+ECHO + IAC+WILL+SGA + IAC+DO+BINARY
CMD_LINEMODE = IAC+WONT+ECHO + IAC+WONT+SGA# + IAC+WILL+LINEMODE

# Cursor

move_up_n    = lambda l : '\x1b[%dA' % l
move_down_n  = lambda l : '\x1b[%dB' % l
move_right_n = lambda r : '\x1b[%dC' % r
move_left_n  = lambda r : '\x1b[%dD' % r

move0 = '\x1b[H'
movex = lambda x : '\x1b[%d%c' % (abs(x),'D' if x<0 else 'C')
movey = lambda y : '\x1b[%d%c' % (abs(y),'A' if y<0 else 'B')
movey_1 = '\x1b[B'
movey_p = '\x1b[A'
movey_n = '\x1b[B'
movex_f = '\x1b[C'
movex_d = '\x1b[D'
save =    '\x1b[s'
restore = '\x1b[u'
clear0 = '\x1b[0j'
clear1 = '\x1b[J'
clear_2 =   '\x1b[2J'
clear = move0 + clear_2
clear_l = '\x1b[k'
move2 = lambda x,y : '\x1b[%d;%dH' % (x,y)

insert1 = '\x1b[1L'
insertn = lambda x : '\x1b[%dL' % x

line_beginning = '\r'

# KeyCode

k_up = '\x1b[A'
k_down = '\x1b[B'
k_right = '\x1b[C'
k_left = '\x1b[D'

k_page_up = '\x1b[5~'
k_page_down = '\x1b[6~'

k_home = '\x1b[1~'
k_end = '\x1b[4~'

k_cp = lambda c : chr(ord(c)-96)
k_ctrl_a = k_cp('a')
k_ctrl_w = k_cp('w')
k_ctrl_h = k_cp('h')
k_ctrl_e = k_cp('e')
k_ctrl_l = k_cp('l')
k_ctrl_b = k_cp('b')
k_ctrl_f = k_cp('f')
k_ctrl_c = k_cp('c')
k_ctrl_z = k_cp('z')
k_ctrl_g = k_cp('g')
k_ctrl_d = k_cp('d')
k_ctrl_r = k_cp('r')
k_ctrl_p = k_cp('p')
k_ctrl_n = k_cp('n')
k_ctrl_u = k_cp('u')
k_ctrl_s = k_cp('s')
k_ctrl_v = k_cp('v')
k_ctrl_t = k_cp('t')
k_ctrl_y = k_cp('y')
k_ctrl_q = k_cp('q')
k_ctrl_x = k_cp('x')
k_ctrl_k = k_cp('k')
k_ctrl_f2 = '\x1b[12~'
k_ctrl_S2 = '\x00'
k_ctrl_S6 = '\x1e'
k_ctrl_m = k_cp('m')
k_ctrl_be = '\x1c'  # '\'
k_c_a = '\x01'
k_c_b = '\x02'
k_c_c = '\x03'
k_c_h = '\x08'
k_c_p = k_cp('p')

k_del = chr(127)
k_delete = '\x1b[3~'
k_backspace = chr(8)

k_enter_linux = chr(13)
k_enter_window = chr(10)

ks_finish = set(('\n','\r\n','\r','\r\x00'))

backspace = k_left+ ' '+k_left

kill_line = '\x1b[K'
kill_to_end = '\x1b[K'

import string

printable = set(chr(x) for x in range(32,127))

is_chchar = lambda data : all( c >= u'\u4e00' and c <= u'\u9fa5' for c in data)
is_safe_char = lambda data : \
    (data[0] >= u' ')  and \
    ((data[0] <= u'~') or (data[0] > u'\xff'))
is_alnum = lambda d : ('0'<=d<='9') or ('a'<=d<='z') or ('A'<=d<='Z')

from unicodedata import east_asian_width

srcwidth = lambda x : 2 if east_asian_width(x) in "FAW" else 1
