#!/usr/bin/env python

import imp, os, sys, platform, urllib

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

versions = { 'Python' : "2.5.5" }

prefix = ch.getPrefix()

libDirs = []

for i in ( "lib", "lib64" ):
  libPath = os.path.join( prefix, i )
  if os.path.isdir( libPath ):
    libDirs.append( libPath )

env = {}
env[ 'LD_LIBRARY_PATH' ] = ":".join( libDirs )
if 'LD_LIBRARY_PATH' in os.environ:
  env[ 'LD_LIBRARY_PATH' ] += ":%s" % os.environ[ 'LD_LIBRARY_PATH' ]
env[ 'CPPFLAGS' ] = "-I%s/include -I%s/include/ncurses" % ( prefix, prefix )
#env[ 'CFLAGS' ] = "-I%s/include -I%s/include/ncurses" % ( prefix, prefix )
env[ 'LDFLAGS' ] = " ".join( [ "-L%s" % libPath for libPath in libDirs ] )
print env
ch.setDefaultEnv( env )

darwinVer = ch.getDarwinVersion()

pythonFile = "Python-%s.tar.bz2" % versions[ 'Python' ]
pythonFilePath = os.path.join( here, pythonFile )
if not os.path.isfile( pythonFilePath ):
  try:
    urllib.urlretrieve( "http://python.org/ftp/python/%s/%s" % ( versions[ 'Python' ] , pythonFile ),
                        os.path.join( here, pythonFile ) )
  except Exception, e:
    ch.ERROR( "Could not retrieve python 2.5: %s" % e )
    sys.exit( 1 )

ch.setPackageVersions( versions )
if not ch.unTarPackage( "Python" ):
  ch.ERROR( "Could not untar python" )
  sys.exit( 1 )

prefix = ch.getPrefix()
#configureArgs = "CFLAGS='-L%s/lib' CPPFLAGS='-I%s/include -I%s/include/ncurses'" % ( prefix, prefix, prefix )
configureArgs = ""

#Hack for python2.5 and Leopard

if darwinVer == "10.6":
  env = ch.getDefaultEnv()
  env[ 'MACOSX_DEPLOYMENT_TARGET' ] = "10.5"
  #configureArgs = "--enable-universalsdk=/"
  ch.setDefaultEnv( env )

if not ch.doConfigure( "Python", extraArgs = configureArgs ):
  ch.ERROR( "Could not deploy Python" )
  sys.exit( 1 )

for func in ( ch.doMake, ch.doInstall ):
  if not func( "Python" ):
    ch.ERROR( "Could not deploy Python" )
    sys.exit( 1 )

if not ch.pythonExec( os.path.join( here, "ez_setup.py" ) ):
  ch.ERROR( "Could not install setuptools" )
  sys.exit( 1 )

if not ch.pythonExec( os.path.join( here, "distribute_setup.py" ) ):
  ch.ERROR( "Could not install Distribute" )
  sys.exit( 1 )

if not ch.easyInstall( "setuptools" ):
  ch.ERROR( "Could not install setuptools" )
  sys.exit( 1 )

if not ch.easyInstall( "pip" ):
  ch.ERROR( "Could not install setuptools" )
  sys.exit( 1 )
