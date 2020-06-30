#!/usr/bin/env python3
# 
# -*- coding: utf-8 -*-
# title           : read_alec.py
# description     : [description]
# author          : Adebayo B. Braimah
# e-mail          : adebayo.braimah@cchmc.org
# date            : 2020 01 22 15:33:37
# version         : 0.0.1
# usage           : read_alec.py [-h,--help]
# notes           : [notes]
# python_version  : 3.7.4
#==============================================================================

# Import python modules and packages
import os
import re
import pandas as pd
import argparse

# Define functions
def get_comp_area(acl_file):
    '''
    Reads ALEC alc2 file and returns the MRE composite area value (float)

    Arguments:
        acl_file: ALEC alc2 (ascii-II text) file

    Returns:
        comp_area (float): MRE Composite Area
    '''

    # RegEx to search for
    regexp = re.compile(r' mre.roi.compositeArea = *?([0-9.-]+)')

    # Read file line-by-line, look for (unique) match
    with open(acl_file) as f:
        for line in f:
            match_ = regexp.match(line)
            if match_:
                # print(match_.group(1))
                comp_area = match_.group(1)
                comp_area = float(comp_area)

    return comp_area


def get_comp_stiff(acl_file):
    '''
    Reads ALEC alc2 file and returns the MRE composite stiffness value (float)

    Arguments:
        acl_file: ALEC alc2 (ascii-II text) file

    Returns:
        comp_stiff (float): MRE Composite Stiffnes
    '''

    # RegEx to search for
    regexp = re.compile(r' mre.roi.compositeStiffness = *?([0-9.-]+)')

    # Read file line-by-line, look for (unique) match
    with open(acl_file) as f:
        for line in f:
            match_ = regexp.match(line)
            if match_:
                # print(match_.group(1))
                comp_stiff = match_.group(1)
                comp_stiff = float(comp_stiff)

    return comp_stiff


def file_parts(file):
    '''
    Divides file with file path into: path, filename, extension.
    Function from convert_source: https://github.com/AdebayoBraimah/convert_source

    Arguments:
        file (string): File with absolute filepath

    Returns:
        path (string): Path of input file
        filename (string): Filename of input file, without the extension
        ext (string): Extension of input file
    '''

    [path, file_with_ext] = os.path.split(file)

    # Make condition for gzipped files
    if '.gz' in file_with_ext:
        file_with_ext = file_with_ext[:-3]
        [filename, ext] = os.path.splitext(file_with_ext)
        ext = ext + '.gz'
    else:
        [filename, ext] = os.path.splitext(file_with_ext)

    path = str(path)
    filename = str(filename)
    ext = str(ext)

    return path, filename, ext


def get_sub_id(file):
    '''
    Reads filename and returns subject unique subject identifier.

     Arguments:
        file (string): File with absolute filepath

    Returns:
        sub_id (int): Unique subject identifier
    '''

    [p_name, f_name, ext] = file_parts(file)
    id_parts = f_name.split("_")
    sub_id = id_parts[1]
    sub_id = int(sub_id)

    return sub_id


def make_spread(sub_id, mre_area, mre_stiff, out_file):
    '''
    Creates CSV spreadsheet for automated MRE exams. If the spreadsheet does not exist at runtime, it is created.
    If the spreadsheet does  exist, then it is appended to.

    Arguments:
        sub_id (int): Unique subject identifier
        mre_area (float): MRE Composite Area
        mre_stiff (float): MRE Composite Stiffnes
        out_file: Output file to be written or appended to

    Returns:
        out_file: Appended output file
    '''

    # Create MRE dictionary
    mre_dict = {"Subject_Identifier": [sub_id],
                "MRE_Composite_Area": [mre_area],
                "MRE_Composite_Stiffness": [mre_stiff]}

    # Create data frame from MRE dictionary
    df = pd.DataFrame.from_dict(mre_dict, orient='columns')

    # Write to file
    if os.path.exists(out_file):
        df.to_csv(out_file, sep=",", header=False, index=False, mode='a')
    else:
        df.to_csv(out_file, sep=",", header=True, index=False, mode='w')

    return out_file

if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(description='Reads ALEC Processed MRE Exam files and writes the subject ID, area, and stiffness values to a CSV spreadsheet.')

    # Parse Arguments
    # Required Arguments
    reqoptions = parser.add_argument_group('Required arguments')
    reqoptions.add_argument('-i', '-in', '--input',
                            type=str,
                            dest="alc2",
                            metavar="ALEC_MRE_file.alc2",
                            required=True,
                            help="Automated ALEC MRE alc2 file.")
    reqoptions.add_argument('-o', '-out', '--output',
                            type=str,
                            dest="csv_file",
                            metavar="All_MRE_Exams.csv",
                            required=True,
                            help="Output spreadsheet name.")

    # Optional Arguments
    optoptions = parser.add_argument_group('Optional arguments')
    optoptions.add_argument('-v', '-verbose', '--verbose',
                            dest="verbose",
                            required=False,
                            default=False,
                            action="store_true",
                            help="Prints completion information to screen.")

    args = parser.parse_args()

    # Print help message in the case
    # of no arguments
    try:
        args = parser.parse_args()
    except SystemExit as err:
        if err.code == 2:
            parser.print_help()

    # Verbose flag
    if args.verbose:
        args.verbose = True

    # Parse file
    mre_area = get_comp_area(acl_file=args.alc2)
    mre_stiff = get_comp_stiff(acl_file=args.alc2)
    sub_id = get_sub_id(file=args.alc2)

    args.csv_file = make_spread(sub_id=sub_id, mre_area=mre_area, mre_stiff=mre_stiff, out_file=args.csv_file)

    if args.verbose:
        print(f"Completed parsing MRE exam for {args.alc2}")