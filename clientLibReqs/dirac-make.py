#!/usr/bin/env python

import imp, os, sys, platform, urllib2
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')

here = os.path.dirname( os.path.abspath( __file__ ) )
chFilePath = os.path.join( os.path.dirname( here ) , "common", "CompileHelper.py")
try:
  fd = open( chFilePath )
except Exception as e:
  print "Cannot open %s: %s" % ( chFilePath, e )
  sys.exit( 1 )

chModule = imp.load_module( "CompileHelper", fd, chFilePath, ( ".py", "r", imp.PY_SOURCE ) )
fd.close()
chClass = getattr( chModule, "CompileHelper" )

ch = chClass( here )

versions = { 'readline' : "6.3",
             'bzip2' : "1.0.6",
             'zlib' : '1.2.8',
             'ncurses' : "5.9",
             'sqlite' : "3.8.8.3",
             'openssl' : "1.0.2h" }

darwinVer = ch.getDarwinVersion()

ch.setPackageVersions( versions )


compileLibs = True

if compileLibs:

  if not ch.deployPackage( 'zlib', configureArgs = '--shared' ):
    logging.error( "Could not deploy zlib" )
    sys.exit( 1 )

  if not ch.deployPackage( 'readline', configureArgs = '--enable-shared' ):
    logging.error( "Could not deploy readline" )
    sys.exit( 1 )

  if not ch.deployPackage( 'sqlite', configureArgs = '--enable-shared --enable-threadsafe' ):
    ch.ERROR( "Could not deploy sqlite" )
    sys.exit( 1 )

  if not ch.deployPackage( 'bzip2', makeSteps = [ "-f Makefile-libbz2_so", "" ],
                           installArgs = "PREFIX='%s'" % ch.getPrefix(), skipConfigure = True,
                           onlyOneMakeStepRequired = darwinVer ):
    logging.error( "Could not deploy bzip2" )
    sys.exit( 1 )

  if not ch.deployPackage( 'ncurses', configureArgs = '--with-shared --enable-symlinks --enable-const --enable-tcap-names',
                           configureEnv = { "CPPFLAGS": "-P" } ):
    logging.error( "Could not deploy ncurses" )
    sys.exit( 1 )

#OpenSSL

ossltar = os.path.join( here, "openssl-%s.tar.gz" % versions[ 'openssl' ] )
if not os.path.isfile( ossltar ):
  ossurl = "http://www.openssl.org/source/openssl-%s.tar.gz" % ( versions[ 'openssl' ] )
  logging.info( "Downloading %s" % ossurl )
  try:
    furl = urllib2.urlopen( ossurl )
    with open( ossltar, "wb") as localFile:
      localFile.write( furl.read() )

  except Exception as e:
    logging.error( "Could not retrieve openssl %s", e )
    sys.exit( 1 )

if not darwinVer:
  osslConfArgs = "threads shared"
  if not ch.deployPackage( 'openssl', configureArgs = osslConfArgs, configureExecutable = "config",
                           makeSteps = [ '', 'test' ], onlyOneMakeStepRequired = True, makeJobs = 1,
                           skipInstall = True):
    logging.error( "Could not deploy openssl" )
    sys.exit( 1 )
  if not ch.doInstall( 'openssl', makeExecutable='make install_sw' ):
    logging.error( "Could not deploy openssl" )
    sys.exit( 1 )

else:

  if not ch.unTarPackage( 'openssl' ):
    logging.error( "Could not deploy openssl" )
    sys.exit( 1 )

  #Hack to compile without the crappy macosx universal stuff
  osslDir = ch.getPackageDir( 'openssl' )

  if platform.architecture()[0] == "64bit" :
    if not ch.doConfigure( 'openssl', configureExecutable = "Configure", extraArgs = "darwin64-x86_64-cc threads shared" ):
      logging.error( "Could not deploy openssl" )
      sys.exit( 1 )
  else:
    filesToHack = [ os.path.join( osslDir, "Configure" ) ]
    #filesToHack = []
    for f2h in filesToHack:
      print "H4x0ring %s" % f2h
      ch.replaceInFile( f2h, "-arch i386 ", "" )

    if not ch.doConfigure( 'openssl', configureExecutable = "config", extraArgs = "threads shared" ):
      logging.error( "Could not deploy openssl" )
      sys.exit( 1 )

  if not ch.doMake( 'openssl', makeJobs = 1 ):
    logging.error( "Could not deploy openssl" )
    sys.exit( 1 )
  if not ch.doInstall( 'openssl', makeExecutable='make install_sw' ):
    logging.error( "Could not deploy openssl" )
    sys.exit( 1 )
