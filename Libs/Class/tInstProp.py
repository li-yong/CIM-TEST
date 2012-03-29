import sys, logging
sys.path.append('.\libs')
sys.path.append('.\class')
import unittest,tcParser,cim,HTMLTestRunner,re,pickle,os

logger = logging.getLogger(__name__)

#the class test classes properties as expected.
class tInstProp(cim.cimBase):
    
    
    def __init__(self,methodName,clsName,instanceCondition,caseVerify):
        #map methodName to self.mainMethod.  MethodName is the testcase name.
        setattr(self,methodName,self.mainMethod)
        unittest.TestCase.__init__(self, methodName)
        self.writeHtml("info", "Class __init__,one class Instance created, tc is {}".format(methodName))
        self.methodName=methodName
        self.clsName=clsName
        self.instanceCondition=instanceCondition
        self.caseVerify=caseVerify

    
    @classmethod
    def setUpClass(self):
        cim.cimBase().writeHtml("info","run class setUpClass method")
        self.cnt=cim.cimBase().connect()
        cimClasses=cim.cimBase().enumerateClasses(self.cnt,'DeepInheritance=True')
        dictClass={}
        for i in cimClasses:
            key=i.classname
            dictClass[key]=i
            
        self.cimClasses=dictClass
        self.cimClassesNameList=dictClass.keys()        
       
    
    @classmethod
    def tearDownClass(self):
        self.writeHtml("info","run class tearDownClass method")


    def mainMethod(self):
        str="\nExecuting test:{}. ".format(self.methodName)
        self.writeHtml("info",str)
        
        clsName=self.clsName
        instanceConditionX=self.instanceCondition
        verifyClsDict=self.caseVerify
        
        
        #find instance qualify requirement.
        criteraList=[]
        for k,v in instanceConditionX.iteritems():
            str="{}={}".format(k,v)
            criteraList.append(str)

        
        cimInstanceUnderTest=self.findInst(self.cnt,clsName,criteraList)
        chk=verifyClsDict.keys()
        chk.sort()
        
        
        for x in chk:
            k=x
            v=verifyClsDict[k]
            
            astInstPropEqual=re.match(r"astInstPropEqual\((.*?),(.*?)\)",v)            
            if astInstPropEqual:
                inst=cimInstanceUnderTest[0]
                propName=astInstPropEqual.group(1)
                propValue=astInstPropEqual.group(2)
                self.astInstPropEqual(self,inst,propName,propValue)
                
            astOnlyOneInst=re.match(r"astOnlyOneInst\(\)",v)            
            if astOnlyOneInst:
                self.astOnlyOneInst(self,cimInstanceUnderTest)                
            
            astAtLeastOneInst=re.match(r"astAtLeastOneInst\(\)",v)            
            if astAtLeastOneInst:
                self.astAtLeastOneInst(self,cimInstanceUnderTest)

    #end of mainMethod


def testInstance(cfg):
    verify=tcParser.tcParser(cfg)
    verify.parseTest()
    
    suite=unittest.TestSuite()
    
    #Todo: assert each conf have one cls
    clsName=verify.tc['Class']['clsname']
    
    for verifyInst in verify.tc.keys():
        match=re.match("Test(\d+)",verifyInst)
        if match:
            id=match.group(1)
            tcName=verify.tc[verifyInst]['testname']
            #tc='test_instancePro_'+cls+'_'+tcName
            tc=tcName
            instanceCondition=verify.tc['Instance'+id]
            caseVerify=verify.tc['Verify'+id]
            
            tcObj=tInstProp(tc,clsName,instanceCondition,caseVerify)
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
        
    print 'End of Test'


if __name__ == '__main__':
    #unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(CimSimpleTestCase)
    testInstance("C:/cim_test/testcase/simple/testInstance_C4CB_HostService.conf")
    #testInstance("C:/cim_test/testcase/simple/t01.ini")

    

