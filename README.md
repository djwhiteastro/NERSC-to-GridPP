# NERSC-to-GridPP
Tools to 'simplify' transferring data from NERSC to GridPP storage elements.

## Requires

- DIRAC tools - tested with version 6.21.10
- GFAL2 (and python bindings) - tested with version 2.15.2
- Access to relevant systems from local client machine (e.g. via 
voms-proxy-init).

## Environment setup

During development of this tool a bug was found in the version of GFAL that
was accessible with a CernVM via CVMFS. A fix was created, and can be sourced
as below, but this results in incompatibility with DIRAC. It is not possible
to have access to both GFAL and DIRAC tools in the same environment as things
currently stand. Therefore, the script has been split in to two stages (with 
the previous version retained for posterity and ease of update if things are 
fixed later on).

If using a CernVM (with SL6/Centos6), the following will source the correct
version of GFAL:

```
source /cvmfs/grid.cern.ch/umd-sl6ui-test/etc/profile.d/setup-ui-example.sh
```

To access DIRAC tools, in a clean environment, use:

```
source /cvmfs/ganga.cern.ch/dirac_ui/bashrc 
```

For both cases, a valid proxy is required. For ease of use, set up for the
longest valid time allowed:

```
voms-proxy-init --voms lsst --valid 24:00
```

If using a system without CernVM, similar incompatibilities are present. You
must still use two different environments for each stage of the script.



## Usage

Since the required packages are incompatible, the tools now has two distinct 
steps, and must make use of a tracking file to store previously-transferred 
files and relevant metadata. 

### Transfer:
```
python transfer.py -o <track-file> -s <source-dir> -d <dest-dir>
```

The script should only transfer files that have not been transferred correctly
previously. This is useful as transfer of large amounts of data can take longer
than proxy is valid for.

Future improvements:
- Multiprocessing to transfer multiple files at once
- Use local track-file to speed up batch transfer and save checking files
through GFAL (takes significant amount of time when having to check many files)

### Register:
```
python register.py -i <track-file> -l <LFN-path> -e <storage-element>
```

Again, this should (in theory) work for files already registered, but extensive 
testing is still ongoing.

<!---

## Environment setup

When working within a CernVM, the following commands are required:

```
source /cvmfs/ganga.cern.ch/dirac_ui/bashrc 
source /cvmfs/grid.cern.ch/umd-sl6ui-latest/etc/profile.d/setup-ui-example.sh
voms-proxy-init --voms lsst
```

If the script is executed on a client machine that is currently setup and able
to communicate with both NERSC and GridPP, these may not be required.

## Usage

```
python transfer_and_register.py
```

While working I found out that due to the way Dirac python bindings work, it is
not possible to pass variables on the command line. For now, the only way to 
alter how the script runs is to manually edit the values in the `arguments`
class.

The script now accepts command line arguments to alter execution.

The user can pass either a folder or file to the `source` argument, with only
directories being passed to `dest` and `lfnpath` arguments. WARNING: This script
currently ignores subdirectories if giving a source directory.

The user can control how the script behaves with the `transfer` and `register`
boolean flags.

### Transfer-only:

Transfer-only mode requires a `source` and `dest` only. Storage Elements 
(`se`) and `lfnpath`s are not required. 

### Register-only:

Register-only mode requires a `source`, `se`, and `lfnpath`. The `source` 
should point to a GridPP folder/file, that currently exists.

### Combined mode:

If the `transfer` and `register` flags are the same, both stages are executed. 
The output from the `transfer` stage mode becomes the input for the `register`
stage.-->



