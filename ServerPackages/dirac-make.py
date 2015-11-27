#!/usr/bin/env python

import imp
import os
import sys

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

versions = { 'mock' : "1.3.0",
             'Sphinx' : '1.3.1',
             'rst2pdf' : '0.93',
             'nose' : '1.3.7',
             'pylint' : '1.4.4',
             'coverage' : '4.0.3',
             'pexpect' : '4.0.1'}

ch.setPackageVersions( versions )

for package in versions:
  packageToInstall = "%s>=%s" % ( package, versions[ package ] )
  if not ch.easyInstall( packageToInstall ):
    ch.ERROR( "Could not deploy %s with easy_install" % package )
    if not ch.pip( packageToInstall ):
      ch.ERROR( "Could not deploy %s with pip" % package )
      sys.exit( 1 )
