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


versions = { 'mysql' : "5.1.53" }

ch.setPackageVersions( versions )

dataDir = os.path.join( os.path.dirname( ch.getPrefix() ), "mysql" )
if not os.path.isdir( dataDir ):
  os.makedirs( dataDir )

env = {}
env[ 'CFLAGS'] = "-O3 -fno-omit-frame-pointer"
env[ 'CXX'] = "g++"
env[ 'CC'] = "gcc"
env[ 'CXXFLAGS'] = "-O3 -fno-omit-frame-pointer -felide-constructors -fno-exceptions -fno-rtti -g"
ch.setDefaultEnv( env )

configureArgs = []
configureArgs.append( "--exec-prefix='%s'" % ch.getPrefix() )
configureArgs.append( "--prefix='%s'" % dataDir )
configureArgs.append( "--localstatedir='%s'" % os.path.join( dataDir, "db" ) )
configureArgs.append( "--sysconfdir='/opt/dirac/pro/mysql/etc'" )
configureArgs.append( "--with-plugins=max-no-ndb" )
configureArgs.append( "--enable-assembler" )
configureArgs.append( "--with-mysqld-ldflags=-all-static" )
configureArgs.append( "--with-client-ldflags=-all-static" )
configureArgs.append( "--enable-thread-safe-client" )
configureArgs.append( "--with-big-tables" )
configureArgs.append( "--without-docs" )
configureArgs.append( "--without-man" )
configureArgs.append( "--without-debug" )
configureArgs.append( "--disable-profiling" )
configureArgs.append( "--includedir='%s'" % os.path.join( ch.getPrefix(), "include" ) )
configureArgs.append( "--with-pic" )
configureArgs.append( "--with-mysqld-ldflags='-lstdc++'" )
configureArgs.append( "--enable-local-infile" )
configureArgs.append( "--with-extra-charsets=complex" )
configureArgs.append( "--with-readline" )

if not ch.deployPackage( "mysql", configureArgs = " ".join( configureArgs ) ):
  ch.ERROR( "Could not deploy package mysql" )
  sys.exit( 1 )

etcDir = os.path.join( dataDir, "etc" )
if not os.path.isdir( etcDir ):
  os.makedirs( etcDir )

shutil.copy( os.path.join( here, "my-huge.cnf" ), 
             os.path.join( etcDir, "my.cnf" ) )

