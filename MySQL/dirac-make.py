#!/usr/bin/env python
#To install this, you need to have ncurses-static installed.

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


versions = { 'mysql' : "5.6.23" }

ch.setPackageVersions( versions )

dataDir = os.path.join( os.path.dirname( ch.getPrefix() ), "mysql" )
if not os.path.isdir( dataDir ):
  os.makedirs( dataDir )

configureArgs = []
configureArgs.append( "-DINSTALL_LIBDIR='%s/lib'" % ch.getPrefix() )
configureArgs.append( "-DINSTALL_BINDIR='%s/bin'" % ch.getPrefix() )
configureArgs.append( "-DINSTALL_SBINDIR='%s/sbin'" % ch.getPrefix() )
configureArgs.append( "-DCMAKE_INSTALL_PREFIX='%s'" % dataDir )

if not ch.deployPackage( "mysql",
                         configureExecutable = "/usr/bin/cmake",
                         configureArgs = " ".join( configureArgs )):
  ch.ERROR( "Could not deploy package mysql" )
  sys.exit( 1 )

etcDir = os.path.join( dataDir, "etc" )
if not os.path.isdir( etcDir ):
  os.makedirs( etcDir )

shutil.copy( os.path.join( here, "my-huge.cnf" ),
             os.path.join( etcDir, "my.cnf" ) )

