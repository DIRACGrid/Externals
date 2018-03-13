#!/usr/bin/env python

import imp, os, sys
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

versions = { 'suds-jurko' : "0.6",
             'boto' : '1.9b' }
ch.setPackageVersions( versions )

for package, version in versions.iteritems():
  packageToInstall = "%s==%s" % (package, version)
  if not ch.pip( packageToInstall ):
    logging.error( "Could not deploy %s with pip", package )
    sys.exit( 1 )
