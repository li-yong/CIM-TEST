import sys, logging
sys.path.append('..\libs')
sys.path.append('..\libs\class')
import os,unittest,tcParser,cim,HTMLTestRunner,re,pickle,os,baselib,time,tInvokeMethod
import __builtin__
from configobj import ConfigObj

#global suiteG
#suiteG=unittest.TestSuite()
suiteHashG=dict()

#global testListG
testListG=[]

#global tearDownListG
tearDownListG=[]

#global tsuiteList
#tsuiteList=[]
__builtin__.tsuiteList=dict()


logger = logging.getLogger(__name__)

#the class test classes properties as expected.

#tSmis class logic:
#1. expect cSetup.ini as @setupClass, and cTeardown.ini as @tearDownClass
#2. for a ini testcase, map setup/execute/teardown section to each function then run by htmlRunner

class tSmis(cim.cimBase):
        
    def __init__(self,methodName,setupObj=None,exeObj=None,teardownObj=None,threadName=None):
        setattr(self,methodName,self.exeute)
        unittest.TestCase.__init__(self, methodName)
        
        #self.writeHtml("info", "Class tSmis __init__,one class Instance created, tc is {}".format(methodName))
        self.setupObj=setupObj
        self.exeObj=exeObj
        self.teardownObj=teardownObj

        
    @classmethod
    def setUpClass(self):
        dirName=self.dirName
        cfg=self.cfg
        
        cfgSuiteSetup=dirName+'/cSetup.ini'
        if os.path.exists(cfgSuiteSetup):
            #Do not run wjen cfg is cSetup.ini itself.
            if not re.match('.*/cSetup.ini',cfg) and not re.match('.*/cTeardown.ini',cfg):
                rst=runOneIni(cfgSuiteSetup,threadName=self.threadName).runTest();
                if hasattr(rst,'failure_count') and (rst.failure_count > 0):
                    #errStr='Suite level setup failed, file cSetup.ini'
                    raise self.failureException(rst.failures[0])
    
    @classmethod
    def tearDownClass(self):
        #cfg=os.getenv('cfg')
        #dirName=os.getenv('tsPath')
        dirName=self.dirName
        cfg=self.cfg
        cfgSuiteTeardown=dirName+'/cTeardown.ini'
        if os.path.exists(cfgSuiteTeardown):
            if not re.match('.*/cTeardown.ini',cfg) and not re.match('.*/cSetup.ini',cfg):
                rst=runOneIni(cfgSuiteTeardown,threadName=self.threadName).runTest();
                if hasattr(rst,'failure_count') and (rst.failure_count > 0):
                    raise self.failureException(rst.failures[0])
        
    def exeute(self):
        if self.exeObj:

                
            rst=run(self.exeObj,thread=self.threadName)

            
            if hasattr(rst,'failure_count') and (rst.failure_count > 0):
                raise self.failureException(rst.failures[0])
    
    def setUp(self):
        if self.setupObj:

            rst=run(self.setupObj,thread=self.threadName)
            if hasattr(rst,'failure_count') and (rst.failure_count > 0):
                raise self.failureException(rst.failures[0])

    def tearDown(self):
        if self.teardownObj:

            rst=run(self.teardownObj,thread=self.threadName)
            
            if hasattr(rst,'failure_count') and (rst.failure_count > 0):
                raise self.failureException(rst.failures[0])            
        
class runOneIni():
    #dep means it is a depended test, so it's teardown part will be execute later. 
    def __init__(self,cfg,runSecList=["ALL"],dep=False,threadName=None):
        if not os.path.exists(cfg):
            print "WARNING, os path {} does not exist".format(cfg)
        
        self.cfg=cfg
        dirName=os.path.dirname(self.cfg)
        self.dirName=dirName
        self.threadName=threadName
        
        tSuiteN=dirName.split('/')[-1]
        self.tSuiteN=tSuiteN+'_'+self.threadName
        
        self.verify=ConfigObj(cfg)
        self.runSecList=runSecList
        

        
        if runSecList==["ALL"]:
            self.runSecList=['setup','execute','teardown']
        self.dep=dep
            
        self.tcSections=self.verify.sections #the list of testcase in the conf file
        tcName=cfg.split("/")[-1]
        self.tcName=tcName.split('.')[0]
        
        if 'depend' in self.verify.sections:
            secDepend=self.verify['depend']
            for i in secDepend.scalars:
                dpd=secDepend[i]
                runOneIni(dpd,['setup','execute'],True).addTest()
                
        if self.dep:
            secTeardown=self.verify['teardown']
            tcObjT=tInvokeMethod.tInvokeMethod(self.tcName+"_teardown",secTeardown)        
            tearDownListG.insert(0,tcObjT)
            
        
            

        
            
    def _getTestObj(self):
        
        tcObjS=None
        tcObjE=None
        tcObjT=None
        
        if not self.threadName in __builtin__.tsuiteList.keys():
            __builtin__.tsuiteList[self.threadName]=[]
        
        if not hasattr(__builtin__,'clsSMIS'):
            __builtin__.clsSMIS=dict()
           
        if not hasattr(__builtin__,'cls2'):
            __builtin__.cls2=dict()           
        
        if self.tSuiteN in __builtin__.tsuiteList[self.threadName]:
            #cls is for ini section, tInvokeMethod.tInvokeMethod
            cls=__builtin__.cls2[self.threadName]
            
            #clsSMIS is for ini file.
            clsSMIS=__builtin__.clsSMIS[self.threadName]
        else:
            #cim.cimBase().writeHtml("info",  "CREATE CLASS "+self.tSuiteN)
            cls=type(self.tSuiteN,(tInvokeMethod.tInvokeMethod,),{})
            __builtin__.cls2[self.threadName]=cls
            __builtin__.tsuiteList[self.threadName].append(self.tSuiteN)
            
            clsSMIS=type('tSmis_'+self.tSuiteN,(tSmis,),{})
            __builtin__.clsSMIS[self.threadName]=clsSMIS
        
            #assign class variable
            clsSMIS.dirName=self.dirName
            clsSMIS.cfg=self.cfg
            clsSMIS.threadName=self.threadName
            
            
            
                
        if 'setup' in self.runSecList and 'setup' in self.verify.sections:
            secSetup=self.verify['setup']
            doc=None
            if 'doc' in secSetup.scalars:
                doc=secSetup['doc']
            #tcObjS=tInvokeMethod.tInvokeMethod(self.tcName+"_setup",secSetup,doc)
            tcObjS=cls(self.tcName+"_setup"+'_'+self.threadName,secSetup,doc,threadName=self.threadName)
            #tcObjS=eval(tcObjS)
        
        if 'execute' in self.runSecList and 'execute' in self.verify.sections:
            secExec=self.verify['execute']
            tcObjE=cls(self.tcName+"_execute"+'_'+self.threadName,secExec,threadName=self.threadName)
            #print tcObjE
            #tcObjE=eval(tcObjE)
        
        if 'teardown' in self.runSecList and 'teardown' in self.verify.sections:    
            secTeardown=self.verify['teardown']
            tcObjT=cls(self.tcName+"_teardown"+'_'+self.threadName,secTeardown,threadName=self.threadName)
            #tcObjT=eval(tcObjT)
            
        tSmisObj=clsSMIS(self.tcName,tcObjS,tcObjE,tcObjT)
        self.iniFileTestObj=tSmisObj
        #print "\n{} assembed iniObj for file {}".format(self.threadName,self.cfg)
        
    def addTest(self):
        self._getTestObj()
        suiteHashG[self.threadName].addTest(self.iniFileTestObj)

    def runTest(self):
        self._getTestObj()
        rst=run(self.iniFileTestObj,thread=self.threadName)




def run(suite,html=True,thread=None,threadObj=None):
    
    
    html=__builtin__.htmlReport
    
    suite.threadName=thread
    
    import traceback

    if html:
               
        fp = file('./Report/att.html', 'wb')
        runner = HTMLTestRunner.HTMLTestRunner(
            stream=fp,
            title='SMI-S Component test',
            description='This demonstrates the report output by HTMLTestRunner.',
            thread=thread,
            threadObj=threadObj
            )
        
        #runner = HTMLTestRunner.HTMLTestRunner()
        __builtin__.htmlReporter=runner
        
        #rst is _TestResult instance, if rst.failure_count > 0: print 'TestFailed'
        #try:
            #3/0
        rst=runner.run(suite)            
        #except:
            #print "Unexpected error:", sys.exc_info()
            #traceback.print_exc(file=sys.stdout)
        return rst 
        
       # rtn="PASS"
       # if rst.failure_count > 0:
       #     rtn="FAIL"
       # return (rtn,rst)
            
   
    if not html:
        rst=unittest.TextTestRunner(verbosity=5).run(suite)
        return rst



def start(fileList,threadName,threadObj):
    #print threadName, '-----run started'
    global suiteHashG
    
   # assembel suiteG in smisTest.start()
    suiteHashG[threadName]=unittest.TestSuite()
   
    for file in fileList:
        runOneIni(file,threadName=threadName).addTest()
        
    
    
    run(suiteHashG[threadName],thread=threadName, threadObj=threadObj)
    #self.writeHtml('info', "----run finished")
    
    if hasattr(__builtin__,'resultG') and (threadName in __builtin__.resultG.keys()):
        setattr(__builtin__.resultG[threadName],'_testRunEntered', False)
    
    
        
        
if __name__ == '__main__':
    [fileName]=sys.argv[1:]
    fileName="C:/cim_test/testcase/ts_pool/t1_debug.ini"
    #fileName="C:/cim_test/testcase/ts_pool/cSetup.ini"
    #print fileName
    start(fileName)
