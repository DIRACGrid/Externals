#!/usr/bin/env python

import imp
import os
import sys
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')

here = os.path.dirname( os.path.abspath( __file__ ) )
chFilePath = os.path.join( os.path.dirname( here ) , "common", "CompileHelper.py" )
try:
  with open( chFilePath ) as fd:
    chModule = imp.load_module( "CompileHelper", fd, chFilePath, ( ".py", "r", imp.PY_SOURCE ) )
except Exception as e:
  print "Cannot open %s: %s" % ( chFilePath, e )
  sys.exit( 1 )

chClass = getattr( chModule, "CompileHelper" )

ch = chClass( here )

versions = { 'simplejson' : "3.13.2",
             'python-json-logger' : '0.1.8',
             # 'fuse-python' : "0.2",
             'pyparsing' : '2.2.0',
             'requests' : '2.18.4',
             'futures' : '3.2.0',
             'certifi' : '2018.1.18',
             'stomp.py' : '4.1.19'}

ch.setPackageVersions( versions )

for package, version in versions.iteritems():
  packageToInstall = "%s=%s" % (package, version)
  if not ch.pip( packageToInstall ):
    logging.error( "Could not deploy %s with pip", package )
    sys.exit( 1 )
