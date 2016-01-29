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

trashDir = os.path.join( os.path.dirname( ch.getPrefix() ), "trash" )
if not os.path.isdir( trashDir ):
  os.makedirs( trashDir )

configureArgs = []
configureArgs.append( "-DCMAKE_INSTALL_PREFIX='%s'" % ch.getPrefix() )
configureArgs.append( "-DINSTALL_SUPPORTFILESDIR='%s/share/mysql'" % dataDir )

# We do not need thos
configureArgs.append( "-DINSTALL_MYSQLTESTDIR='%s'" % trashDir )
configureArgs.append( "-DINSTALL_INFODIR='%s'" % trashDir )
configureArgs.append( "-DINSTALL_DOCDIR='%s'" % trashDir )
configureArgs.append( "-DINSTALL_DOCREADMEDIR='%s'" % trashDir )
configureArgs.append( "-DINSTALL_MANDIR='%s'" % trashDir )

configureArgs.append( "-DWITH_EMBEDDED_SERVER=0" )

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

