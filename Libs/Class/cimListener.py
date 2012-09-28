#!/usr/bin/python
#
# Simple indication receiver using Twisted Python.  
#
# Requires Twisted Python and 
#

import sys,os
sys.path.append('c:\cim_test\libs')
sys.path.append('c:\cim_test\libs\class')
import cim,baselib
import xml.etree.ElementTree

from twisted.internet import reactor
from twisted.internet import task
from twisted.web import server, resource
import pywbem
import threading,time
from multiprocessing import Process,Queue

from twisted.internet import reactor
#from twisted.python import loghelp

from time import sleep

class CIMListener(object):
    """ CIM Listener
    """

    isLeaf = 1



    def __init__(self, timeout=3, http_port=59900,q=None,timeoutS=60):
        timeoutS=int(timeoutS)
        #self.callback = callback
        self.http_port = http_port
        site = server.Site(self)
        self.timeout=timeoutS
        
        self.q=q
        self.q.put("queue content inited")
                
        
        #cim.cimBase().writeHtml('info',   "__init__ subrountine")
        #cim.cimBase().writeHtml('info',   'self.q is {}'.format(q))
        
        self.datagramRecieved = False
        self.rvMsg=''
        self.timeout = timeoutS # One second

        if self.http_port and self.http_port > 0:
            reactor.listenTCP(self.http_port, site)




    def run(self):
        self.datagramRecieved=False
        l = task.LoopingCall(self.hasTimeout)
        cim.cimBase().writeHtml('info',"timeout is {} sec".format(self.timeout)  ) 
        l.start(self.timeout)        
        cim.cimBase().writeHtml('info',   "queue is filling \'queue content started\'")
        cim.cimBase().writeHtml('info',   'reactor is running')
        while self.q.qsize()>0:
            self.q.get()
        self.q.put("queue content started")
        reactor.run()
        
        
        

    def hasTimeout(self):
        cim.cimBase().writeHtml('info',   'run cimListener.hasTimeout()')
                                
        if (not self.datagramRecieved) and reactor._started:    
            reactor.stop()
            cim.cimBase().writeHtml('info',   'reactor stopped because timeout.')

            #empty the queue
            while self.q.qsize()>0:
                self.q.get()
            
            self.q.put('listener got data timeout')
            

                
    
    def render(self, request):
        print '----------------------------------------------------------------'
        cim.cimBase().writeHtml('info',  'Indication Received')
        #print '----------------------------------------------------------------'
        rtn=request.content.read()
        self.rvMsg += rtn
        self.datagramRecieved=True
        self.done()
        
    
    def done(self):
        if (self.datagramRecieved) and (reactor._started):           
                reactor.stop()
                cim.cimBase().writeHtml('info',   'reactor stopped because indication msg received.')            
                cim.cimBase().writeHtml('info',   'received len {}'.format(len(self.rvMsg)))
                #empty the queue
                while self.q.qsize()>0:
                    self.q.get()
                #f=open('./tmpCimResponse','w')
                #f.write(self.rvMsg)
                #f.close()
                
                x=xml.etree.ElementTree.fromstring(self.rvMsg)
                self.q.put(x)                    

                #self.q.put(self.rvMsg[:5120])

                cim.cimBase().writeHtml('info',   'fill the Queue with indication msg')
                #reset for next loop
                #self.datagramRecieved = False
                #return        





def s(name,q,timeoutS):
    baselib.initLogger(__name__,'./Report/att.log')
    spid= os.getpid()
    cim.cimBase().writeHtml('info','socket {} process id: {}'.format(name,spid))
    
    #a=SocketR()
    #rtn=a.run()
    
    a=CIMListener(q=q,timeoutS=timeoutS)
    rtn=a.run()

if __name__ == '__main__':
    #def cb(inst):
    #    print inst.tomof()
    cl = CIMListener()
    cl.timeout=100
    q=Queue()
    cl.q=q
    cl.run()
    
