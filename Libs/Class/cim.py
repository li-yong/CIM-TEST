global connectFile
#connectFile='C:/cim_test/connect.cfg'
import sys
sys.path.append('..\libs')
import unittest,re,baselib,pywbem,pickle,os,time,__builtin__,string
import logging,shelve,csv,cimListener
from string import Template
from timeit import Timer
from multiprocessing import Process,Queue
import xml.etree.ElementTree

logger = logging.getLogger(__name__)


global varHash
varHash=dict()

class cimBase(unittest.TestCase):

    #@classmethod
    #def setUpClass2(self):
    #    cimBase().writeHtml("info","run cimBase class setUpClass method")
    #    self.cnt=self.connect() 
       
    
    #@classmethod
    #def tearDownClass2(self):
    #    self.writeHtml("info","run cimBase class tearDownClass method")

    
    def __init__(self,methodName=None,threadName=None):
        
        if threadName != None:
            self.threadName=threadName
        
        #for ini case, this method is dumy
        if methodName==None:
            pass
        #for python case
        else:
            super(cimBase,self).__init__(methodName=methodName)
            
    def sayHi(self):
        print "hi"


    def writeHtml(self,loglevel,msg):
        
        if hasattr(self,'threadName'):
            threadName=self.threadName
        else:
            threadName='MainProcess'
            

        if loglevel=='info':
            #write to log file and concole
            __builtin__.logger.info(threadName+':'+msg) 

            if hasattr(__builtin__,'htmlReport') and __builtin__.htmlReport:
                if threadName=='MainProcess':
                    pass
                else:
                    __builtin__.stringIoG[threadName]['stdout'].fp.write(threadName+':'+msg+"\n")


        if loglevel=='error':
            __builtin__.logger.error(threadName+':'+msg)
            if hasattr(__builtin__,'htmlReport') and __builtin__.htmlReport:
                if threadName=='MainProcess':
                    pass
                else:
                    __builtin__.stringIoG[threadName]['stdout'].fp.write(threadName+':'+msg+"\n")
                
        if loglevel=='blankLine':
            if hasattr(sys.stdout,'fp'):
                sys.stdout.fp.write("\n")                
            
 
    
    def enumerateClasses(self,cnt,option=''):
        self.writeHtml("info","Enumerateing Classes...")
        #option=''
        cmdStr="cnt.EnumerateClasses("+option+")"
        #cimClasses=eval(cmdStr)
        
        #using pickle for develop, avoide too long waiting for emmu.
        dumpfile=".\emmuClasses.pickle.del"
        
        #write dump to file
        #fh=open(dumpfile,'wb')
        #pickle.dump(cimClasses,fh)
        #fh.close()
        
        
        fh=open(dumpfile,'rb')
        cimClasses=pickle.load(fh)
        fh.close()
        
        
        self.writeHtml("info","EnumerateClasses Finished")
        return cimClasses
    
    
    def enumerateInstances(self,cimclass,option=''):
        self.writeHtml("info","Enumerateing Instances of class "+cimclass+"...")
        cmdStr="self.cnt.EnumerateInstances('"+cimclass+"',"+option+")"
        self.writeHtml("info","Exec: "+cmdStr)
        cimInstances=eval(cmdStr)
        
        #using pickle for develop, avoide too long waiting for emmu.
        #dumpfile=".\emmuInstance_CIM_RegisteredProfile.pickle.del"
        
        #write dump to file
        #fh=open(dumpfile,'wb')
        #pickle.dump(cimInstances,fh)
        #fh.close()
        
        #read from the dump file
        #fh=open(dumpfile,'rb')    
        #cimInstances=pickle.load(fh)
        #fh.close()
        
        
        self.writeHtml("info","EnumerateInstance for class {} Finished".format(cimclass))
        return cimInstances
    
    def queryInst(self,cql):
        ql='cql'
        self.writeHtml('info',"query instance, {}".format(cql))
        self.writeHtml('info',"connect: {}".format(self.cnt))
        instance=self.cnt.ExecQuery(ql,cql)
        return instance
    
    
    def actFi(self,section):
        self.assertTrue('clsName' in section.scalars, "need clsName")
        self.assertTrue('rst' in section.scalars, "need rst")        
    
        
        clsName=section['clsName']
        rstName=section['rst']
        
        section.scalars.remove('clsName')
        section.scalars.remove('rst')
        
        #find instance qualify requirement.
        criteraList=[]
        for i in section.scalars:
            str="{}={}".format(i,section[i])
            criteraList.append(str)
            
        rst=self.findInst(clsName,criteraList)
        
        self.saveConfVar(rstName,rst)        
            


    def findInst(self,clsName,criteraList,namespace='root/emc'):
        ql='cql'
        whereClause=''        
            
        if len(criteraList)==0:
            cql="select * from {}".format(clsName)
        else:
            for i in criteraList:
                match=re.match("(.*)=(.*)",i)
                if match:
                    name=match.group(1)
                    value=match.group(2) 
                    whereClause +="{}.{}=\'{}\' and ".format(clsName,name,value)
                    
            where=re.match("(.*)(and $)",whereClause).group(1)                
            cql="select * from {} where {}".format(clsName,where)
            
        logMsg="query instance, {}".format(cql)
        self.writeHtml("info",logMsg)
        #logger.info()
        if namespace=='root/emc':
            instance=self.cnt.ExecQuery(ql,cql)
        elif namespace=='interop':
            instance=self.cntInterop.ExecQuery(ql,cql)        
            
        
        return instance
    
    #self is the instance of 'Unittest.testcase' or it's subclass.
    def getInstProp(self,Inst,propName):
        self.assertIsInstance(Inst,pywbem.cim_obj.CIMInstance,"input Instance {} is not a CIMInstance object".format(Inst))
        try:
            actualPropertiesValue=Inst.properties[propName].value
            return actualPropertiesValue
        except KeyError:
            #raise AttributeError("Class has no arrtibute Id "+k)
            msg="Instance '{}' has no property named '{}'".format(Inst,propName)
            raise self.failureException(msg)
            
            
            
    
    def astInstPropEqual(self,Inst,propName,propValue):
        self.assertIsInstance(Inst,pywbem.cim_obj.CIMInstance,"input Instance {} is not a CIMInstance object".format(Inst))
        actualPropertiesValue=self.getInstProp(Inst,propName)
        msg="Instance Property {}, expected value {}, actual value {}".format(Inst,propValue,actualPropertiesValue)
        self.assertEqual(actualPropertiesValue, propValue,msg)
        self.writeHtml("info","Pass: astInstPropEqual")
        
    def astZeroInst(self,Instslist):
        self.assertIsInstance(Instslist,list,"input {} is not a list.".format(Instslist))
        instCnt=len(Instslist)
        msg="Expected Qualified Instance # {}, actual Instance # {}".format(0,instCnt)
        self.assertEqual(instCnt,0,msg)
        self.writeHtml("info","Pass: astZeroInst")        
        
    def astOnlyOneInst(self,Instslist):
        self.assertIsInstance(Instslist,list,"input {} is not a list.".format(Instslist))
        instCnt=len(Instslist)
        msg="Expected Qualified Instance # {}, actual Instance # {}".format(1,instCnt)
        self.assertEqual(instCnt,1,msg)
        self.writeHtml("info","Pass: astOnlyOneInst")
    
    def astAtLeastOneInst(self,Instslist, msgPass=None):
        self.assertIsInstance(Instslist,list,"input {} is not a list.".format(Instslist))
        instCnt=len(Instslist)
        msg="Expected Qualified Instance # {}, actual Instance # {}".format('>=1',instCnt)
        self.assertTrue(instCnt>=1,msg)
        self.writeHtml("info","Pass: astAtLeastOneInst")
        
    
    def saveConfVar(self,name,value):
        if not hasattr(self,'confVar'):
            self.confVar=dict()
        
        
        self.confVar[name]=value
        
        varHash[name]=value
        #print "varHash[{}] set to {}".format(name,value)
        
    def uniqList(self,list):
        keys = {}
        for e in list:
            keys[e] = 1
        return keys.keys()
            
    
        
    def translateVar(self,str):
        #str='astAtLeastOneInst(${myInstList}) astAtLeastOneInst(${myInstList2} (${myInstList3}) '
        varList=re.findall(r"\${\w+}",str)
        varList=self.uniqList(varList)

        for i in  varList:
            i2=re.findall(r"\${(\w+)}",i)[0]
            if (hasattr(self,'confVar')) and (i2 in self.confVar.keys()):
                if self.confVar[i2].__class__ == type('str'):
                    v= self.confVar[i2]
                else:
                    v='self.confVar[\''+i2+'\']'
                    
                str=str.replace(i,v)
            elif i2 in varHash.keys() :
                if varHash[i2].__class__ == type('str'):
                    v= varHash[i2]
                else:
                    v="varHash['"+i2+"']"
                    
                str=str.replace(i,v)
            elif i2=='ThreadName':
                if hasattr(self,'threadName'):
                    v=self.threadName
                else:
                    raise BaseException("self not has attribute threadName")
                    
                str=str.replace(i,v)    
                    
                
            else:
                logger.error("var {} not set before use".format(i))
                raise BaseException("var {} not set before use".format(i))
        return str
                   
        
    
    #Action:emuInstance
    def actEi(self,section):
        self.assertTrue('clsName' in section.scalars, "need clsName")
        self.assertTrue('rst' in section.scalars, "need rst")
        
        #self.showNote(section)  
        
        clsName=section['clsName']
        
        
        rst=self.enumerateInstances(clsName)
        rstName=section['rst']
        self.saveConfVar(rstName,rst)
        self.check(section)

    #Action: check instance properties    
    def actCip(self,section):
        #self.assertTrue('clsName' in section.scalars, "need clsName")
        #self.assertTrue('rst' in section.scalars, "need rst")
        
        #self.showNote(section)  
        
        #clsName=section['clsName']
        
        
        #rst=self.enumerateInstances(clsName)
        #rstName=section['rst']
        #self.saveConfVar(rstName,rst)
        self.check(section)

                


    #Action:InvokeMethod
    def actIm(self,section):
        self.assertTrue('rst' in section.scalars, "need rst")
        self.assertTrue('methodName' in section.scalars, "need methodName")
                
        wJC=False
      
        if 'waitJobComplete' in section.scalars:
            wJC=section['waitJobComplete']
            section.scalars.remove('waitJobComplete')
            
        feJR=False    
        if 'expectedJobResult' in section.scalars:
            feJR=True
            eJR=section['expectedJobResult']
            section.scalars.remove('expectedJobResult')
            
        if (hasattr(__builtin__,'indication')) and (__builtin__.indication)\
        and ('indiFilterCql' in section.scalars):
            if ('indiFilterCql' not in section.scalars):
                raise "must have indiFilterCql"
            if ('indiWaittime' not in section.scalars):
                raise "must have indiWaittime"
            if ('indiFilterExpKw' not in section.scalars):
                raise "must have indiFilterExpKw"
            runIndi=True
            self.writeHtml('info','Indication is turn on, will check indication')
        else:
            runIndi=False
            self.writeHtml('info','Indication is turn off, will not check indication')
                       
            
        #if 'indicator' in section.scalars: section.scalars.remove('indicator')
        #if 'dest' in section.scalars: section.scalars.remove('dest')
        if 'indiFilterCql' in section.scalars: section.scalars.remove('indiFilterCql')
        if 'indiWaittime' in section.scalars: section.scalars.remove('indiWaittime')
        if 'indiFilterExpKw' in section.scalars: section.scalars.remove('indiFilterExpKw')            
            
        if  runIndi:          
            #indiDst=section['dest']
            
            clientIp=baselib.getClientIp()
            port=59900
            indiDst='http://{}:{}'.format(clientIp,port)
            
            indiCql=section['indiFilterCql']

            secName=section.name
            fN=section.parent.parent.main.filename
            tStamp=time.time()
            #indiId='{}/{}/{}'.format(fN,secName,tStamp)
            indiId='{}/{}'.format(fN,secName)
            
            #set Indicator
            self.setIndi(self.cntInterop, indiId,indiDst,indiCql)

            #q=Queue()
            #timeoutS=int(section['indiWaittime']) #timeout of the twister reactor
            #self.writeHtml('info',"Indication Timeout set to {} second".format(timeoutS))
            #p=self.startListen(q,timeoutS)
            
            




        rstName=section['rst']
        section.scalars.remove('rst')
        
        cmdStr='\''+section['methodName']+'\''
        section.scalars.remove('methodName')
        
        for i in section.scalars:
            a=section[i]
            cmdStr +=', '+ a

        cmdRst=self.translateVar(cmdStr)
        cmd='self.cnt.InvokeMethod('+cmdRst+')'
        self.writeHtml('info',cmd)
        iMRst=eval(cmd)
        job=iMRst[1]['Job']
        if wJC:
            jobActRst=self.waitJobComplete(job,"InvokeMethod Job Successed","InvokeMethod Job Failed")
            if feJR:
                self.assertEqual(jobActRst.upper(),eJR.upper())
       
        self.saveConfVar(rstName,iMRst)

        self.check(section)
        
        
        if  runIndi:
            
            #'''get listener result'''
            self.writeHtml('info', 'read indication in Queue')
            
            x=q.get(timeout=3)
            
            if type(x)==str:
                msgQ=x
            else:               
                msgQ=xml.etree.ElementTree.tostring(x)
            
            #msgQ=q.get(timeout=3)
            msgQShort=msgQ[:50]
            self.writeHtml('info', 'first 50 chars of msg get in queue:{}'.format(msgQShort) )
            
            self.writeHtml('info','close the Queue')
            q.close()
            self.stopListen(p)
            del q
            del p            
            
            indiChk=section['indiFilterExpKw'].split(',')
            indiRst=True
            for i in indiChk:
                if i in msgQ:
                    self.writeHtml('info','found expected keyword {} in indication received.'.format(i))
                    indiRst=indiRst and True
                else:
                    self.writeHtml('info','Indication Test Failed, Not found expected keyword {} in indication received. Either server no indication sent or waittime need be increased.'.format(i))
                    indiRst=indiRst and False
            
                    
            self.writeHtml('info','indication test result:{}'.format(indiRst))
            
            if not indiRst:
                self.fail('indication test failed')

            

    
    def check(self,section):
        chklist=section.scalars
        for i in chklist:
            if re.match(r"check\d",i):
                str=section[i]
                if section[i].__class__==list:
                    str=string.join(section[i],',')
                    
                abc=self.translateVar(str)
                chk='self.'+abc
                self.writeHtml('info','check {}'.format(chk))
                eval(chk)
                #if re.match('astZeroInst',section[i]):
                    #self.astZeroInst(self.confVar['ac2Rst'])
                    
                
    
    def waitJobComplete(self,job,msgSucc, msgFail):
        while True:
            instJob=self.cnt.GetInstance(job)
            jobstatus = instJob.properties['Status'].value
            reason=instJob.properties['JobStatus'].value
            error=instJob.properties['ErrorDescription'].value
            
            if jobstatus == 'Success':
                    msg= "{}, actual status value: {}, reason: {}, error:{}".format(msgSucc,jobstatus,reason,error)
                    self.writeHtml('info',msg)
                    break
            elif jobstatus == 'Error':
                    msg= "{}, actual status value:{},reason: {}, error:{}".format(msgFail,jobstatus,reason,error)
                    self.writeHtml('info',msg)                    
                    break
            else:
                    self.writeHtml("info", "sleep 2secs before next job status checking")
                    time.sleep(2)
        return jobstatus       

    def showNote(self,section):
        self.assertTrue(section.name, "need name")
        
        secName=section.name
        fN=section.parent.parent.main.filename
        
        self.writeHtml("blankLine","\n")
        self.writeHtml("info",fN)
        self.writeHtml("info","Section: "+secName)
        #logger.info("in file:"+fN)
        #logger.info("run section:"+secName)

        if 'note' in section.scalars:
            note=section['note']
            section.scalars.remove('note')
            if isinstance(note, list):
                note=','.join(note)
            output= "Description: "+note
            self.writeHtml("info",output)


   #Action1:Query Instance
    def actQi(self,section):
        self.assertTrue('rst' in section.scalars, "need rst")
        self.assertTrue('cql' in section.scalars, "need cql statement")
        rstName=section['rst']
        section.scalars.remove('rst')
        
        
        
        cqlStat=section['cql']
        section.scalars.remove('cql')
        cqlStat=self.translateVar(cqlStat)
               
        qiRst=self.queryInst(cqlStat)
        
        self.saveConfVar(rstName,qiRst)
        self.check(section)
        
   #Action1:query Associator
    def actQa(self,section):
        self.assertTrue('rst' in section.scalars, "need rst")
        self.assertTrue('ObjectName' in section.scalars, "need ObjectName statement")
        self.assertTrue('AssocClass' in section.scalars, "need AssocClass statement")
        #self.showNote(section)    
        
        rstName=section['rst']
        section.scalars.remove('rst')
        
        objectName=section['ObjectName']
        objectName=self.translateVar(objectName)
        object=eval(objectName)
        
        assocClass=section['AssocClass']
        assocClass=self.translateVar(assocClass)        
               
        qaRst=self.queryAsso(object,assocClass)
        
        self.saveConfVar(rstName,qaRst)
        self.check(section)        
    
    def queryAsso(self,objectName,assocClass):
        rst=self.cnt.Associators(objectName, AssocClass=assocClass)
        return rst
    
    def actTrue(self,section):
        if section['msg']=='forceFalse':
            #raise attError("aaa") #ryan:
            #ryan: must raise self.failureException, otherwise the left case still be run.
            raise self.failureException("aaaa") 
            #self.assertEqual(0,1,"This is a force failure  message ")
            #return "FALSE"
        self.assertEqual(0,0,"This is a debug  message ")
        #self.writeHtml("info","Pass: actTrue")
        logger.info("Pass: actTrue")
        

       
    
    def actPrint(self,section):
        fR=1
        sec=0
        exp='pass'
        
        msg=section['msg']
        rv=self.writeHtml("info",msg)
        
        #indicator start
        if ('indicator' in section.scalars) and (section['indicator']=='on'):
            if ('dest' not in section.scalars) or ('filterCql' not in section.scalars):
                raise "must have dest and filterQueryCql"
            
            indiDst=section['dest']
            indiCql=section['filterCql']

            secName=section.name
            fN=section.parent.parent.main.filename
            tStamp=time.time()
            #indiId='{}/{}/{}'.format(fN,secName,tStamp)
            indiId='{}/{}'.format(fN,secName)
            
            #set Indicator
            self.setIndi(self.cntInterop, indiId,indiDst,indiCql)

            q=Queue()
            timeoutS='60' #timeout of the twister reactor
            p=self.startListen(q,timeoutS)
            #print q.get(timeout=3)
            
            
            #exit()
            #do sth
            self.writeHtml('info', "main process trigger indication")
            self.writeHtml('info', "main process job completed")
            #
            
            '''stop listener in a new process'''
            self.writeHtml('info', 'cim.stopListen(): terminate the listener process')
            
            self.writeHtml('info', 'waiting listener process to join')
            p.join()
            #p.terminate()
            self.writeHtml('info', "listener process joined")
        
        
            #q.close()
            
            
            #'''get listener result'''
            #q.put("HAHAHA")
            msgQ=q.get(timeout=3)
            msgQShort=msgQ[:50]
            self.writeHtml('info', 'first 50 chars of msg get in queue:{}'.format(msgQShort) )
            

            
            del q
            del p            
            
            
            
            
            indiChk=section['filterExpKw'].split(',')
            indiRst=True
            for i in indiChk:
                if i in msgQ:
                    self.writeHtml('info','found expected keyword {} in indication received.'.format(i))
                    indiRst=indiRst and True
                else:
                    self.writeHtml('info','Indication Test Failed, Not found expected keyword {} in indication received.'.format(i))
                    indiRst=indiRst and False
            
                    
            self.writeHtml('info','indication test result:{}'.format(indiRst))    
            

            
            pass
            
            
            
        
    def startListen(self,q,timeoutS):
        '''run listener in a new process'''
        mpid=os.getpid()
        self.writeHtml('info', 'main process id:{}'.format(mpid))
        #time.sleep(5)
        self.writeHtml('info', "listener process start listen"  )      
        p1 = Process(target=cimListener.s, args=('1',q,timeoutS))
        p1.start()
        self.writeHtml('info', "listener process started")
        return p1
        
    def stopListen(self,p):
        '''stop listener in a new process'''        
        
        self.writeHtml('info', 'cim.stopListen(): waiting the listener process to join')
        p.join()
        #p.terminate()
        self.writeHtml('info', "listener process joined")
        

    def setIndi(self, cnt,indiId,indiDst,indiCql):
        #remove all instance of cim_indicationsubscription
        
        creList=[]
        #creList.append('handler='+dest)
        #creList.append('filter='+fltrObj)

        instList=self.findInst('cim_indicationsubscription',creList,namespace='interop')
        for i in instList:
            cnt.DeleteInstance(i.path)
            self.writeHtml('info','removed cim_indicationsubscription instance')        
        
        
        #create listner destination
        lsnr_dst=pywbem.CIMInstance('cim_listenerdestinationcimxml')
        instName='mydest'
        lsnr_dst['name']=instName
        lsnr_dst['destination']=indiDst
        
        creList=[]
        #creList.append('name='+instName)
        #creList.append('destination='+indiDst)
        
        #find instance, if exist, remove it.
        instList=self.findInst('cim_listenerdestinationcimxml',creList,namespace='interop')
        
        for i in instList:
            cnt.DeleteInstance(i.path)
            self.writeHtml('info','removed cim_listenerdestinationcimxml instance')
        dest=cnt.CreateInstance(lsnr_dst)
        self.writeHtml('info','created cim_listenerdestinationcimxml instance:{}'.format(lsnr_dst['destination']))
            
            
            
        
        
        #create indication filter
        fltr=pywbem.CIMInstance('cim_indicationfilter')
        fltrName='filter_'+indiId
       
        fltr['name']=fltrName
        fltr['query']=indiCql
        fltr['querylanguage']='DMTF:CQL'
        fltr['sourcenamespace']='root/emc'
        fltr['sourcenamespaces']=['root/emc']
        
        creList=[]
        #creList.append('name='+fltrName) 
        
        #creList.append('query='+indiCql)

        instList=self.findInst('cim_indicationfilter',creList,namespace='interop')
        
        for i in instList:
            cnt.DeleteInstance(i.path)
            self.writeHtml('info','removed cim_indicationfilter instance')
            
        fltrObj=cnt.CreateInstance(fltr)
        self.writeHtml('info','created cim_indicationfilter instance,filter is {}'.format(fltr['query']))
        
        #subscibe indication
        subscription=pywbem.CIMInstance('cim_indicationsubscription')
        subscription['handler']=dest
        subscription['filter']=fltrObj
        
        
        subOjb=cnt.CreateInstance(subscription)
        self.writeHtml('info','created subscription: {}'.format(subscription))
        
        #write database
        v=dict()
        v['id']=fltrName
        v['timeSet']=time.time()
        v['timeReceive']= None
        v['revStatus']=False
        
        if not hasattr(__builtin__,'smisDbWritble') or (__builtin__.smisDbWritble==True):
            __builtin__.smisDbWritble=False
            try:
                db = shelve.open("./Report/.DATABASE", flag='c')
                db[fltrName] = v
                
                csvF='./Report/indicator.csv'
                if os.path.exists(csvF):
                    os.remove(csvF)
                csvWriter = csv.writer(open(csvF, 'wb'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                #self.dumpIndiDb(db)
                for i in db.keys():
                    fltName=i
                    timeSet=db[fltName]['timeSet']
                    timeReceive=db[fltName]['timeReceive']
                    revStatus=db[fltName]['revStatus']
                    csvWriter.writerow([fltName,timeSet,timeReceive,revStatus])
                db.close()       
            finally:                
                __builtin__.smisDbWritble=True
                
            #listern the indicator
            #cL=cimListener.CIMListener()
            #cL.run()
        
        
            
            

if __name__ == '__main__':

    
    obj=cimBase()
    obj.translateVar()
    exit 
    
    
    obj.show()
    cnt=connect()
    #inst=enumerateInstances(cnt,"C4CB_HostService")
    
    cd=[]
    cd.append('name=123')
    cd.append('name2=345')
    inst2=findInst(cnt,"C4CB_HostService",cd)
    print 'hi'