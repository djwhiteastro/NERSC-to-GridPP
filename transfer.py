'''
Script to transfer data using gfal2
'''

import os
import sys
import argparse
import stat
import uuid
import gfal2

description = "Script to transfer data to GridPP"


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

    parser.add_argument("-o", "--output", metavar='<out_file>',
        default="transferred.txt", 
        help="File to store list of transferred files")

    return parser.parse_args()



def transfer(gf, filelist, dest, outfile):
    """
    Transfers each file in a list to a destination directory
    """
    with open(outfile, 'a') as out:
        for file in filelist:
            info = gf.stat(file)
            size = info.st_size
            chksum = gf.checksum(file, 'ADLER32')

            params = gf.TransferParameters()
            params.overwrite = True # Need to overwrite for checksum diff
            params.checksum_check = True

            if not stat.S_ISDIR(info.st_mode): # Ignore directories
                _, fname = os.path.split(file)  # Filecopy needs to know end
                                                # filename
                dest_file = dest+fname
                if not dest_file_exists(gf, chksum, dest_file):
                    print("Transferring {} to {}".format(file, dest))
                    gf.filecopy(params, file, dest_file)
                    out.write("{0} {1} {2}\n".format(dest_file, size, chksum))


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
                "checking if path is a directory: {}".format(msg))
    else:
        return True


def dest_file_exists(gf, s_chksum, dest_file):
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
        if s_chksum == dest_chksum: # If yes, don't transfer
            return True
        else: # If not, okay to transfer and overwrite
            return False


def main(args):

    if not args.dest.endswith("/") :
        raise Exception("Destination Path must be a directory "+
        "ending with a '/'")

    gfal = gfal2.creat_context()

    if is_dir(gfal, args.source):
        files = list_files(gfal, args.source)
        print(files)
    else:
        files = [args.source]

    gfal.mkdir_rec(args.dest, 0755)
    transfer(gfal, files, args.dest, args.output)

if __name__ == "__main__":

    arguments = parse_command_line()
    main(arguments)