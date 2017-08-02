from flask import Flask
from flask import request
from flask import render_template
import urllib2
import base64
import re
import requests
temp=''
pm=''
headers1=''
username = 'xxxxx'
password = 'xxxxxx'
app = Flask(__name__, static_url_path="/static", static_folder="static")

@app.route('/')
def my_form():
    return render_template("index.html")
@app.route('/', methods=['POST'])

def my_form_post():
    hostname = request.form['text']

    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, 'http://spectrum1.qualcomm.com/spectrum/restful/models', username, password)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    xmlparameters = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    <rs:model-request
      xmlns:rs='http://www.ca.com/spectrum/restful/schema/request'
      xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
      xsi:schemaLocation='http://www.ca.com/spectrum/restful/schema/request ../../../xsd/Request.xsd '>
     <rs:target-models>
      <rs:models-search>
       <rs:search-criteria xmlns='http://www.ca.com/spectrum/restful/schema/filter'>
         <devices-only-search />
         <filtered-models>
           <has-substring-ignore-case>
            <attribute id='0x1006e'>
             <value>%s</value>
            </attribute>
          </has-substring-ignore-case>
         </filtered-models>
       </rs:search-criteria>
      </rs:models-search>
     </rs:target-models>
     <rs:requested-attribute id='0x1006e' />
     <rs:requested-attribute id='0x12d7f' />
     <rs:requested-attribute id='0x10009' />
     <rs:requested-attribute id='0x10000' />
    </rs:model-request>"""% hostname
    theurl = 'spectrum server rest url'
    encodedstring = base64.encodestring(username+':'+password)[:-1]
    auth = 'Basic %s' % encodedstring
    headers = {'Authorization': auth}
    req = urllib2.Request(theurl, xmlparameters, headers)
    req.add_header('Content-Type', 'application/xml; charset=UTF-8')
    try:
        result1 = urllib2.urlopen(req).read()
    except urllib2.HTTPError:
        print 'There was an error with the request'
    pat = re.compile('\<[A-Za-z]{5}\s([a-z]{2})=(.\w+.)')
    pat1 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    test=pat.search(result1)
    test1=pat1.search(result1)
    mh = test.group(2)
    Old_ip = test1.group(0)
    model_handle=mh.replace('"',"" )
    global temp
    temp = model_handle

    specOld = "Existing IP address in CA Spectrum: %s" % Old_ip

##find old IP in CAPM
    PMURL='CAPM server rest url'
    payload = """<FilterSelect xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="filter.xsd">
        <Filter>
        <Device.HostName
        type="CONTAINS">%s</Device.HostName>
        </Filter>
        </FilterSelect>""" % hostname
    headers = {'Content-Type': 'application/xml'}
    global headers1
    headers1=headers
    result=requests.post(PMURL, data=payload, headers=headers).text
    pat = re.compile('\<[A-Za-z]{2}>(\d+)')
    pat1 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    test1=pat1.search(result)

    test=pat.search(result)
    pmOld_ip = test1.group(0)
    ID = test.group(1)
    global pm
    pm=ID
    PMoldip="Existing IP address in CAPM: %s" % pmOld_ip

    return render_template("index1.html", capmip=PMoldip, specip=specOld)

@app.route('/add')
def hello():
    return render_template("index1.html")
@app.route('/add', methods=['POST'])
def add():
    NewIp = request.form['value']

    URL= 'spectrum server rest url'
    r= requests.put(URL, auth=(username, password))

    msg = "\nCongrats!!New ip has been updated in CA Spectrum\n!!!"
    #CAPM new ip update
    CAURL= 'CAPM server rest url'
    data="""
        <Device version="1.0.0">
        <PrimaryIPAddress>%s</PrimaryIPAddress>
        </Device>""" % NewIp
    r= requests.put(CAURL, data=data, headers=headers1)
    msg1 = "\nCongrats!!New ip has been updated in CA PM\n!!!"
    return render_template("index2.html", message=msg, message1=msg1)


if __name__ == '__main__':
    app.run(host ='0.0.0.0')
