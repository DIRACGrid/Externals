#!/usr/bin/env python

import imp, os, sys, re, shutil
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
prefix = ch.getPrefix()

def deleteObjects( regexFilter, onlyFiles = False, onlyDirs = False, removeEmptyDirs = True, dirToExplore = False ):
  if not dirToExplore:
    dirToExplore = prefix
  numEntries = 0
  for objName in os.listdir( dirToExplore ):
    objPath = os.path.join( dirToExplore, objName )
    isDir = os.path.isdir( objPath )
    if isDir:
      entriesInSubDir = deleteObjects( regexFilter, onlyFiles, onlyDirs, removeEmptyDirs, objPath )
      if entriesInSubDir == 0 and removeEmptyDirs:
        os.rmdir( objPath )
        continue
    if isDir and onlyFiles:
      numEntries += 1
      continue
    isFile = os.path.isfile( objPath )
    if isFile and onlyDirs:
      numEntries += 1
      continue
    if regexFilter.search( objName ):
      if isFile:
        os.unlink( objPath )
        continue
      if isDir:
        shutil.rmtree( objPath )
        continue
    numEntries += 1
  return numEntries

def stripObjects( dirToExplore = False ):
  if not dirToExplore:
    dirToExplore = prefix
  numEntries = 0
  for objName in os.listdir( dirToExplore ):
    objPath = os.path.join( dirToExplore, objName )
    if os.path.isdir( objPath ):
      stripObjects( objPath )
    elif os.path.isfile( objPath ) and not os.path.islink( objPath ):
      os.system( "strip '%s' 2>/dev/null" % objPath )

darwinVer = ch.getDarwinVersion()

#Delete pycs and pyos
deleteObjects( re.compile( ".*\.pyc$" ), onlyFiles = True )
deleteObjects( re.compile( ".*\.pyo$" ), onlyFiles = True )
deleteObjects( re.compile( ".*\.a$" ), onlyFiles = True )
deleteObjects( re.compile( "^test$" ), onlyDirs = True )
deleteObjects( re.compile( "^ssl$" ), onlyDirs = True )
deleteObjects( re.compile( "^man$" ), onlyDirs = True )

if not darwinVer:
  stripObjects()
