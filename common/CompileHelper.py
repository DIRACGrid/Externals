""" some utilities for compiling
"""

import sys
import os
import getopt
import shutil
import platform
import re
import urllib2
import logging
import ssl

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG)

try:
  import subprocess
  useSubprocess = True
except ImportError:
  import popen2
  useSubprocess = False

PKG_SOURCE = "http://lhcbproject.web.cern.ch/lhcbproject/dist/DIRAC3/Externals"

class CompileHelper(object):

  def __init__( self, packageRoot ):
    packageRoot = os.path.realpath( packageRoot )
    self.__packageRoot = packageRoot
    self.__moduleName = os.path.basename( packageRoot )
    self.__externalsRoot = self.getExternalsRoot()
    self.__platform = False
    self.__prefix = False
    self.__enableDebug = False
    self.__makeJobs = 1
    self.__redirectOutput = False
    self.__packageVersions = {}
    self.__defaultEnv = {}
    self.__processCommandLine()
    if self.__prefix:
      if "PATH" in os.environ and os.environ['PATH']:
        os.environ['PATH'] = "%s:%s" % ( os.path.join( self.__prefix, 'bin' ), os.environ['PATH'] )
      else:
        os.environ['PATH'] = os.path.join( self.__prefix, 'bin' )
      if "LD_LIBRARY_PATH" in os.environ and os.environ['LD_LIBRARY_PATH']:
        os.environ['LD_LIBRARY_PATH'] = "%s:%s" % ( os.path.join( self.__prefix, 'lib' ), os.environ['LD_LIBRARY_PATH'] )
      else:
        os.environ['LD_LIBRARY_PATH'] = os.path.join( self.__prefix, 'lib' )

  def getDarwinVersion( self ):
    return ".".join( platform.mac_ver()[0].split( "." )[:2] )

  def replaceInFile( self, filePath, replacedStr, newStr ):
    fd = open( filePath )
    data = fd.read()
    fd.close()
    data = data.replace( replacedStr, newStr )
    fd = open( filePath, "w" )
    fd.write( data )
    fd.close()

  def replaceREInFile( self, filePath, replacedRE, newStr ):
    fd = open( filePath )
    data = fd.read()
    fd.close()
    newData = []
    for line in data.split( "\n" ):
      newData.append( re.sub( replacedRE, newStr, line ) )
    fd = open( filePath, "w" )
    fd.write( "\n".join( newData ) )
    fd.close()

  def setPackageVersions( self, versions ):
    self.__packageVersions = versions

  def setDefaultEnv( self, env ):
    self.__defaultEnv = env

  def getDefaultEnv( self ):
    return self.__defaultEnv

  def __processCommandLine( self ):
    self.cmdOpts = ( ( 'h', 'help', 'Show this help' ),
                     ( 'p:', 'prefix=', 'Set the compilation prefix' ),
                     ( 'l:', 'platform=', 'Use <platfom> instead of autodiscovered one' ),
                     ( 'd', 'debug', 'Enable debug output' ),
                     ( 'j:', 'makeJobs=', 'Number of make jobs, by default is 1' ),
                     ( 'o:', 'redirectOutputTo=', 'Redirect commands output to <file>' ),)
    optList, args = getopt.getopt( sys.argv[1:],
                                   "".join( [ opt[0] for opt in self.cmdOpts ] ),
                                   [ opt[1] for opt in self.cmdOpts ] )
    for o, v in optList:
      if o in ( '-h', '--help' ):
        print "Usage %s <opts>" % sys.argv[0]
        for cmdOpt in self.cmdOpts:
          print "%s %s : %s" % ( cmdOpt[0].ljust( 4 ), cmdOpt[1].ljust( 15 ), cmdOpt[2] )
        sys.exit( 1 )
      elif o in ( '-d', '--debug' ):
        self.__enableDebug = True
      elif o in ( '-p', '--prefix' ):
        self.__prefix = os.path.abspath( v )
      elif o in ( '-l', '--platform' ):
        self.__platform = v
      elif o in ( '-j', '--makeJobs' ):
        try:
          self.__makeJobs = int( v )
        except:
          logging.error( "Make jobs has to be a number" )
          sys.exit( 1 )
      elif o in ( '-o', '--redirectOutputTo' ):
        self.__redirectOutput = os.path.abspath( v )


    #Check defaults
    if not self.__platform:
      self.__platform = self.__discoverPlatform()
    if not self.__prefix:
      self.__prefix = self.__discoverPrefix()

    logging.debug( "PLATFORM : %s", self.__platform )
    logging.debug( "PREFIX : %s", self.__prefix )


  def getExternalsRoot( self ):
    return os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )

  def __discoverPlatform( self ):
    pList = [ os.path.join( self.__externalsRoot, "dirac-platform.py" ) ]
    for diracPlatform in pList:
      if os.path.isfile( diracPlatform ):
        if useSubprocess:
          sp = subprocess.Popen( diracPlatform, stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                                 close_fds = True )
        else:
          sp = popen2.Popen3( diracPlatform )
        if sp.wait():
          continue
        if useSubprocess:
          return sp.stdout.read().strip()
        else:
          return sp.fromchild.read().strip()
    return None

  def __discoverPrefix( self ):
    return os.path.join( self.__externalsRoot, self.__platform )

  def getPlatform( self ):
    return self.__platform

  def getPrefix( self ):
    prefix = self.__prefix
    if not os.path.isdir( prefix ):
      os.makedirs( prefix )
    return prefix

  def downloadPackage( self, package, remoteLocation = '' ):
    if package in self.__packageVersions:
      package = "%s-%s" % ( package, self.__packageVersions[ package ] )
    logging.info( "Finding %s", package )
    for tarExt in ( "tar.gz", "tar.bz2", "tgz", "tbz2" ):
      tarLoc = os.path.join( self.__packageRoot, "%s.%s" % ( package, tarExt ) )
      if os.path.isfile( tarLoc ):
        logging.info( "%s exists", tarLoc )
        return True
    logging.info( "No %s found locally, downloading", package )
    remoteLocs = []
    if remoteLocation:
      name = package
      last = remoteLocation.split("/")[-1]
      for tarExt in ( "tar.gz", "tar.bz2", "tgz", "tbz2" ):
        if last.find( tarExt ) > -1:
          name = "%s.%s" % ( name, tarExt )
          break
      remoteLocs.append( ( remoteLocation, os.path.join( self.__packageRoot, name ) ) )
    else:
      for tarExt in ( "tar.gz", "tar.bz2" ):
        remoteLocs.append( ( "%s/%s/%s.%s" % ( PKG_SOURCE, self.__moduleName, package, tarExt ),
                             os.path.join( self.__packageRoot, "%s.%s" % ( package, tarExt ) ) ) )
    for remoteURL, localFile in remoteLocs:
      logging.info( "Trying to download %s", remoteURL )
      try:
        context = ssl._create_unverified_context()
        remote = urllib2.urlopen( remoteURL, context = context )
      except Exception as e:
        logging.error( "Cannot retrieve %s: %s", remoteURL, str(e) )
        continue
      try:
        local = open( localFile, "wb" )
      except IOError, e:
        logging.error( "Cannot open %s; %s", localFile, str(e) )
      try:
        data = remote.read( 262144 )
        while data:
          local.write( data )
          data = remote.read( 262144 )
        local.close()
        remote.close()
        logging.info( "Downloaded %s", localFile )
        return True
      except Exception as e:
        logging.error( "Error reading from %s: %s", remoteURL, str(e) )
        try:
          os.unlink( localFile )
        except:
          pass
    return False


  def unTarPackage( self, package ):
    if package in self.__packageVersions:
      package = "%s-%s" % ( package, self.__packageVersions[ package ] )
    logging.info( "Untaring %s", package )
    p = os.path.join( self.__packageRoot, package )
    if os.path.isdir( p ):
      logging.debug( "Deleting %s", p )
      shutil.rmtree( p )
    for gzExt in ( "tar.gz", "tgz" ):
      p = os.path.join( self.__packageRoot, "%s.%s" % ( package, gzExt ) )
      logging.debug( "Trying %s", p )
      if os.path.isfile( p ):
        if not os.system( "cd '%s'; tar xzf '%s'" % ( self.__packageRoot, p ) ):
          return True
        else:
          logging.error( "Could not untar %s", p )
    for gzExt in ( "tar.bz2", "tbz" ):
      p = os.path.join( self.__packageRoot, "%s.%s" % ( package, gzExt ) )
      logging.debug( "Trying %s", p )
      if os.path.isfile( p ):
        if not os.system( "cd '%s'; tar xjf '%s'" % ( self.__packageRoot, p ) ):
          return True
        else:
          logging.error( "Could not untar %s", p )
    return False

  def getPackageDir( self, package ):
    if package in self.__packageVersions:
      package = "%s-%s" % ( package, self.__packageVersions[ package ] )
    return os.path.join( self.__packageRoot, package )

  def __findDirs( self, baseDir, validFileExts ):
    dirs = []
    for t in os.walk( baseDir ):
      valid = False
      for fileInDir in t[2]:
        if valid:
          break
        for fext in validFileExts:
          fPos = len( fileInDir ) - len( fext )
          if fileInDir.find( fext, fPos ) == fPos:
            valid = True
            break
      if valid and t[0] not in dirs:
        dirs.append( t[0] )
    return dirs

  def execRawAndGetOutput( self, command, env = None, cwd = None ):
    if useSubprocess:
      sb = subprocess.Popen( command, shell = True, env = env, stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE, close_fds = True, cwd = cwd )
      if sb.wait():
        return False
      return ( sb.stdout.read(), sb.stderr.read() )
    else:
      if cwd:
        command = "cd '%s'; %s" % ( cwd, command )
      if env:
        envList = []
        for k in env:
          envList.append( "export %s='%s'" % ( k, env[k] ) )
        envStr = "; ".join( envList )
        if envStr:
          envStr += ";"
        command = "%s; %s" % ( envStr, command )
      sb = popen2.Popen4( command )
      if sb.wait():
        return False
      return ( sb.fromchild.read(), "" )

  def execRaw( self, command, env = None, cwd = None ):
    if self.__redirectOutput:
      fd = open( self.__redirectOutput, "a" )
      fd.write( "%s\n%s\n%s\n" % ( "="*20, command, "="*20 ) )
      fd.close()
      command = "%s >>'%s' 2>&1" % ( command, self.__redirectOutput )
    if useSubprocess:
      sb = subprocess.Popen( command, shell = True, env = env, cwd = cwd )
      return sb.wait() == 0
    else:
      if cwd:
        command = "cd '%s'; %s" % ( cwd, command )
      if env:
        envList = []
        for k in env:
          envList.append( "export %s='%s'" % ( k, env[k] ) )
        envStr = "; ".join( envList )
        if envStr:
          envStr += ";"
        command = "%s; %s" % ( envStr, command )
      return os.system( command ) == 0

  def getPrefixLibDirs( self ):
    return self.__findDirs( os.path.join( self.__prefix, "lib" ), ( ".so", ".a" ) )

  def getPrefixIncludeDirs( self ):
    return self.__findDirs( os.path.join( self.__prefix, "include" ), ( ".h", ".hpp" ) )

  def getCommandEnv( self, env = {}, autoEnv = True, discoverEnv = False ):
    cmdEnv = dict( os.environ )
    if discoverEnv:
      libPaths = self.__findDirs( os.path.join( self.__prefix, "lib" ), ( ".so", ".a" ) )
      libPaths += self.__findDirs( os.path.join( self.__prefix, "lib64" ), ( ".so", ".a" ) )
      includePaths = self.__findDirs( os.path.join( self.__prefix, "include" ), ( ".h", ".hpp" ) )
      if libPaths:
        cmdEnv[ 'LD_LIBRARY_PATH' ] = ":".join( libPaths )
        if 'LD_LIBRARY_PATH' in os.environ:
          cmdEnv[ 'LD_LIBRARY_PATH' ] = os.environ[ 'LD_LIBRARY_PATH' ]
        cmdEnv[ 'LDFLAGS' ] = "-L%s" % " -L".join( libPaths )
      if includePaths:
        cmdEnv[ 'CPPFLAGS' ] = "-I%s" % " -I".join( includePaths )
    if autoEnv:
      libDirs = []
      for suf in ( 'lib', 'lib64' ):
        libPath = os.path.join( self.__prefix, suf )
        if os.path.isdir( libPath ):
          libDirs.append( libPath )
      if 'LD_LIBRARY_PATH' in cmdEnv:
        cmdEnv[ 'LD_LIBRARY_PATH' ] = "%s:%s" % ( ":".join( libDirs ),
                                                  cmdEnv[ 'LD_LIBRARY_PATH' ] )
      else:
        cmdEnv[ 'LD_LIBRARY_PATH' ] = ":".join( libDirs )
      cmdEnv[ 'CPPFLAGS' ] = "-I%s/include -I%s/include/ncurses" % ( self.__prefix, self.__prefix )
      #env[ 'CFLAGS' ] = "-I%s/include -I%s/include/ncurses" % ( prefix, prefix )
      cmdEnv[ 'LDFLAGS' ] = " ".join( [ "-L%s" % lp for lp in libDirs ] )
    for k in self.__defaultEnv:
      cmdEnv[ k ] = self.__defaultEnv[ k ]
    for k in env:
      cmdEnv[ k ] = env[ k ]
    return cmdEnv

  def execCommand( self, command, package = False , env = {}, autoEnv = True, discoverEnv = False ):
    if package:
      if package in self.__packageVersions:
        package = "%s-%s" % ( package, self.__packageVersions[ package ] )
    cmdEnv = self.getCommandEnv( env, autoEnv, discoverEnv )
    logging.debug( "ENV: %s" % cmdEnv )

    if self.__redirectOutput:
      fd = open( self.__redirectOutput, "a" )
      fd.write( "%s\n%s\n%s\n" % ( "="*20, command, "="*20 ) )
      fd.close()
      command = "%s >>'%s' 2>&1" % ( command, self.__redirectOutput )

    if package:
      cwd = os.path.join( self.__packageRoot, package )
    else:
      cwd = self.__packageRoot

    if not useSubprocess:
      envList = []
      for k in cmdEnv:
        envList.append( "export %s='%s'" % ( k, cmdEnv[k] ) )
      envStr = "; ".join( envList )
      if envStr:
        envStr += ";"
      command = "%s cd '%s'; %s" % ( envStr, cwd, command )

    logging.debug( "Executing %s for package %s" % ( command, package ) )
    if useSubprocess:
      return subprocess.Popen( command, shell = True, cwd = cwd, env = cmdEnv ).wait() == 0
    else:
      return os.system( "%s cd '%s'; %s" % ( envStr, cwd, command ) ) == 0

  def doConfigure( self, package, extraArgs = "", env = {}, configureExecutable = "configure", autoEnv = False ):
    configureCmd = "./%s --prefix='%s' %s" % ( configureExecutable, self.__prefix, extraArgs )
    if 'cmake' in configureExecutable:
      configureCmd = "%s -DCMAKE_INSTALL_PREFIX='%s' %s" % ( configureExecutable, self.__prefix, extraArgs )
    logging.info( "Running %s for %s" % ( configureCmd, package ) )
    return self.execCommand( configureCmd, package, env, autoEnv = autoEnv )

  def doMake( self, package, extraArgs = "", env = {}, makeExecutable = "make", autoEnv = False, makeJobs = 0 ):
    if not makeJobs:
      makeJobs = self.__makeJobs
    makeCmd = "%s -j %d" % ( makeExecutable, makeJobs )
    if extraArgs:
      makeCmd = "%s %s" % ( makeCmd, extraArgs )
    logging.info( "Running %s for %s" % ( makeCmd, package ) )
    return self.execCommand( makeCmd, package, env, autoEnv = autoEnv )

  def doInstall( self, package, extraArgs = "", env = {}, makeExecutable = False, autoEnv = False ):
    if makeExecutable:
      makeCmd = makeExecutable
    else:
      makeCmd = "make -j %d install" % self.__makeJobs
    if extraArgs:
      makeCmd = "%s %s" % ( makeCmd, extraArgs )
    logging.info( "Running %s for %s" % ( makeCmd, package ) )
    return self.execCommand( makeCmd, package, env, autoEnv = autoEnv )

  def deployPackage( self, package, configureArgs = "", skipConfigure = False, configureExecutable = "configure", configureEnv = {},
                     makeSteps = False, makeEnv = {}, makeExecutable = "make", skipMake = False, onlyOneMakeStepRequired = False,
                     installArgs = "", installEnv = {}, installExecutable = False, skipInstall = False, autoEnv = True,
                     makeJobs = 0 ):
    if not self.downloadPackage( package ):
      return False
    self.unTarPackage( package )
    if not skipConfigure:
      if not self.doConfigure( package, extraArgs = configureArgs, env = configureEnv,
                               configureExecutable = configureExecutable, autoEnv = autoEnv ):
        return False
    if not skipMake:
      if not makeSteps:
        makeSteps = [ '' ]
      makeOK = True
      for ms in makeSteps:
        if self.doMake( package, extraArgs = ms, env = makeEnv, makeExecutable = makeExecutable, autoEnv = autoEnv, makeJobs = makeJobs ):
          if onlyOneMakeStepRequired:
            makeOK = True
            break
        else:
          if onlyOneMakeStepRequired:
            makeOK = False
          else:
            return False
      if not makeOK:
        return False
    if not skipInstall:
      if not self.doInstall( package, extraArgs = installArgs, env = installEnv, makeExecutable = installExecutable, autoEnv = autoEnv ):
        return False
    return True

  def pythonExec( self, fileToExec, package = False, extraArgs = "", env = {}, autoEnv = True ):
    pythonExe = os.path.join( self.__prefix, "bin", "python" )
    if not os.path.isfile( pythonExe ):
      logging.error( "Could not find %s", pythonExe )
      return False
    cmd = "'%s' '%s'" % ( pythonExe, fileToExec )
    if extraArgs:
      cmd = "%s %s" % ( cmd, extraArgs )
    logging.info( "Executing %s", cmd )
    return self.execCommand( cmd, package = package, env = env, autoEnv = autoEnv )

  def pythonSetupPackage( self, package, setupCommand, extraArgs = "", env = {}, autoEnv = True ):
    pythonExe = os.path.join( self.__prefix, "bin", "python" )
    if not os.path.isfile( pythonExe ):
      logging.error( "Could not find %s", pythonExe )
      return False
    cmd = "'%s' '%s' '%s'" % ( pythonExe,
                               os.path.join( self.getPackageDir( package ), 'setup.py' ),
                               setupCommand )
    if extraArgs:
      cmd = "%s %s" % ( cmd, extraArgs )
    logging.info( "Executing %s", cmd )
    return self.execCommand( cmd, package = package, env = env, autoEnv = autoEnv )

  def easyInstall( self, packagesToInstall, switches = "-UZ", env = {}, autoEnv = True ):
    pythonExe = os.path.join( self.__prefix, "bin", "python" )
    eaExe = os.path.join( self.__prefix, "bin", "easy_install" )
    for f in ( pythonExe, eaExe ):
      if not os.path.isfile( f ):
        logging.error( "Could not find %s", f )
        return False
    cmd = "'%s' '%s' %s '%s'" % ( pythonExe, eaExe, switches, packagesToInstall )
    logging.info( "Executing %s", cmd )
    return self.execCommand( cmd, env = env, autoEnv = autoEnv )

  def pip( self, package, switches = "", env = {}, autoEnv = True ):
    pythonExe = os.path.join( self.__prefix, "bin", "python" )
    eaExe = os.path.join( self.__prefix, "bin", "pip" )
    for f in ( pythonExe, eaExe ):
      if not os.path.isfile( f ):
        logging.error( "Could not find %s", f )
        return False
    cmd = "%s install %s %s" % ( eaExe, switches, package )
    logging.info( "Executing %s", cmd )
    return self.execCommand( cmd, env = env, autoEnv = autoEnv )


  def copyPostInstall( self ):
    logging.info( "Copying post install scripts" )
    psDir = os.path.join( self.__prefix, "postInstall" )
    if not os.path.isdir( psDir ):
      os.makedirs( psDir )
    packagePsDir = os.path.join( self.__packageRoot, "postInstall" )
    for entry in os.listdir( packagePsDir ):
      if entry == ".svn":
        continue
      shutil.copy( os.path.join( packagePsDir, entry ),
                   os.path.join( psDir, entry ) )
      logging.info( "  Copied %s", entry )
