#!/usr/bin/env python

import imp
import os
import sys
import urllib
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

versions = { 'openldap' : "2.4.45",
             'python-ldap' : '3.0.0b4' }

ldapFile = "openldap-%s.tgz" % versions[ 'openldap' ]
ldapFilePath = os.path.join( here, ldapFile )
if not os.path.isfile( ldapFilePath ):
  try:
    logging.info( "Retrieving %s", ldapFile )
    urllib.urlretrieve( "ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/%s" % ( ldapFile ),
                        ldapFilePath )
  except Exception as e:
    logging.error( "Could not retrieve ldap: %s" % e )
    sys.exit( 1 )


ch.setPackageVersions( versions )
if True:
  ch.setDefaultEnv( { 'CFLAGS' : "-g -O2 -D_GNU_SOURCE" } )
  if not ch.deployPackage( 'openldap', makeSteps = [ 'depend', '' ],
                           configureArgs = "--enable-slapd=no --without-tls --enable-slurpd=no --enable-shared" ):
    logging.error( "Could not deploy openldap" )
    sys.exit( 1 )

ch.setDefaultEnv( {} )
if not ch.downloadPackage( 'python-ldap' ):
  logging.error( "Could not download python-ldap" )
  sys.exit( 1 )

if not ch.unTarPackage( 'python-ldap' ):
  logging.error( "Could not untar python-ldap" )
  sys.exit( 1 )

setupFile = os.path.join( ch.getPackageDir( 'python-ldap' ), 'setup.cfg' )
print setupFile
ch.replaceREInFile( setupFile, r"^libs *=.*$", "libs = ldap_r lber" )
ch.replaceREInFile( setupFile, r"^library_dirs *=.*$", "library_dirs = %s" % os.path.join( ch.getPrefix(), "lib" ) )
ch.replaceREInFile( setupFile, r"^include_dirs *=.*$", "include_dirs = %s" % os.path.join( ch.getPrefix(), "include" ) )
if not ch.pythonSetupPackage( "python-ldap", "install" ):
  logging.error( "Could not deploy python-ldap" )
  sys.exit( 1 )
