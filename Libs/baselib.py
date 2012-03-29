
import sys
sys.path.append('..\libs')
sys.path.append('..\libs\class')
import unittest,tcParser,cim,re,time,pywbem,os
import logging, __builtin__,HTMLTestRunner
import socket


#connect and return connect obj
def connect(cimsrv,cimusr,cimpwd,cimns):
    
    cliconn = pywbem.WBEMConnection(cimsrv,(cimusr,cimpwd),cimns)
    return cliconn



def parseTest(testStr):
    rtnTest=dict()
    list=testStr.split(";")
    for i in list:
        if re.match('suite=.*,tests=.*',i):
            tcs=[]
            c=re.match('suite=(.*),tests\=(.*)',i);
            suite=c.group(1)
            tests=c.group(2).split(',')  #test will be run
            if suite not in rtnTest.keys():
                rtnTest[suite] =[]
            rtnTest[suite] +=tests
            
    return  rtnTest


            
    

def initLogger(loggerName,logFile):
    logging.basicConfig(filename=logFile,
                        stream=HTMLTestRunner.stdout_redirector,
                        level=logging.DEBUG,
                        format='%(levelname)s %(asctime)s %(filename)s Line:%(lineno)d %(message)s',
                        datefmt="%H:%M:%S"
                        )
    logger = logging.getLogger(loggerName)
    
    
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(stream=sys.__stdout__)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(levelname)-6s %(asctime)6s %(message)10s', datefmt="%H:%M:%S")
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    __builtin__.logger=logger
    
    #logger.info('Program Started')
        




def parseNameValue(nv):
    (name,value)=re.match('^(.*)=(.*)', nv).groups()
    name=name.strip()
    value=value.strip()
    return (name,value)

def sleep(sec,reason):
    secS=str(sec)
    if sec > 0:
        #cim.cimBase().writeHtml("info", "sleep "+secS+" seconds, reason :"+reason)
        time.sleep(sec)


#cleanup file
def removeComment(fileName):
    f=open(fileName,'r')
    rtn=""
    for line in f:
        line=line.strip()           
        if re.match(r'^#',line):
           pass
        elif re.match(r'^\s*$',line):
           pass             
        else:
           rtn+=line
           rtn+='\n'           
    f.close()
    rtn=re.findall('(.*)\n$',rtn,re.S)[0]
    return rtn


def parseInvokeMethodTest(tcInst):    
    print "hi"
    pass
    


def setIndi(cnt,indiId,indiDst,indiCql):
    #create listner destination
    lsnr_dst=pywbem.CIMInstance('cim_listenerdestinationcimxml')
    lsnr_dst['name']='mydest'
    lsnr_dst['destination']=indiDst
    dest=cnt.CreateInstance(lsnr_dst)
    
    
    #create indication filter
    fltr=pywbem.CIMInstance('cim_indicationfilter')
    fltrName='filter_'+indiId
   
    fltr['name']=fltrName
    fltr['query']=indiCql
    fltr['querylanguage']='dmtf:cql'
    fltrObj=cnt.CreateInstance(fltr)    
    
    #subscibe indication
    subscription=pywbem.CIMInstance('cim_indicationsubscription')
    subscription['handler']=dest
    subscription['filter']=fltrObj
    subOjb=cnt.CreateInstance(subscription)
    
    return subOjb
    
def getClientIp():
    ip=socket.gethostbyname(socket.gethostname())
    return ip


if __name__ == '__main__':
    cimlib.connect()
    print 'hi'