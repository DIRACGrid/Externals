#!/usr/bin/env python

import imp
import os
import sys
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

compileOpenSSL = False

if compileOpenSSL:
  osslch = chClass( os.path.join( here, "openssl" ) )

  versions = { 'openssl' : "0.9.8m" }
  osslch.setPackageVersions( versions )

  osslch.unTarPackage( "openssl" )
  ret = osslch.execRawAndGetOutput( "gcc -dumpversion" )

  if not osslch.doConfigure( "openssl", extraArgs = "shared threads", configureExecutable = "config" ):
    logging.error( "Could not deploy openssl package" )
    sys.exit( 1 )

  if ret:
    if ret[0].strip() >= "4.3.0":
      makefilePath = os.path.join( osslch.getPackageDir( 'openssl' ), 'Makefile' )
      logging.error( "Patching %s", makefilePath )
      osslch.replaceInFile( makefilePath, "-m486", "-mtune=i486" )

  if not osslch.doMake( "openssl", makeJobs = 1 ):
    logging.error( "Could not deploy openssl package" )
    sys.exit( 1 )

ch = chClass( here )
version = "0.6.5"
ch.setPackageVersions( { "GSI": version } )

gsidir = os.path.join( here, "pyGSI-%s" % version )

ch.downloadPackage( "GSI", "https://github.com/DIRACGrid/pyGSI/archive/%s.tar.gz" % version )
ch.unTarPackage( "GSI" )

libPaths = []
for lp in ( "lib", "lib64" ):
  lp = os.path.join( ch.getPrefix(), lp )
  if os.path.isdir( lp ):
    libPaths.append( lp )

fd = open( os.path.join( gsidir, "setup.cfg" ), "w" )
fd.write(
"""
[build_ext]
include_dirs = %s
library_dirs = %s
define = OPENSSL_NO_KRB5
verbose = 1
""" % ( os.path.join( ch.getPrefix(), "include" ), ":".join( libPaths ) )
 )
fd.close()


#for step in ( "build", "bdist_egg" ):
#  if not ch.pythonExec( "setup.py", extraArgs = step ):
#    ch.ERROR( "Could not deploy GSI" )
#    sys.exit( 1 )


if not ch.easyInstall( gsidir ):
  ch.ERROR( "Could not deploy GSI" )
  sys.exit( 1 )
