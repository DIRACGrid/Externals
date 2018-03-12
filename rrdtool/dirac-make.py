#!/usr/bin/env python

import imp, os, sys
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')


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

versions = { 'rrdtool' : "1.7.0" }
ch.setPackageVersions( versions )

if not ch.downloadPackage( "rrdtool" ):
  logging.error( "Could not download rrdtool" )
  sys.exit( 1 )

if not ch.unTarPackage( "rrdtool" ):
  logging.error( "Could not deploy rrdtool" )
  sys.exit( 1 )

prefix = ch.getPrefix()
env = {}
env[ 'CC' ] = 'gcc'
env[ 'LDFLAGS' ] = "-L%s" % os.path.join( prefix, "lib" )
env[ 'CPPFLAGS' ] = ""
ch.setDefaultEnv( env )
includeDirs = ( "", "freetype2", "libart-2.0" )
for idir in includeDirs:
  env[ 'CPPFLAGS' ] += "-I%s " % os.path.join( prefix, "include", idir )

configFlags = []
configFlags.append( "--enable-static" )
configFlags.append( "--disable-shared" )
configFlags.append( "--disable-python" )
configFlags.append( "--disable-ruby" )
configFlags.append( "--disable-perl" )
configFlags.append( "--disable-tcl" )
if not ch.deployPackage( "rrdtool", configureArgs = " ".join( configFlags ) ):
  logging.error( "Could not deploy rrdtool" )
  sys.exit( 1 )
