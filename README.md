# NERSC-to-GridPP
Tools to simplify transferring data from NERSC to GridPP storage elements.

## Requires

- DIRAC tools
- GFAL2 (and python bindings)
- Access to relevant systems from local client machine (e.g. via 
voms-proxy-init).

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

~~While working I found out that due to the way Dirac python bindings work, it is
not possible to pass variables on the command line. For now, the only way to 
alter how the script runs is to manually edit the values in the `arguments`
class.~~

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
stage.


