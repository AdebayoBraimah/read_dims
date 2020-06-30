#!/usr/bin/env python 

# Import modules
import nibabel as nib
import pandas as pd
import os

# Import modules for argument parsing
import argparse

# Define functions
def get_img_dims(nii_file):
    '''
    Ascertains image dimensions from input nifti image header.
    
    Arguments:
        nii_file (nifti file): NifTi image filename with absolute filepath
        
    Returns: 
        x (float): X dimension length (in mm).
        y (float): Y dimension length (in mm).
        z (float): Z dimension length (in mm).
    '''
    
    # Load image
    img = nib.load(nii_file)
    
    # Store image dimensions
    x = float(img.header['pixdim'][1])
    y = float(img.header['pixdim'][2])
    z = float(img.header['pixdim'][3])
    
    return x,y,z

def determine_orientation(nii_file,num_dec=1):
    '''
    Determines image acquisition direction from input nifti image.
    
    Arguments:
        nii_file (nifti file): NifTi image filename with absolute filepath.
        num_dec (int): Number of decimal places to round each voxel dimension to.
        
    Returns: 
        orientation (string): Output string that describes image acquisition direction
        x (float): X dimension length (in mm).
        y (float): Y dimension length (in mm).
        z (float): Z dimension length (in mm).
    '''
    
    # Determine image dimensions
    [x,y,z] = get_img_dims(nii_file=nii_file)
    
    # Round values to managable numbers
    x = round(x,num_dec)
    y = round(y,num_dec)
    z = round(z,num_dec)
    
    # Ascertain image acquisition direction
    if x == y == z:
        orientation = "isotropic"
    elif x == y:
        orientation = "axial"
    elif x == z:
        orientation = "coronal"
    elif y == z:
        orientation = "sagittal"
    else:
        orientation = "inconsistent voxel sizes - review manually"
        
    return orientation,x,y,z

def write_spread(nii_file,out_file,num_dec=1,full_path=False):
    '''
    Writes image filename, dimensions, and acquisition direction to a
    spreadsheet. If the spreadsheet already exists, then it is appended
    to.
    
    Arguments:
        nii_file (nifti file): NifTi image filename with absolute filepath.
        out_file (csv file): Output csv file name and path. This file need not exist at runtime.
        num_dec (int): Number of decimal places to round each voxel dimension to.
        full_path (bool): Whether to write the absolute path (vs the basename) in the spreadsheet.
            This option should be 'True' if all files in the spreadsheet are named similarly.
            Otherwise, should be 'False' if all the files are labeled uniquely (i.e. BIDS data).
        
    Returns: 
        out_file (csv file): Output csv file name and path.
    '''
    
    # Strip csv file extension from output file name
    if '.csv' in out_file:
        out_file = os.path.splitext(out_file)[0]
        out_file = out_file + '.csv'
    elif '.tsv' in out_file:
        out_file = os.path.splitext(out_file)[0]
        out_file = out_file + '.csv'
    elif '.txt' in out_file:
        out_file = os.path.splitext(out_file)[0]
        out_file = out_file + '.csv'
    else:
        pass
    
    # Determine image orientation
    [orientation,x,y,z] = determine_orientation(nii_file=nii_file,num_dec=num_dec)
    
    # Construct image data dictionary
    if full_path:
        file = os.path.abspath(nii_file)
    else:
        file = os.path.basename(nii_file)
    
    img_dict = {"Filename":[file],
               "x_vox":[x],
               "y_vox":[y],
               "z_vox":[z],
               "Orientation":[orientation]}
    
    # Create dataframe from image dictionary
    df = pd.DataFrame.from_dict(img_dict,orient='columns')
    
    # Write output CSV file
    if os.path.exists(out_file):
        df.to_csv(out_file, sep=",", header=False, index=False, mode='a')
    else:
        df.to_csv(out_file, sep=",", header=True, index=False, mode='w')
    
    return out_file

if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(description='Reads NifTi image header and writes voxel dimension values and acquisition direction to a CSV spreadsheet.')

    # Parse Arguments
    # Required Arguments
    reqoptions = parser.add_argument_group('Required arguments')
    reqoptions.add_argument('-i', '-in', '--input',
                            type=str,
                            dest="nii",
                            metavar="IMG.nii",
                            required=True,
                            help="Nifti image file.")
    reqoptions.add_argument('-o', '-out', '--output',
                            type=str,
                            dest="csv_file",
                            metavar="OUTPUT.csv",
                            required=True,
                            help="Output spreadsheet name.")

    # Optional Arguments
    optoptions = parser.add_argument_group('Optional arguments')
    optoptions.add_argument('-fp', '--full-path',
                            dest="fp",
                            required=False,
                            default=False,
                            action="store_true",
                            help="Writes full input file path to the spreadsheet instead of the basename.")
    optoptions.add_argument('--num-dec',
                            type=int,
                            dest="dec",
                            metavar="DEC",
                            default=1,
                            required=False,
                            help="Number of decimal places to round voxel dimension values to.")

    args = parser.parse_args()

    # Print help message in the case
    # of no arguments
    try:
        args = parser.parse_args()
    except SystemExit as err:
        if err.code == 2:
            parser.print_help()

    # Parse file
    args.csv_file = write_spread(nii_file=args.nii,out_file=args.csv_file,num_dec=args.dec,full_path=args.fp)
  
