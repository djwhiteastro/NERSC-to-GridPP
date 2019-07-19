'''
Script to register files on GridPP using DiracTools, post-transfer
'''

import os
import sys
import argparse
import stat
import uuid
from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

description = "Script to register data to GridPP that exist on storage"


def parse_command_line():
    """
    Parser of command line arguments for transfer_and_register.py
    """
    
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input", metavar='<in_file>',
        default="transferred.txt",
        help="File containing list of transferred files")

    parser.add_argument("-e", "--se", default="UKI-LT2-IC-HEP-disk",
        metavar='<storage-element>', help="Storage element to use on Dirac")

    parser.add_argument("-l", "--lfnpath", metavar='<LFN_PATH>',
        default="/lsst/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double/",
        help="LFN Path/folder to register files to (filename added by script)")

    return parser.parse_args()


def register(fc, filelist, se, lfnpath):
    """
    Registers either a single file, or every file in a directory, to the Dirac
    File Catalogue
    """

    if not fc.isDirectory(lfnpath)["Value"]["Successful"][lfnpath]:
        fc.createDirectory(lfnpath)
        if not lfnpath.endswith("/"):
            lfnpath = lfnpath+"/"

    for line in filelist:
        file, size, chksum = line.split()
        _, fname = os.path.split(file)
        lfn = lfnpath+fname
        if not lfn_exists(fc, lfn):

            infoDict = {}
            infoDict['PFN'] = file
            infoDict['Size'] = int(size)
            infoDict['SE'] = se
            infoDict['GUID'] = str(uuid.uuid4())
            infoDict['Checksum'] = chksum

            fileDict = {}
            fileDict[lfn] = infoDict
            print("Adding {} to DIRAC file catalogue".format(lfn))
            result = fc.addFile(fileDict)
            if not result["OK"]:
                raise Exception(result)
            if result["Value"]["Failed"]:
                raise Exception(result)


def lfn_exists(fc, lfn):
    """
    Checks if a given LFN appears in the Dirac File Catalogue
    """
    result = fc.isFile(lfn)

    if not result["OK"]:
        raise Exception(result)
    elif result["Value"]["Successful"][lfn] == lfn:
        return True
    elif not result["Value"]["Successful"][lfn]:
        return False
    else:
        raise Exception(result)


def main(args):
    # Strip arguments so command below doesn't throw error
    # DIRAC does not work otherwise
    sys.argv = [sys.argv[0]] 
    from DIRAC.Core.Base import Script
    Script.parseCommandLine( ignoreErrors = True )

    if not args.lfnpath.endswith("/"):
        raise Exception("LFN Path must be a directory "+
        "ending with a '/'")

    # # dirac = Dirac()
    fcat = FileCatalogClient()
    fcat.exists("/lsst") # Bug where first use of FileCatalogClient fails, but
                         # subsequent uses are fine, so run throwaway command.

    with open(args.input, "r") as infile:
        files = infile.readlines()

        register(fcat, files, args.se, args.lfnpath)


if __name__ == "__main__":

    arguments = parse_command_line()
    main(arguments)

