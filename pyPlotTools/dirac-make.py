#!/usr/bin/env python

import imp
import os
import sys
import shutil
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

versions = { 'Imaging' : "1.1.6",
             'matplotlib' : '1.5.0',
             'numpy' : '1.10.1',
             'pytz' : '2015.7' }

ch.setPackageVersions( versions )
env = { 'PKG_CONFIG_PATH' : os.path.join( ch.getPrefix(), "lib", "pkgconfig" ) }
ch.setDefaultEnv( env )
for package in ( 'numpy', 'Imaging', 'matplotlib', 'pytz' ):
  if not ch.downloadPackage( package ):
    logging.error( "Could not download %s", package )
    logging.info( "Trying pip" )
    if ch.pip( "%s==%s" % ( package, versions[package] ) ):
      continue
    logging.error( "Could not pip %s", package )
    sys.exit(1)
  if not ch.unTarPackage( package ):
    logging.error( "Could not deploy %s", package )
    sys.exit( 1 )
  fd = open( os.path.join( ch.getPackageDir( package ), "site.cfg" ), "w" )
  fd.write( """\
[DEFAULT]
library_dirs=%s
include_dirs=%s
""" % ( ", ".join( ch.getPrefixLibDirs() ), ", ".join( ch.getPrefixIncludeDirs() ) ) )
  fd.close()

  packageDir = ch.getPackageDir( package )
  if package == "matplotlib":
    shutil.copy( os.path.join( here, "setupext.py" ),
                 os.path.join( packageDir, "setupext.py" ) )

  if not ch.easyInstall( packageDir ):
    logging.error( "Could not deploy %s", package )
    logging.info( "Trying pip" )
    if not ch.pip( "%s==%s" % ( package, versions[package] ) ):
      logging.error( "Could not pip %s", package )
      sys.exit( 1 )
