
from __future__ import print_function

import os
import sys
import urllib
import zipfile
import shutil

# Include cStringIO in case its available, since its faster
try: from cStringIO import StringIO
except: from StringIO import StringIO

class SubmoduleDownloader:

    """ Util class to download and extract (sub-)modules from github """

    @staticmethod
    def download_submodule(author, module_name, dest_path, ignore_list):
        """ Downloads a submodule from the given author and module name, and extracts
        all files which are not on the ignore_list to the dest_path.

        Example: download_submodule("tobspr", "RenderPipeline", ".", ["README.md", "LICENSE"])
         """

        # Make directory, if it does not exist yet
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)

        # Construct download url
        source_url = "https://github.com/" + author + "/" + module_name + "/archive/master.zip"
        prefix = module_name + "-master"
        print("Fetching:", source_url)

        # Download the zip
        try:
            usock = urllib.urlopen(source_url)
            zip_data = usock.read()
            usock.close()
        except Exception as msg:
            print("ERROR: Could not fetch module", module_name, "! Reason:", msg, file=sys.stderr)
            sys.exit(2)

        # Extract the zip
        zip_ptr = StringIO(zip_data)

        try:
            zip_handle = zipfile.ZipFile(zip_ptr)
        except zipfile.BadZipfile:
            print("ERROR: Invalid zip file!", file=sys.stderr)
            sys.exit(3)

        if zip_handle.testzip() is not None:
            print("ERROR: Invalid zip file checksums!", file=sys.stderr)
            sys.exit(1)

        for fname in zip_handle.namelist():
            rel_name = fname.replace(prefix, "").strip()
            rel_name = rel_name.replace("\\", "/").lstrip("/")
            
            if not rel_name:
                continue

            is_file = not rel_name.endswith("/")
            rel_name = os.path.join(dest_path, rel_name.rstrip("/"))

            # Files
            if is_file:
                for ignore in ignore_list:
                    if ignore in rel_name:
                        break
                else:
                    print("Writing", rel_name)
                    with zip_handle.open(fname, "r") as source, open(rel_name, "wb") as dest:
                            shutil.copyfileobj(source, dest)
                            
            # Directories
            else:
                if not os.path.isdir(rel_name):
                    print("Creating", rel_name)
                    os.makedirs(rel_name)

        print("Done!")
