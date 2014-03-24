#!/usr/local/bin/python

import sys,os,cgi,shelve,subprocess,re
import cgitb
cgitb.enable()

dns_server = "nameserver.fq.dn"

print "Content-type: text/html"
print ""

http_vars = cgi.FieldStorage()

username = http_vars.getvalue("u")
password = http_vars.getvalue("p")
fqdn = http_vars.getvalue("h")
zone = http_vars.getvalue("z")

if username == None or password == None or fqdn == None:
  print "no u,p or h"
  sys.exit()

d_users = {'username':'password'}

try:
#  d_users = shelve.open("ddns.shelve",flag='r')
  d_users = d_users
except:
  print "no shelve"
  sys.exit()

# check credentials

if not d_users.get(username) == password:
  print "no auth"
  sys.exit()

# get ip

newip = os.getenv('REMOTE_ADDR')
if re.search(':',newip):
  v6 = True
else:
  v6 = False

# get zone

if zone == None:
  zone = '.'.join(fqdn.split('.')[1:])

# todo check if zone is legit

# host check
# todo check if user has permit to change this host

#update needed?
if v6:
  currentip = subprocess.Popen(['dig','+short','AAAA',fqdn],stdout=subprocess.PIPE).communicate()[0].strip('\n')
else:
  currentip = subprocess.Popen(['dig','+short','A',fqdn],stdout=subprocess.PIPE).communicate()[0].strip('\n')

if currentip == newip:
  print "no new" 
  sys.exit()

# create update file

if v6:
  updatecommand = """server %(ns)s
  zone %(zone)s
  update delete %(fqdn)s. AAAA
  update add %(fqdn)s 60 AAAA %(ipaddr)s
  send
  """ % { "ns": dns_server,
          "zone": zone,
          "fqdn": fqdn,
          "ipaddr": newip
        }
else:
  updatecommand = """server %(ns)s
  zone %(zone)s
  update delete %(fqdn)s. A
  update add %(fqdn)s 60 A %(ipaddr)s
  send
  """ % { "ns": dns_server,
          "zone": zone,
          "fqdn": fqdn,
          "ipaddr": newip
        }

#update!

try:
  sp_nsupdate = subprocess.Popen(['nsupdate','-k','/path/to/ddns/key/file.private'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate(updatecommand)
except:
  print sp_nsupdate
