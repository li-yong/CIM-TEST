import sys
sys.path.append('./Libs')
sys.path.append('./Libs/Class')

import cim,tInvokeMethod,baselib,cimListener,smisTest,tInstProp
import unittest,tcParser,HTMLTestRunner,re,pickle,os
import logging, __builtin__
from optparse import OptionParser
import threading,datetime
from multiprocessing import Process,Queue
from xml.sax import saxutils

class ThreadClass(threading.Thread):
    def __init__(self,testDict,mode):
        self.testDict=testDict
        self.mode=mode
        threading.Thread.__init__(self)
    def run(self):
        threadName=self.getName()
        threadObj=self
        now = datetime.datetime.now()
        #print "%s says Hello World at time: %s" % (threadName, now)
        testDict=self.testDict
        if self.mode=='iniIm':
            fP='./Tests/Ini/Im/'
            runIniCase(testDict,fP,threadName,threadObj)
        elif self.mode=='iniProp':
            fP='./Tests/Ini/Prop/'
            runIniCase(testDict,fP)
        elif self.mode=='py':
            fP='./Tests/Py/'
            runPyCase(testDict,fP)
if __name__ == '__main__':
 
    baselib.initLogger(__name__,'./Report/att.log')
    
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser = OptionParser()
    
    
    defaultCimSrv='http://10.32.191.225:5988'
    defaultNs='root/emc'
    defaultUsr='admin'
    defaultPwd='#1Password'
        
    
    #namespace
    parser.add_option("-s", "--cimsrv", help="cim server https connection [default: %default]",default=defaultCimSrv,dest="cimsrv")
    parser.add_option("-u", "--username",help="cim user [default: %default]",default=defaultUsr,dest="cimusr")
    parser.add_option("-p", "--password",help="cim password [default: %default]",default=defaultPwd,dest="cimpwd")
    parser.add_option("-n", "--namespace", help="namespace used [default: %default]",default=defaultNs,dest="cimns")
    
    
    parser.add_option("-v", "--verbose",action="store_true", dest="verbose", default=True, help="put more information")
    
    parser.add_option("-w", "--htmlReport", default="yes", choices=('yes','no'),help="Generate Html Report.(less console output)")
    parser.add_option("-i", "--indication", default="no", choices=('yes','no'),help="enable indication test")
    
    parser.add_option("-m", "--mode", default="iniProp",  choices=('iniIm','iniProp','py'),   help="Ini or python test "  "[default: %default]")
    
    parser.add_option("-t", "--tests", dest="tests",    help="test to be run.")
    
    parser.add_option("-r", "--threadsNum", dest="threadsNum", help="run in multiThreads [default: %default]",default="1",)
    

    
    
    def startListen():
        '''run listener in a new process'''
        mpid=os.getpid()
        cim.cimBase().writeHtml('info', 'main process id:{}'.format(mpid))
        cim.cimBase().writeHtml('info', "listener process start listen"  )
        
        q=Queue()
        timeoutS=10000
        p1 = Process(target=cimListener.s, args=('1',q,timeoutS))
        p1.start()
        cim.cimBase().writeHtml('info', "listener process started")
        return p1    
    
    def stopListen(p):
        '''stop listener in a new process''' 
        cim.cimBase().writeHtml('info', 'cim.stopListen(): waiting the listener process to join')
        #p.join()
        p.terminate()
        cim.cimBase().writeHtml('info', "listener process joined")
    
    def runIniCase(testDict,fP,threadName,threadObj):
        for suite, testsList in testDict.iteritems():
            tFList=[]
            for i in testsList:
                tF=fP+suite+'/'+i+'.ini'
                tFList.append(tF)
            smisTest.start(tFList,threadName,threadObj)
            
            
    def runPyCase(testDict,fP):
        for suite, testsList in testDict.iteritems():
            tFList=[]
            for i in testsList:
                tF=fP+suite+'/'+i+'.ini'
                sys.path.append(fP+suite+'/')
                str='import '+i
                exec(str)
                tL=unittest.TestLoader()
                s=tL.loadTestsFromTestCase(t.TestSample)
                
        if __builtin__.htmlReport==False:
            rst=unittest.TextTestRunner(verbosity=5).run(s)
    
        if __builtin__.htmlReport==True:
            fp = file('./Report/att.html', 'wb')
            runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title='SMI-S Component test',
                description='Branding Description'
                )
            #__builtin__.htmlReporter=runner
            rst=runner.run(s)
            


    (options, args) = parser.parse_args()
    
    cntOpt={'cimsrv':options.cimsrv,'cimusr':options.cimusr,'cimpwd':options.cimpwd,'cimns':options.cimns}
    for k,v in cntOpt.iteritems():
        os.environ.__setitem__(k,v)
        
    if options.indication=='yes':
        __builtin__.indication=True
        p=startListen()
    
    if options.htmlReport=='yes':
        __builtin__.htmlReport=True
        __builtin__.resultG=dict() #for generate html report
        __builtin__.testG=dict()   #for generate html report
        __builtin__.stringIoG=dict()   #for generate html report
        
      
        

    elif options.htmlReport=='no':
        __builtin__.htmlReport=False
    
    
    testDict=baselib.parseTest(options.tests)            
      
            
            
    tList=[]

    
    for i in range(int(options.threadsNum)):
        t = ThreadClass(testDict,options.mode)
        tList.append(t)
        t.start()
       #t.join() #the thread (case )will be run one by one, not simultaneously
          
    for t in tList: #the thread (case )run simultaneously
        t.join()
        
        
    if options.indication=='yes':
        stopListen(p)
    
    if __builtin__.htmlReport:
        #generate HTML report
        allTests=unittest.TestSuite()
        allTestResults=HTMLTestRunner._TestResult()
        
        
        allResult=[]
        allSuccess_count=0
        allfailure_count=0
        allerror_count=0
        
    
        
        threadList= __builtin__.resultG.keys()
        threadList.reverse() #let report show in Thread1, 2, 3 sequence from top to bottom
        for i in threadList:        
            test=__builtin__.testG[i]
            result=__builtin__.resultG[i]
            for b in result.result:
                allResult.append(b)
                
            allSuccess_count+=result.success_count 
            allfailure_count+=result.failure_count 
            allerror_count+=result.error_count 
            
            
        allTestResults.result=allResult
        allTestResults.success_count=allSuccess_count
        allTestResults.failure_count=allfailure_count
        allTestResults.error_count=allerror_count
        
        
        __builtin__.htmlReporter.generateReport(None, allTestResults)
    

    exit(0)