# 
# This file is part of the S370BALEdt distribution.
# Copyright (c) 2021 James Salvino.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
# This is a primitive line editor
# designed for coding IBM S370 BAL source.
#
# You can also call the S370BALAsm or
# the S370BALEmulator so it's almost
# an IDE (edit - assemble - emulate
# all in one place)
#
# Programmers actually used a line editor
# similar to this one over 40 years ago.
#
# Using the TAB key you can format
# your assembler source for the
# expected column layout of:
# 1     10       16
# label mnemonic operands  [optional comment]
#
# For example, you can type:
# balr[TAB KEY]r12,0
#
# to add this line:
#          BALR  R12,0
#
# Another example, you can type:
# loop[TAB KEY]mvi[TAB KEY]0(r5),c'0'
#
# to add this line:
# LOOP     MVI   0(R5),C'0'
#
# A line that starts with an '*' is
# assumed to be a comment
#
# A line with no TAB charaters
# is assumed to be an editor command.
#
# For example, if you typed:
#
# list
#
# an enumerated source listing would be 
# displayed.
#
# See the function doHelp for
# a list of supported commands
#

import os

# --------------------
# global variables
# --------------------

lines = []             # holds the source code
insert_after = 999999  # more or less a current line pointer
filename_save = ''     # provide a default filename

# --------------------
# functions
# --------------------

def doCmd(cmd):
    global lines, filename_save, insert_after
    print(f'cmd : {cmd}')
    if cmd == 'LIST':
        for (num, line) in enumerate(lines):
            print(f'{num:>8} {line}')
    elif cmd == 'QUIT':
        return False
    elif cmd == 'SAVE' or cmd == 'READ':
        file_read_write(cmd)
    elif cmd == 'ASSM':
        os.system(f'python3 S370BALAsm.py {filename_save}')
    elif cmd == 'EMUL':
        want_debug = input('Enter -debug for debug run ')
        os.system(f'python3 S370BALEmulator.py {want_debug}')
    elif cmd == 'HELP':
        doHelp()
    elif cmd.startswith('I'):
        insert_after = int(cmd[1:]) + 1
    elif cmd.startswith('D'):
        begin_end = cmd[1:].split(',')
        if len(begin_end) == 1:
            del lines[int(begin_end[0])]
        else:
            begin = int(begin_end[0])
            end = int(begin_end[1]) + 1
            for i in range(begin,end):
                del lines[begin]
    elif cmd.startswith('E'):
        del lines[int(cmd[1:])]
        insert_after = int(cmd[1:])
    elif cmd.startswith('C'):
        if cmd[1:].count(',') == 1:
            (source, dest) = cmd[1:].split(',')
            insert_after = int(dest)
            doAdd(lines[int(source)])
        else:
            (begin, end, dest) = cmd[1:].split(',')
            insert_after = int(dest) + 1
            for i in range(int(begin),int(end)+1):
                doAdd(lines[i])
    elif cmd.startswith('M'):
        if cmd[1:].count(',') == 1:
            (source, dest) = cmd[1:].split(',')
            source_int = int(source)
            dest_int = int(dest)
            popped = lines.pop(source_int)
            insert_after = dest_int if source_int < dest_int else dest_int+1
            doAdd(popped)
        else:
            (begin, end, dest) = cmd[1:].split(',')
            begin_int = int(begin)
            end_int = int(end)
            dest_int = int(dest)
            popped = [lines.pop(begin_int) for i in range(begin_int,end_int+1)]
            insert_after = dest_int-len(popped)+1 if begin_int < dest_int else dest_int+1
            for line in popped:
                doAdd(line)
    elif cmd.startswith('G'):
        (linenum, before, after) = cmd[1:].split('/')
        if linenum == '*':
            lines = [l.replace(before, after) for l in lines]
        else:
            lines[int(linenum)] = lines[int(linenum)].replace(before, after)
    else:
        print('Unknown Command Entered')

    return True


def file_read_write(oper):
    global lines, filename_save, insert_after

    if oper == 'SAVE':
        filename = input(f'save as[{filename_save}].. ')
    else:
        filename = input(f'read what[{filename_save}].. ')
        after_what_line = input('after what line.. ')

    if filename == '':
        filename = filename_save
    else:
        filename_save = filename

    if oper == 'SAVE':
        with open(filename,'w') as fo:
            fo.write('\n'.join(lines)+'\n')
    else:
        with open(filename,'r') as fi:
            if after_what_line == '':   
                lines = [l.rstrip('\n') for l in fi]
            else:
                insert_after = int(after_what_line) + 1
                for l in fi:
                    doAdd(l.rstrip('\n'))

    return


def doAdd(line):
    global lines, insert_after

    if insert_after == 999999:
        lines.append(line)
    else:
        lines.insert(insert_after, line)
        insert_after += 1

    return


def doHelp():
    print('*********************************************')
    print('LIST - list source file')
    print('READ - read in source file overlaying what is')
    print('       there or inserting after certain line')
    print('SAVE - write out source file')
    print('ASSM - assemble source file with S370BALAsm')
    print('EMUL - run emulation with S370BALEmulator')
    print('HELP - display help text')
    print('QUIT - quit this program')
    print(' ')
    print('Edit Commands:')
    print('In1 - insert next line after line n1')
    print('Dn1 - delete line n1')
    print('Dn1,n2 - delete lines n1 to n2 (Block Delete)') 
    print('En1 - replace line n1 with next line entered')
    print('Cn1,n2 - copy line n1 after line n2')
    print('Cn1,n2,n3 - copy lines n1 to n2 after line n3 (Block Copy)')
    print('Mn1,n2 - move line n1 after line n2')
    print('Mn1,n2,n3 - move lines n1 to n2 after line n3 (Block Move)')
    print('Gn1/aaa/bbb - on line n1 change text aaa to bbb')
    print('*********************************************')

    return


# --------------------
# main starts here
# --------------------

os.system('clear')

print('-------------------------')
print('Welcome to S370BALEdt')
print('type HELP for a help menu')
print('-------------------------')
print(' ')

while True:
    inp = input('> ').upper().split('\t')

    if len(inp) == 1:
        if inp[0].startswith('*'):
            doAdd(inp[0])
            continue
        if doCmd(inp[0]):
            continue
        else:
            break
    elif len(inp) == 2:
        label = ''
        (mnemonic,operands) = inp
    else:
        (label,mnemonic,operands) = inp

    if operands.find('*',2) != -1:
        (operand, comment) = operands.rsplit('*',1)         
        operands = f'{operand:<34}*{comment}' 

    doAdd(f'{label:9}{mnemonic:6}{operands}')
