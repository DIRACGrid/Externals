#!/usr/bin/env python

import imp, os, sys, platform, urllib

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

versions = { 'Python' : "2.7.8" }

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

pythonFile = "Python-%s.tgz" % versions[ 'Python' ]
pythonFilePath = os.path.join( here, pythonFile )

if not os.path.isfile( pythonFilePath ):
  try:
    urllib.urlretrieve( "http://python.org/ftp/python/%s/%s" % ( versions[ 'Python' ], pythonFile ),
                        os.path.join( here, pythonFile ) )
  except Exception as e:
    ch.ERROR( "Could not retrieve python 2.7: %s" % e )
    sys.exit( 1 )


ch.setPackageVersions( versions )
if True:
  if not ch.unTarPackage( "Python" ):
    ch.ERROR( "Could not untar python" )
    sys.exit( 1 )

  prefix = ch.getPrefix()
  #configureArgs = "CFLAGS='-L%s/lib' CPPFLAGS='-I%s/include -I%s/include/ncurses'" % ( prefix, prefix, prefix )
  configureArgs = " --enable-shared --enable-static --enable-unicode=ucs4 "

  if not ch.doConfigure( "Python", extraArgs = configureArgs ):
    ch.ERROR( "Could not deploy Python" )
    sys.exit( 1 )

  for func in ( ch.doMake, ch.doInstall ):
    if not func( "Python" ):
      ch.ERROR( "Could not deploy Python" )
      sys.exit( 1 )

if not ch.pythonExec( os.path.join( here, "distribute_setup.py" ) ):
  ch.ERROR( "Could not install distribute" )
  sys.exit( 1 )

if not ch.pythonExec( os.path.join( here, "ez_setup.py" ) ):
  ch.ERROR( "Could not install ez_setup" )
  sys.exit( 1 )

if not ch.pythonExec( os.path.join( here, "get-pip.py" ) ):
  ch.ERROR( "Could not install pip" )
  sys.exit( 1 )
