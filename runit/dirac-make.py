#!/usr/bin/env python

import imp, os, sys, shutil
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

versions = { 'runit' : "2.1.1" }
ch.setPackageVersions( versions )

if not ch.downloadPackage( "runit" ):
  logging.error( "Could not download runit" )
  sys.exit( 1 )

if not ch.unTarPackage( "runit" ):
  logging.error( "Could not deploy runit" )
  sys.exit( 1 )

#Hack because runit is badly packaged
runitDir = "runit-%s" % versions[ 'runit' ]
os.rename( os.path.join( here, "admin", runitDir ), os.path.join( here, runitDir ) )

darwinVer = ch.getDarwinVersion()
if darwinVer:
  fd = open( os.path.join( ch.getPackageDir( 'runit' ), "src", "conf-ld" ), "w" )
  fd.write( "cc -Xlinker -x\n" )
  fd.close()
  ch.replaceInFile( os.path.join( ch.getPackageDir( 'runit' ), 'src', "Makefile" ),
                    " -static", "" )

logging.info( "Moding commands" )
ch.replaceInFile( os.path.join( ch.getPackageDir( 'runit' ), 'src', 'Makefile' ),
                  "IT=", "IT=runsvctrl runsvstat " )
commandsFilePath = os.path.join( ch.getPackageDir( 'runit' ), "package", "commands" )
fd = open( commandsFilePath, "a" )
fd.write( "runsvctrl\nrunsvstat\n" )
fd.close()

for step in ( "compile", ):
  logging.info( "Executing %s step" % step )
  if not ch.execRaw( os.path.join( "package", step ), cwd = ch.getPackageDir( "runit" ) ):
    logging.error( "Could not deploy runit" )
    sys.exit( 1 )

binDir = os.path.join( ch.getPrefix(), "bin" )
if not os.path.isdir( binDir ):
  os.makedirs( binDir )
fd = open( commandsFilePath, "r" )
commands = [ line.strip() for line in fd.readlines() if line.strip() ]
fd.close()
for cmd in commands:
  logging.info( "Copying %s to %s" % ( cmd, binDir ) )
  shutil.copy( os.path.join( ch.getPackageDir( 'runit' ), "command", cmd ), binDir )
