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

versions = { 'simplejson' : "3.8.1",
             # 'fuse-python' : "0.2",
             'pyparsing' : '2.0.6',
             'requests' : '2.9.1',
             'futures' : '3.0.5',
             'certifi' : '2016.9.26',
             'stomp' : '4.1.15'}

ch.setPackageVersions( versions )

for package in versions:
  packageToInstall = "%s>=%s" % ( package, versions[ package ] )
  if not ch.easyInstall( packageToInstall ):
    logging.error( "Could not deploy %s with easy_install", package )
    if not ch.pip( packageToInstall ):
      logging.error( "Could not deploy %s with pip", package )
      sys.exit( 1 )
