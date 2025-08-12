#!/usr/bin/env python


import xarray as xr
import os
import re
 
input_dir = "STELLAR-Phase4A-Paleotopography-Merged-PMAG" #"paleomap_present-day-coords_interp"
output_dir = "CrustalThickness_P4a_airy_PMAG"
os.makedirs(output_dir, exist_ok=True)
print("Input dir:", input_dir)
print("Output dir:", output_dir)

# Constants
RHO_M = 3300  # kg/m³
RHO_C = 2700  # kg/m³
H0 = 35000    # Reference crustal thickness in meters

def convert_elevation_to_thickness(elevation):
    """Convert elevation (m) to crustal thickness (m) using Airy isostasy."""
    return H0 + (elevation * RHO_M) / (RHO_M - RHO_C)

def process_netcdf_file(filename):
    """Load NetCDF, convert elevation to crustal thickness, and save new NetCDF."""
    ds = xr.open_dataset(filename)
    
    elevation = ds["z"] #["ElevationDL"]

    # Compute crustal thickness
    crust_thickness = convert_elevation_to_thickness(elevation)

    # Create new DataSet
    thickness_ds = xr.Dataset(
        {"z": (elevation.dims, crust_thickness.data)},
        coords=elevation.coords,
        attrs={"description": "Crustal thickness derived from paleoelevation using Airy isostasy"}
    )

    # Add metadata
    thickness_ds["z"].attrs = {
        "units": "m",
        "long_name": "Crustal Thickness"
    }

    # Output filename
    age = re.search(r"(\d+)Ma", filename).group(1)
    out_filename = os.path.join(output_dir, f"crustal_thickness_{age}Ma.nc")
    
    encoding = {
        "z": {
            "zlib": True,
            "complevel": 1,
            "shuffle": True
        }
    }
    
    thickness_ds.to_netcdf(out_filename, encoding=encoding)
    print(f"Saved: {out_filename}")

# Batch process all files
for file in os.listdir(input_dir):
    if file.startswith("paleotopography_spliced_") and file.endswith(".nc"):
        process_netcdf_file(os.path.join(input_dir, file))
