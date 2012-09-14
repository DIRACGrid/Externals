#!/usr/bin/env python

import imp, os, sys, platform

here = os.path.dirname( os.path.abspath( __file__ ) )
chFilePath = os.path.join( os.path.dirname( here ) , "common", "CompileHelper.py" )
try:
  fd = open( chFilePath )
except Exception, e:
  print "Cannot open %s: %s" % ( chFilePath, e )
  sys.exit( 1 )

chModule = imp.load_module( "CompileHelper", fd, chFilePath, ( ".py", "r", imp.PY_SOURCE ) )
fd.close()
chClass = getattr( chModule, "CompileHelper" )

ch = chClass( here )


versions = { 'libart_lgpl' : "2.3.20",
             'freetype' : "2.3.11",
             'libpng' : "1.2.40" }

ch.setPackageVersions( versions )

for package in versions:
  if not ch.deployPackage( package, configureArgs = "--enable-shared" ):
    ch.ERROR( "Could not deploy %s" % package )
    sys.exit( 1 )
