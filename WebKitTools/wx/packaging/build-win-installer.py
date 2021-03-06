#!/usr/bin/python

# Copyright (C) 2008 Kevin Ollivier  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY APPLE COMPUTER, INC. ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Create a Windows installer package for wxPython wxWebKit binaries

import sys, os, string
import commands
import glob
from subprocess import *

# Find InnoSetup executable
def getInnoSetupPath():
    name = "ISCC.exe"
    retval = ""
    dirs = os.environ["PATH"].split(":")
    # Add the default file path
    dirs.append("C:\\Program Files\\Inno Setup 5")
                    
    if os.environ.has_key("INNO5"):
        retval = os.environ["INNO5"]
    
    if retval == "":
        for dir in dirs:
            filepath = os.path.join(dir, name)
            if os.path.isfile(filepath):
                retval = filepath
            
    return retval
    
def getWebKitOutputDir():
    retval = ""
    if os.environ.has_key("WEBKITOUTPUTDIR"):
        retval = os.environ["WEBKITOUTPUTDIR"]
        
    if retval == "":
        retval = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "WebKitBuild"))
        
    return os.path.join(retval, "Release")

def getRevisionString():
    pipe = Popen("svnversion", shell=True, stdout=PIPE).stdout
    svnrevision = pipe.read().strip()
    print "r" + svnrevision
    svnrevision = string.split(svnrevision, ":")[0]
    svnrevision = svnrevision.replace("M", "")
    svnrevision = "r" + svnrevision
    
    return svnrevision

if __name__ == "__main__":
    innoSetup = getInnoSetupPath()
    buildDir = getWebKitOutputDir()
    os.chdir(sys.path[0])

    svnrevision = getRevisionString()

    if not os.path.exists(innoSetup):
        print "ERROR: Cannot find InnoSetup."
        #sys.exit(1)
        
    if not os.path.exists(buildDir):
        print "ERROR: Build dir %s doesn't exist." % buildDir
        sys.exit(1)

    fileList = """
CopyMode: alwaysoverwrite; Source: *.pyd;        DestDir: "{app}"
CopyMode: alwaysoverwrite; Source: *.py;        DestDir: "{app}"
"""
    
    dlls = glob.glob(os.path.join(buildDir, "*.dll"))
    for dll in dlls:
        if dll.find("wxbase") == -1 and dll.find("wxmsw") == -1:
            fileList += """CopyMode: alwaysoverwrite; Source: %s;        DestDir: "{app}" \n""" % dll

    installerTemplate = open("wxWebKitInstaller.iss.in", "r").read()

    installerTemplate = installerTemplate.replace("<<VERSION>>", svnrevision)
    installerTemplate = installerTemplate.replace("<<ROOTDIR>>", buildDir )
    installerTemplate = installerTemplate.replace("<<PYTHONVER>>", "2.5" )
    installerTemplate = installerTemplate.replace("<<FILES>>", fileList )

    outputFile = open("wxWebKitInstaller.iss", "w")
    outputFile.write(installerTemplate)
    outputFile.close()

    success = os.system('"%s" wxWebKitInstaller.iss' % innoSetup)
    sys.exit(success)
