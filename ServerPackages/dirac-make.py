#!/usr/bin/env python

import imp, os, sys, platform, shutil

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

versions = { 'mock' : "0.7.1",
             'Sphinx' : '1.0.7',
             'rst2pdf' : '0.16',
             'nose' : '1.0',
             'pylint' : '0.23.0',
             'coverage' : '3.4' }

ch.setPackageVersions( versions )

for package in versions:
  if not ch.easyInstall( "%s>=%s" % ( package, versions[ package ] ) ):
    ch.ERROR( "Could not deploy %s" % package )
    sys.exit( 1 )
