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

versions = { 'sqlalchemy' : "1.0.9",
             'pexpect' : '4.0.1',
             'MySQL-python' : '1.2.5',
             'requests' : '2.9.1',
             'tornado' : '4.3',
             'apache-libcloud' : '1.1.0',
             'elasticsearch-dsl':'2.0.0',
             'psutil':'4.2.0' }

ch.setPackageVersions( versions )

for package in versions:
  packageToInstall = "%s>=%s" % ( package, versions[ package ] )
  if not ch.easyInstall( packageToInstall ):
    logging.error( "Could not deploy %s with easy_install", package )
    if not ch.pip( packageToInstall ):
      logging.error( "Could not deploy %s with pip", package )
      sys.exit( 1 )
