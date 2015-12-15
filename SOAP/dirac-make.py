#!/usr/bin/env python

import imp, os, sys, platform, shutil

here = os.path.dirname( os.path.abspath( __file__ ) )
chFilePath = os.path.join( os.path.dirname( here ) , "common", "CompileHelper.py" )
try:
  fd = open( chFilePath )
except Exception as e:
  print "Cannot open %s: %s" % ( chFilePath, e )
  sys.exit( 1 )

chModule = imp.load_module( "CompileHelper", fd, chFilePath, ( ".py", "r", imp.PY_SOURCE ) )
fd.close()
chClass = getattr( chModule, "CompileHelper" )

ch = chClass( here )

versions = { 'suds' : "0.4",
             'boto' : '1.9b' }
ch.setPackageVersions( versions )

for package in versions:
  if not ch.easyInstall( "%s>=%s" % ( package, versions[ package ] ) ):
    ch.ERROR( "Could not deploy %s" % package )
    sys.exit( 1 )
