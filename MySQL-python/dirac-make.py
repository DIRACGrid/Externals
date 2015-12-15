#!/usr/bin/env python

import imp
import os
import sys
import shutil

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

versions = { 'MySQL-python' : "1.2.5" }
ch.setPackageVersions( versions )

if not ch.downloadPackage( 'MySQL-python' ):
  ch.ERROR( "Could not deploy MySQL-python" )
  sys.exit( 1 )

if not ch.unTarPackage( 'MySQL-python' ):
  ch.ERROR( "Could not deploy MySQL-python" )
  sys.exit( 1 )

packageDir = ch.getPackageDir( "MySQL-python" )

shutil.copy( os.path.join( here, "setup_posix.py" ),
             os.path.join( packageDir, "setup_posix.py" ) )

sitecfgContents = """\
[options]
# embedded: link against the embedded server library
# threadsafe: use the threadsafe client
# static: link against a static library (probably required for embedded)

embedded = False
threadsafe = True
static = True

# The path to mysql_config.
# Only use this if mysql_config is not on your PATH, or you have some weird
# setup that requires it.
mysql_config = %s/bin/mysql_config
""" % ch.getPrefix()

fd = open( os.path.join( packageDir, "site.cfg" ), "w" )
fd.write( sitecfgContents )
fd.close()

if ch.getDarwinVersion():
  ch.replaceInFile( os.path.join( ch.getPackageDir( "MySQL-python" ), "_mysql.c" ),
                    "#define uint unsigned int", "#define PATATATRONHACKz0R" )

if not ch.easyInstall( packageDir ):
  ch.ERROR( "Could not deploy MySQL-python" )
  sys.exit( 1 )
