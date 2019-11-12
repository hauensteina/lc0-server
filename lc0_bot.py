#!/usr/bin/env python

# /*********************************
# Filename: lc0_bot.py
# Creation Date: Nov, 2019
# Author: AHN
# **********************************/
#
# A wrapper to allow clients to communicate with lc0 over http.
# Simply forward the command to lc0 and return the result.
#

from pdb import set_trace as BP
import os, sys, re
import numpy as np
import signal
import time

import subprocess
from threading import Thread,Lock,Event
import atexit

g_response = ''
g_handler_lock = Lock()
g_response_event = Event()

TIMEOUT = 10 # seconds
#===========================
class LC0Bot:
    # Listen on a stream in a separate thread until
    # a line comes in. Process line in a callback.
    #=================================================
    class Listener:
        #------------------------------------------------------------
        def __init__( self, stream, result_handler, error_handler):
            self.stream = stream
            self.result_handler = result_handler

            #--------------------------------------
            def wait_for_line( stream, callback):
                global g_response
                global g_handler_lock
                global g_response_event
                #global g_win_prob
                while True:
                    line = stream.readline().decode()
                    if line:
                        result_handler( line)
                    else: # probably my process died
                        error_handler()
                        break

            self.thread = Thread( target = wait_for_line,
                                  args = (self.stream, self.result_handler))
            self.thread.daemon = True
            self.thread.start()

    #--------------------------------------
    def __init__( self, leela_cmdline):
        self.leela_cmdline = leela_cmdline
        self._start_leelaproc()
        atexit.register( self._kill_leela)

    #------------------------------
    def _start_leelaproc( self):
        print('starting lc0')
        proc = subprocess.Popen( self.leela_cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
        listener = LC0Bot.Listener( proc.stdout,
                                    self._result_handler,
                                    self._error_handler)
        self.leela_proc = proc
        self.leela_listener = listener
        self._leelaCmd( 'uci')
        self._leelaCmd( 'setoption name backend value cudnn-fp16')
        self._leelaCmd( 'setoption name VerboseMoveStats value true')

    #-------------------------
    def _kill_leela( self):
        try:
            os.kill( self.leela_proc.pid, signal.SIGKILL)
            print( 'killing old leela')
        except:
            print( 'nothing to kill')

    # Pass through the reply.
    #---------------------------------------------
    def _result_handler( self, leela_response):
        # print( leela_response)
        global g_response
        global g_response_event
        # We accumulate responses until a line starting with 'bestmove' comes in
        g_response += leela_response
        if leela_response.startswith( 'bestmove '):
            g_response_event.set()

    # Resurrect a dead Leela
    #---------------------------
    def _error_handler( self):
        #print( '>>>>>>>>> err handler')
        global g_handler_lock
        with g_handler_lock:
            print( 'Leela died. Resurrecting.')
            self._kill_leela()
            self._start_leelaproc()
            print( 'Leela resurrected')

    # Send a command to leela
    #--------------------------------------------------
    def _leelaCmd( self, cmdstr):
        cmdstr += '\n'
        p = self.leela_proc
        p.stdin.write( cmdstr.encode('utf8'))
        p.stdin.write( 'isready\n'.encode('utf8'))
        p.stdin.flush()
        #print( '--> ' + cmdstr)

    # This gets called from an endpoint to send a command.
    # The only accepted command is 'position', e.g.
    # position startpos move e2e4 c7c5 .
    # The position command gets augmented into
    # ucinewgame; position startpos move e2e4 c7c5; go nodes <nodes>
    # where nodes is a separate parameter.
    # We return the reply from lz0 unmodified as soon as a lines starting with
    # 'bestmove' comes in.
    #--------------------------------------------------------
    def send_cmd( self, content ):
        global g_response
        global g_response_event

        cmds = content['cmds']
        nodes = content.get( 'nodes', 1)

        g_response = ''
        for cmd in cmds:
            print( cmd)
            self._leelaCmd( cmd)
        # Hang until the move comes back
        print( '>>>>>>>>> waiting')
        success = g_response_event.wait( TIMEOUT)
        if not success: # I guess leela died
            print( 'error: leela response timeout')
            self._error_handler()
            return None
        #time.sleep(2)
        #print( 'reponse: ' + str(g_response))
        if g_response:
            res = g_response
            #print( '>>>>>>>>> cleared event')
            g_response_event.clear()
        g_response = None
        print( 'leela says: %s' % str(res))
        return res
