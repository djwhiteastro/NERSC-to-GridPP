'''
Script to register files on GridPP using DiracTools, post-transfer
'''

import os
import sys
import argparse
import stat
import uuid
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

description = "Script to register data to GridPP that exist on storage"


def parse_command_line():
    """
    Parser of command line arguments for transfer_and_register.py
    """
    
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-s", "--source", metavar='<source-url>',
        default="gsiftp://dtn01.nersc.gov/global/projecta/projectdirs/lsst/"+
        "groups/CS/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double/",
        help="Source (with protocol, e.g. srm://)")

    parser.add_argument("-d", "--dest", metavar='<dest-url>',
        default="gsiftp://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data"+
        "/lsst/lsst/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double/",
        help="Destination (with protocol, e.g. gsiftp://) on GridPP system")

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

    for file in filelist:
        _, fname = os.path.split(file)
        lfn = lfnpath+fname
        if not lfn_exists(fc, lfn):
            info = gf.stat(file)
            chksum = gf.checksum(file, "adler32")

            infoDict = {}
            infoDict['PFN'] = file
            infoDict['Size'] = int(info.st_size)
            infoDict['SE'] = se
            infoDict['GUID'] = str(uuid.uuid4())
            infoDict['Checksum'] = chksum

            fileDict = {}
            fileDict[lfn] = infoDict

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


def main():
    # args = arguments()

    # Strip arguments so command below doesn't throw error
    # DIRAC does not work otherwise
    sys.argv = [sys.argv[0]] 
    from DIRAC.Core.Base import Script
    Script.parseCommandLine( ignoreErrors = True )

    if not args.dest.endswith("/") or not args.lfnpath.endswith("/"):
        raise Exception("Destination and/or LFN Path must be a directory "+
        "ending with a '/'")

    # # dirac = Dirac()
    fcat = FileCatalog()

    ### TODO - load file list

    register(fcat, files, args.se, args.lfnpath)


if __name__ == "__main__":

    args = parse_command_line()
    main()

