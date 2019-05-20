'''
Script to transfer data using gfal2, and then register on GridPP using
DiracTools
'''

import os
import sys
import argparse
import stat
import uuid
import gfal2
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog


description = "Script to transfer and register data to GridPP"

# Wrote script to use command line arguments but dirac breaks without including
# it's own command line parser. Rather than rewrite, this is a hack.
# class arguments:
#     source = "gsiftp://dtn01.nersc.gov/global/projecta/projectdirs/lsst/groups/CS/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double/"
#     dest = "gsiftp://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/lsst//lsst/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double/"
#     se = "UKI-LT2-IC-HEP-disk"
#     lfnpath = "/lsst/cosmoDC2/cosmoDC2_v1.1.4_rs_scatter_query_tree_double"
#     transfer = False
#     register = False

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

    parser.add_argument("-t", "--transfer", action='store_true',
                        help="Transfer files")
    parser.add_argument("-r", "--register", action='store_true',
                        help="Register files")

    return parser.parse_args()


def transfer(gf, filelist, dest):
    """
    Transfers each file in a list to a destination directory
    """
    newfiles = []
    for file in filelist:
        info = gf.stat(file)
        if not stat.S_ISDIR(info.st_mode):
            _, fname = os.path.split(file) # Filecopy needs to know end filename
            dest_file = dest+fname
            if not dest_file_exists(gf, file, dest_file):
                params = gf.TransferParameters()
                params.overwrite = True #Need to overwrite for checksum diff
                print("Transferring {} to {}".format(file, dest))
                gf.filecopy(params, file, dest_file)
                newfiles.append(dest_file)
    return newfiles

def register(fc, gf, filelist, se, lfnpath):
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

def list_files(gf, path):
    """
    List each file in a directory
    """
    if not path.endswith("/"):
        path = path+"/"

    filelist = []
    filenames = gf.listdir(path)
    for fname in filenames:
        if not fname.endswith(".") and not fname.endswith(".."):
            file = path+fname
            filelist.append(file)
    return filelist


def is_dir(gf, path):
    """
    Check if the path is a directory or a file
    """
    try:
        gf.listdir(path)
    except Exception as e:
        msg = str(e)
        if "is not a directory" in msg:
            # Passed a file, not a directory
            return False
        else:
            raise Exception("An error was thrown that wasn't expected when "+
                "checking if path is a directory")
    else:
        return True


def dest_file_exists(gf, file, dest_file):
    """
    Check if the file to transfer already exists at the destination
    Uses checksum to verify that an existing file is the same, overwrites if not
    """
    try: # Use checksum to see if file exists - hack but works
        dest_chksum = gf.checksum(dest_file, 'ADLER32')
    except Exception as e:
        msg = str(e)
        if "No such file or directory" in msg:
            #File doesn't exist, okay to transfer
            return False
        else:
            raise e
    else:
        # If file exists, check to make sure it is the same file
        source_chksum = gf.checksum(file, 'ADLER32')
        if source_chksum == dest_chksum: # If yes, don't transfer
            return True
        else: # If not, okay to transfer and overwrite
            return False

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

    gfal = gfal2.creat_context()
    # # dirac = Dirac()
    fcat = FileCatalog()

    if is_dir(gfal, args.source):
        files = list_files(gfal, args.source)
        print(files)
    else:
        files = [args.source]

    if args.transfer and not args.register: # Transfer only
        gfal.mkdir_rec(args.dest, 0755)
        transfer(gfal, files, args.dest)

    elif args.register and not args.transfer: # Register only
        register(fcat, gfal, files, args.se, args.lfnpath)

    else: # Transfer AND Register
        gfal.mkdir_rec(args.dest, 0755)

        regfiles = transfer(gfal, files, args.dest)

        register(fcat, gfal, regfiles, args.se, args.lfnpath)

if __name__ == "__main__":

    args = parse_command_line()
    main()
