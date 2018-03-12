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


versions = { 'libart_lgpl' : "2.3.20",
             'freetype' : "2.9",
             'libpng' : "1.6.34" }

ch.setPackageVersions( versions )

for package in versions:
  if not ch.deployPackage( package, configureArgs = "--enable-shared" ):
    logging.error( "Could not deploy %s" % package )
    sys.exit( 1 )
