import sys, logging
sys.path.append('..\..\libs')
sys.path.append('..\..\libs\class')
import unittest,tcParser,cim,HTMLTestRunner,re,pickle,os,baselib,time
from configobj import ConfigObj
from datetime import datetime

logger = logging.getLogger(__name__)

#tInvokeMethod is used to run 'section' in ini files
class tInvokeMethod(cim.cimBase):
    
    def __init__(self,methodName,tcObj,methodDoc=None,threadName=None):
        #map methodName to self.mainMethod.  MethodName is the testcase name.
        setattr(self,methodName,self.mainMethod)
        unittest.TestCase.__init__(self, methodName)
        #self.writeHtml("info", "Class tInvokeMethod __init__,one class Instance created, tc is {}".format(methodName))
        self.methodName=methodName
        self.tcObj=tcObj
        self.threadName=threadName
        #self.cnt=cim.cimBase().connect()
        
        cimsrv=os.getenv('cimsrv')
        cimusr=os.getenv('cimusr')
        cimpwd=os.getenv('cimpwd')
        cimns=os.getenv('cimns')        
        
        self.cnt=baselib.connect(cimsrv,cimusr,cimpwd,cimns)
        self.cntInterop=baselib.connect(cimsrv,cimusr,cimpwd,'interop')

        
        if methodDoc:
            self._testMethodDoc=methodDoc
        

    def mainMethod(self):
        str="===Executing test:{}===".format(self.methodName)
        #print "RYAN"+str
        self.writeHtml("info",str)
        
        #self.tcObj is section of [setup], [execute], or [teardown]
        sections=self.tcObj.sections
        
        if 'init' in sections:
            self.writeHtml("info",self.tcObj['init']['note'])

            for i in self.tcObj['init'].scalars:
                varName=i
                varValu=self.tcObj['init'][varName]
                varValu2=self.translateVar(varValu)                
                self.saveConfVar(varName,varValu2)
            
            

        #k will be subsections of the [setup/execute/teardown],
        #  such as [[Action3:astTrue]], [[Action1:print]]
        for k in sections: 
            act=re.match(r'Action\d+(\.)*\d*:\s*(.*)\s*',k)           
            if act:
                theAct=act.group(2)
                tcObjX=self.tcObj[k]
                
                self.showNote(tcObjX)
                
                
                secBfrExe=secAftExe=0
                fR=1
                
                if 'SleepBeforeExe' in tcObjX.scalars:
                    secBfrExe=float(tcObjX['SleepBeforeExe'])
                
                if 'SleepAfterExe' in tcObjX.scalars:
                    secAftExe=float(tcObjX['SleepAfterExe'])
                    
                if 'reTryOnFail' in tcObjX.scalars:
                    fR=int(tcObjX['reTryOnFail'])    
                    
                for i in range(0,fR):
                    baselib.sleep(secBfrExe, "sleep before execute")
                    
                    timeStart=datetime.now()
                    
                    if theAct=='InstProp':
                        rv=self.actIp(tcObjX);
                        
                    if theAct=='findInst':
                        rv=self.actFi(tcObjX);
                    
                    if theAct=='chkInstProp':
                        rv=self.actCip(tcObjX);                         
                    
                    if theAct=='emuInstance':
                        rv=self.actEi(tcObjX);
                        
                    if theAct=='InvokeMethod':
                        rv=self.actIm(tcObjX)
                        
                    if theAct=='queryInstance':
                        rv=self.actQi(tcObjX)
                        
                    if theAct=='queryAssociator':
                        rv=self.actQa(tcObjX)                  
                    
                    if theAct=='print':
                        rv=self.actPrint(tcObjX) 
                        
                    if theAct=='astTrue':
                        rv=self.actTrue(tcObjX)
                    
                    timeEnd=datetime.now()
                    timeDelta=timeEnd-timeStart
                    
                    self.writeHtml("info","Action Executed, spent time {}".format(timeDelta))
                    
                    baselib.sleep(secAftExe,"sleep after execute")
                    
                    
                    
                    if rv=='FALSE':
                        self.writeHtml("info","Section Result: Failed, retry...")
                    else:
                        self.writeHtml("info","Section Result: PASSED")
                        break
                
                # The [[Action]] still failed even after retry, so fail the testcase [setup/execute/teardown]        
                if rv=='FALSE':
                    errStr=tcObjX.parent.parent.main.filename+","+k+", This Action FAILED"
                    self.writeHtml("error",errStr)

                    raise self.failureException(errStr)


    #end of mainMethod


def testInvokeMethod(cfg):
    #verify=tcParser.tcParser(cfg)
    #verify.parseTest()
    
    verify=ConfigObj(cfg)
    
    suite=unittest.TestSuite()
    
    
    tcSections=verify.sections #the list of testcase in the conf file
    
    tcName=tcSections[0]
    #print tcName 
    
    
    
    #Todo: assert each conf have one cls
    #clsName=verify.tc['Class']['clsname']
    
    for verifyInst in tcSections:
        match=re.match("Test(\d+)",verifyInst)
        if match:
            id=match.group(1)
            oneTc=verify[verifyInst]
            #baselib.parseInvokeMethodTest(oneTc)
            
            tcName=oneTc['TestName']           
            tcObj=tInvokeMethod(tcName,oneTc)
            suite.addTest(tcObj)
    
    
    unittest.TextTestRunner(verbosity=5).run(suite)
   
   
    switch=True
    switch=False    
    if switch:
        fp = file('my_report.html', 'wb')
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title='My unit test',
            description='This demonstrates the report output by HTMLTestRunner.'
            )
        runner.run(suite)
        
    #print 'End of Test'


if __name__ == '__main__':    
    tcConf="C:/cim_test/testcase/ts_pool/testInvokeMethod.conf"
    #tcConf="C:/cim_test/testcase/ts_pool/ts_Common_teardown.ini"
    #tcConf="C:/cim_test/testcase/ts_pool/ts_Common_setup.ini"
    tcConf="C:/cim_test/testcase/ts_pool2/t0_debug.ini"

    testInvokeMethod(tcConf)