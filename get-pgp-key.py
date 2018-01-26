#!/usr/bin/python
import subprocess
import tempfile
import sys
import re
import os

def usage(exitCode):
    print("Usage: %s <key id> <keyring file>" % os.path.basename(sys.argv[0]))
    sys.exit(exitCode)

def fatal(message):
    print(message)
    sys.exit(1)

if len(sys.argv) < 3:
    usage(1)

requestedKey = sys.argv[1]
if requestedKey == '':
    usage(1)
if not re.match(r"[0-9a-fA-F]{16}", requestedKey):
    fatal("Expected key ID to be a 16-hexadecimal character string")

keyringFile = sys.argv[2]
if keyringFile == '':
    usage(1)

try:
    keyHTML = subprocess.check_output(["curl", "http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x" + requestedKey])
except subprocess.CalledProcessError as err:
    fatal(err)

# Extract the GPG key
startTag = "-----BEGIN PGP PUBLIC KEY BLOCK-----"
endTag = "-----END PGP PUBLIC KEY BLOCK-----"

startPgp = keyHTML.find(startTag)
if startPgp == -1:
    fatal("Couldn't find start of PGP key block")

endPgp = keyHTML.find(endTag, startPgp)
if endPgp == -1:
    fatal("Truncated PGP key")

gpgKey = keyHTML[startPgp:endPgp+len(endTag)]

# Output the key to a temporary file
gpgKeyFile, gpgKeyFileName = tempfile.mkstemp(text=True)
os.write(gpgKeyFile, "%s\n" % gpgKey)
os.close(gpgKeyFile)

print(gpgKeyFileName)

# Add it to a GPG keyring
try:
    subprocess.check_call(["gpg", "--no-default-keyring", "--keyring", keyringFile, "--import", gpgKeyFileName])
except subprocess.CalledProcessError as err:
    os.remove(gpgKeyFileName)
    fatal(err)

# Remove the temporary files
os.remove(gpgKeyFileName)
