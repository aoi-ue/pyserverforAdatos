"""
Python Version  : 3.6.6
Script Created  : 4 Sep 2018
Author          : Hafiz Magnus
Description     : Script for the Generation of the Agricultural Indices
                  from Sentinel 2 Data
Libraries       : ast, fiona, gdal2tiles, geopandas, jenkspy, numpy, osgeo,
                  os, pathlib, rasterio, shutil, skimage, subprocess, sys
"""


# importing the necessary modules
from __future__ import absolute_import
import ast
import fiona
import gdal2tiles
import jenkspy
import geopandas
import numpy as np
import os
from osgeo import gdal, gdal_array, gdalconst, gdalnumeric, ogr, osr
from pathlib import Path
import rasterio
import rasterio.features
from rasterio.mask import mask
import rasterio.warp
from rasterio.warp import calculate_default_transform, reproject, Resampling
import shutil
import skimage
import subprocess
import sys
# ---------------------


# consolidating the sen2corr outputs into a single folder
def raster_consolidate(raster_folder):
    """
    Helper function that consolidates the key outputs from the sen2corr
    algorithm into a single folder
    raster_folder       ->      The output folder from the sen2corr algorithm
    """
    bands = ['_B02_10m.jp2',
             '_B03_10m.jp2',
             '_B04_10m.jp2',
             '_B05_20m.jp2',
             '_B06_20m.jp2',
             '_B07_20m.jp2',
             '_B08_10m.jp2',
             '_B8A_20m.jp2',
             '_B11_20m.jp2',
             '_B12_20m.jp2']

    img_folder = os.path.join(raster_folder, "CONSOLIDATED")
    os.mkdir(img_folder)

    for root, dirs, files in os.walk(raster_folder):
        for afile in files:
            for band in bands:
                if afile.endswith(band):
                    ori = os.path.join(root, afile)
                    mvd = os.path.join(img_folder, afile)
                    os.rename(ori, mvd)

    return img_folder


# get the list of rasters which needs to be resampled up
def raster_sorter(raster_folder):
    """
    Helper function for raster resampling
    raster_folder       ->      A folder where the raw sentinel 2
                                images are located
    """
    for aroot, adirs, afiles in os.walk(raster_folder):
        fine_resolution = 1000.0
        best_rasters = []
        course_rasters = []
        raster_dict = {}
        sm_file = sys.maxsize

        for afile in afiles:
            raster = os.path.join(aroot, afile)
            sz = os.path.getsize(raster)
            src = rasterio.open(raster)
            resolution = float(src.res[0])
            raster_dict[raster] = (resolution, sz)
            if fine_resolution > resolution:
                fine_resolution = resolution
            src = None

        for key, values in raster_dict.items():
            if fine_resolution == values[0]:
                if sm_file > values[1]:
                    sm_file = values[1]

        for ikey, ivalues in raster_dict.items():
            if fine_resolution == ivalues[0]:
                if sm_file == ivalues[1]:
                    best_rasters.append(ikey)
            else:
                course_rasters.append(ikey)

        return course_rasters, best_rasters[0]


# resampling rasters
def raster_resampling(raster_folder):
    """
    Increasing the resolution of low resolution rasters.
    This function will replace the low resolution rasters
    in the original folder.
    """
    img_folder = raster_consolidate(raster_folder)
    inputs = raster_sorter(img_folder)
    raster_list = inputs[0]
    match_filename = inputs[1]

    if len(raster_list) > 0:
        for raster in raster_list:
            r_name = os.path.basename(raster)
            dst_filename = str(Path.cwd() / "temp" / r_name)

            # source
            src = gdal.Open(raster, gdalconst.GA_ReadOnly)
            src_proj = src.GetProjection()
            src_geotrans = src.GetGeoTransform()

            # to match
            match_ds = gdal.Open(match_filename, gdalconst.GA_ReadOnly)
            match_proj = match_ds.GetProjection()
            match_geotrans = match_ds.GetGeoTransform()
            wide = match_ds.RasterXSize
            high = match_ds.RasterYSize

            # destination
            dst = gdal.GetDriverByName('GTiff').Create(
                dst_filename, wide, high, 1, gdalconst.GDT_UInt16)
            dst.SetGeoTransform(match_geotrans)
            dst.SetProjection(match_proj)

            # resample the raster
            gdal.ReprojectImage(
                src,
                dst,
                src_proj,
                match_proj,
                gdalconst.GRA_Lanczos)

            # closing opened files
            src = None
            dst = None
            match_ds = None

            # replace original file with resampled
            os.remove(raster)
            shutil.copy2(dst_filename, raster)
            os.remove(dst_filename)
    return


# reproject vector file
def reproj_vector(in_crs, out_crs, vector):
    """
    Function to reproject the vector
    in_crs      ->      the in CRS
    out_crs     ->      the CRS to projet to
    vector      ->      the vector file
    """
    in_vector = geopandas.read_file(vector)
    df = in_vector.to_crs({'init': u'epsg:{}'.format(out_crs)})
    proj_df = ast.literal_eval(df.to_json())
    return proj_df


# check if estate AOI and input rasters are in the same projection
def proj_check(in_raster, aoi):
    r_crs = int(rasterio.open(in_raster).crs['init'].split(":")[-1])
    v_crs = int(fiona.open(aoi, 'r').meta['crs']['init'].split(":")[-1])
    if r_crs != v_crs:
        aoi_proj = reproj_vector(v_crs, r_crs, aoi)
        geo_features = [feature["geometry"]
                        for feature in aoi_proj['features']]
    else:
        cutter = fiona.open(aoi, 'r')
        geo_features = [feature["geometry"] for feature in cutter]
    return geo_features


# clip inputs to estate AOI
def raster_mask(raster, vector):
    geo_features = proj_check(raster, vector)
    with rasterio.open(raster) as src:
        out_img, out_transform = rasterio.mask.mask(src,
                                                    geo_features, crop=True,
                                                    all_touched=True)
        out_img = (out_img.astype(float)) / 10000
        out_meta = src.meta.copy()
        return out_img, out_transform, out_meta


# convert processed numpy array to raster
def imager(img, out_transform, out_meta, f_image):
    out_meta.update({'driver': 'GTiff',
                     'height': img.shape[1],
                     'width': img.shape[2],
                     'transform': out_transform,
                     'dtype': 'float64'})
    with rasterio.open(f_image, "w", **out_meta) as dest:
        dest.write(img)
    return


# render raster with a color ramp
def renderer(in_raster, out_raster, ramp):
    cmd = 'gdaldem color-relief {} {} {}'.format(in_raster, ramp, out_raster)
    subprocess.call(cmd)
    return out_raster


# create raster tiles
def tiler(in_raster, out_raster, ramp, folder):
    options = {'zoom': (8, 18), 'resampling': 'near', 'webviewer': 'none'}
    rend = renderer(in_raster, out_raster, ramp)
    gdal2tiles.generate_tiles(rend, folder, **options)
    return


# standardising array to 0 to 100
def std_array(in_array, d_min=None, d_max=None, f_min=0, f_max=100):
    if d_min is None:
        d_min = np.min(in_array)
    if d_max is None:
        d_max = np.amax(in_array)

    def scaler(x): return (((x - d_min)
                            / (d_max - d_min))
                           * (f_max - f_min)
                           + f_min)
    vfunc = np.vectorize(scaler)
    out_array = vfunc(in_array)
    return out_array


# function to create the raster tiles
def raster_executor(
        p_image,
        in_array,
        out_transform,
        out_meta,
        i_ramp,
        tile_folder,
        i_folder):
    """
    p_image         -> the name of the temporary output image
    in_array        -> the raw index created
    out_transform   -> second output from the raster_mask function
    out_meta        -> third output from the raster_mask function
    ramp            -> the color ramp to be used when rendering the index
    tile_folder     -> the base tile folder path
    i_folder        -> where all the tiles will be created in the tile_folder

    Returns the path to the created image
    """
    # write the created index into a temporary file
    f_image = str(Path.cwd() / "temp" / p_image)
    imager(in_array, out_transform, out_meta, f_image)

    # generating the inputs for the color ramps
    ramp = str(Path.cwd() / "ramps" / i_ramp)
    temp_raster = str(Path.cwd() / "temp" / "rendered_temp_image.tif")

    # tiling the raw raster
    folder = os.path.join(tile_folder, i_folder)
    if not os.path.exists(folder):
        os.mkdir(folder)
    tiler(f_image, temp_raster, ramp, folder)

    # delete unnecessary temporary file
    os.remove(temp_raster)

    return f_image


# natural breaks classification for visual display
def natural_breaks(input_array):
    copy_array = np.copy(input_array)
    copy_array = copy_array[~np.isnan(copy_array)]

    rdm_array = np.random.choice(copy_array, size=100000)
    rdm_list = rdm_array.tolist()
    breaks = jenkspy.jenks_breaks(rdm_list, nb_class=101)

    del copy_array
    del rdm_array

    return breaks


# function to calculate weighted Normalised Difference Water Index.
# this index measures water stress in plants.
def wndwi_f(nir_band, swir11_band, aoi, tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    swir11 = raster_mask(swir11_band, aoi)[0]
    wndwi = ((2 * nir - swir11)
             / (2 * nir + swir11))

    # creating the standard array
    wndwi_std = std_array(in_array=wndwi, d_min=-1.0, d_max=1.0)

    # categorising the wNDWI array for visualisation
    classes = natural_breaks(wndwi)
    wndwi[(wndwi <= classes[30])] = 1.1
    wndwi[(wndwi <= classes[50])] = 2
    wndwi[(wndwi <= classes[60])] = 3
    wndwi[(wndwi <= classes[75])] = 4
    wndwi[(wndwi >= classes[75]) & (wndwi <= 1.0)] = 5
    wndwi[(wndwi == 1.1)] = 1

    # rendering and tiling the raw index
    wndwi_img = raster_executor("raw_wndwi.tif",
                                wndwi, out_transform,
                                out_meta, "wndwi_color.txt",
                                tile_folder, "wNDWI")

    return wndwi_img, wndwi_std, out_transform, out_meta


# function to calculate Wide Dynamic Range Vegetation Index.
# this index measures plant biomass.
def wdrvi_f(nir_band, red_band, aoi, tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    red = raster_mask(red_band, aoi)[0]
    wdrvi = (0.2 * nir - red) / (0.2 * nir + red)

    # creating the standard array
    wdrvi_std = std_array(in_array=wdrvi, d_min=-1.0, d_max=1.0)

    # categorising the WDRVI array for visualisation
    classes = natural_breaks(wndwi)
    wdrvi[(wdrvi <= classes[30])] = 1.1
    wdrvi[(wdrvi <= classes[50])] = 2
    wdrvi[(wdrvi <= classes[60])] = 3
    wdrvi[(wdrvi <= classes[75])] = 4
    wdrvi[(wdrvi >= classes[75]) & (wdrvi <= 1.0)] = 5
    wdrvi[(wdrvi == 1.1)] = 1

    # rendering and tiling the raw index
    wdrvi_img = raster_executor("raw_wdrvi.tif",
                                wdrvi, out_transform,
                                out_meta, "wdrvi_color.txt",
                                tile_folder, "WDRVI")

    return wdrvi_img, wdrvi_std, out_transform, out_meta


# function to calculate Enhanced Vegetation Index
# this index measures late stage LAI
def evi_f(nir_band, red_band, blue_band, aoi, tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    red = raster_mask(red_band, aoi)[0]
    blue = raster_mask(blue_band, aoi)[0]
    evi = ((2.5 * (nir - red))
           / (nir + (6 * red)
              - (7.5 * blue) + 1.0))

    # creating the standard array
    evi_std = std_array(in_array=evi, d_min=-1.0, d_max=1.0)

    # categorising the EVI array for visualisation
    classes = natural_breaks(evi)
    evi[(evi <= classes[30])] = 1.1
    evi[(evi <= classes[50])] = 2
    evi[(evi <= classes[60])] = 3
    evi[(evi <= classes[75])] = 4
    evi[(evi >= classes[75]) & (evi <= 1.0)] = 5
    evi[(evi == 1.1)] = 1

    # rendering and tiling the raw index
    evi_img = raster_executor("raw_evi.tif",
                              evi, out_transform,
                              out_meta, "evi_color.txt",
                              tile_folder, "EVI")

    return evi_img, evi_std, out_transform, out_meta


# function to calculate Normaliased Differentiated Vegetation Index
# this index measures the amount of Photosythetically Active Radiation
def ndvi_f(nir_band, red_band, aoi, tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    red = raster_mask(red_band, aoi)[0]
    ndvi = ((nir - red) / (nir + red))

    # creating the standard array
    ndvi_std = std_array(in_array=ndvi, d_min=-1.0, d_max=1.0)

    # categorising the NDVI array for visualisation
    classes = natural_breaks(ndvi)
    ndvi[(ndvi <= classes[30])] = 1.1
    ndvi[(ndvi <= classes[50])] = 2
    ndvi[(ndvi <= classes[60])] = 3
    ndvi[(ndvi <= classes[75])] = 4
    ndvi[(ndvi >= classes[75]) & (ndvi <= 1.0)] = 5
    ndvi[(ndvi == 1.1)] = 1

    # rendering and tiling the raw index
    ndvi_img = raster_executor("raw_ndvi.tif",
                               ndvi, out_transform,
                               out_meta, "ndvi_color.txt",
                               tile_folder, "NDVI")

    return ndvi_img, ndvi_std, out_transform, out_meta


# function to calculate Optimised Soil Adjusted Vegetation Index
# this index measures early stage LAI
def osavi_f(nir_band, red_band, aoi, tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    red = raster_mask(red_band, aoi)[0]
    osavi = (nir - red) / (nir + red + 0.16)

    # creating the standard array
    osavi_std = std_array(in_array=osavi, d_min=-1.0, d_max=1.0)

    # categorising the OSAVI array for visualisation
    classes = natural_breaks(osavi)
    osavi[(osavi <= classes[30])] = 1.1
    osavi[(osavi <= classes[50])] = 2
    osavi[(osavi <= classes[60])] = 3
    osavi[(osavi <= classes[75])] = 4
    osavi[(osavi >= classes[75]) & (osavi <= 1.0)] = 5
    osavi[(osavi == 1.1)] = 1

    # rendering and tiling the raw index
    osavi_img = raster_executor("raw_osavi.tif",
                                osavi, out_transform,
                                out_meta, "osavi_color.txt",
                                tile_folder, "OSAVI")

    return osavi_img, osavi_std, out_transform, out_meta


# function to calculate Plant Senescence Reflectance Index
# this index measures the level of senescence in the plants
def psri_f(red_band, blue_band, re6_band, aoi, tile_folder):
    red, out_transform, out_meta = raster_mask(red_band, aoi)
    blue = raster_mask(blue_band, aoi)[0]
    re6 = raster_mask(re6_band, aoi)[0]
    psri = (red - blue) / re6

    # creating the standard array
    psri_std = std_array(in_array=psri, d_min=-1.0, d_max=1.0)

    # categorising the PSRI array for visualisation
    classes = natural_breaks(psri)
    psri[(psri <= classes[30])] = 1.1
    psri[(psri <= classes[50])] = 2
    psri[(psri <= classes[60])] = 3
    psri[(psri <= classes[75])] = 4
    psri[(psri >= classes[75]) & (psri <= 1.0)] = 5
    psri[(psri == 1.1)] = 1

    # rendering and tiling the raw index
    psri_img = raster_executor("raw_psri.tif",
                               psri, out_transform,
                               out_meta, "psri_color.txt",
                               tile_folder, "PSRI")

    return psri_img, psri_std, out_transform, out_meta


# function to calculate Inverted Red-Edge Chlorophyll Index
# this index is a measure of leaf chlorophyll concentration
def ireci_f(nir_band, red_band, re5_band, re6_band, aoi, tile_folder):
    red, out_transform, out_meta = raster_mask(red_band, aoi)
    nir = raster_mask(nir_band, aoi)[0]
    re5 = raster_mask(re5_band, aoi)[0]
    re6 = raster_mask(re6_band, aoi)[0]
    ireci = ((nir - red) / (re5 / re6))

    # creating the standard array
    ireci_std = std_array(in_array=ireci, d_min=-1.0, d_max=2.5)

    # categorising the IRECI array for visualisation
    classes = natural_breaks(ireci)
    ireci[(ireci <= classes[30])] = 1.1
    ireci[(ireci <= classes[50])] = 2
    ireci[(ireci <= classes[60])] = 3
    ireci[(ireci <= classes[75])] = 4
    ireci[(ireci >= classes[75]) & (ireci <= 1.0)] = 5
    ireci[(ireci == 1.1)] = 1

    # rendering and tiling the raw index
    ireci_img = raster_executor("raw_ireci.tif",
                                ireci, out_transform,
                                out_meta, "ireci_color.txt",
                                tile_folder, "IRECI")

    return ireci_img, ireci_std, out_transform, out_meta


# function to calculate Forest Canopy Density
def fcd_f(
        nir_band,
        red_band,
        green_band,
        blue_band,
        swir11_band,
        aoi,
        tile_folder):
    nir, out_transform, out_meta = raster_mask(nir_band, aoi)
    red = raster_mask(red_band, aoi)[0]
    green = raster_mask(green_band, aoi)[0]
    blue = raster_mask(blue_band, aoi)[0]
    red = raster_mask(red_band, aoi)[0]
    swir11 = raster_mask(swir11_band, aoi)[0]

    # calculate the Advance Vegetation Index
    avi = ((nir * (1.0 - red) * (nir - red)) ** (1.0 / 3.0))
    avi_std = std_array(in_array=avi, d_min=-1.0, d_max=1.0)

    # calculate the Bare Soil Index
    bsi = ((swir11 + red) - (nir + blue)) / ((swir11 + red) + (nir + blue))
    bsi_std = std_array(in_array=bsi, d_min=-1.0, d_max=1.0)

    # calculate the Shadow Index
    si = ((1.0 - blue) * (1.0 - green) * (1.0 - red)) ** (1.0 / 3.0)
    si_std = std_array(in_array=si, d_min=0.0, d_max=1.0)

    # calculate forest canopy density
    fcd = (avi_std / (si_std * bsi_std))
    fcd_std = std_array(in_array=fcd)

    # categorising the fcd array for visualisation
    classes = natural_breaks(fcd)
    fcd[(fcd <= classes[30])] = 1.1
    fcd[(fcd <= classes[50])] = 2
    fcd[(fcd <= classes[60])] = 3
    fcd[(fcd <= classes[75])] = 4
    fcd[(fcd >= classes[75]) & (fcd <= 1.0)] = 5
    fcd[(fcd == 1.1)] = 1

    # rendering and tiling the raw index
    ireci_img = raster_executor("raw_fcd.tif",
                                fcd, out_transform,
                                out_meta, "fcd_color.txt",
                                tile_folder, "FCD")

    return fcd_std

# generate basemap tiles
def rgb_tiles(tci_img, tile_root_folder, aoi):
    temp_img = os.path.join(tile_root_folder, os.path.basename(tci_img))
    p_aoi = proj_check(tci_img, aoi)
    with rasterio.open(tci_img) as src:
        out_image, out_transform = rasterio.mask.mask(
            src, p_aoi, crop=True, all_touched=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
    with rasterio.open(temp_img, "w", **out_meta) as dest:
        dest.write(out_image)
    options = {'zoom': (8, 18), 'resampling': 'near', 'webviewer': 'none'}
    basemap_folder = os.path.join(tile_root_folder, "BASEMAP")
    if not os.path.exists(basemap_folder):
        os.makedirs(basemap_folder)
    gdal2tiles.generate_tiles(temp_img, basemap_folder, **options)
    os.remove(temp_img)
    return


# function to calculate yield propensity score
def yield_f(
        nir_band,
        red_band,
        green_band,
        blue_band,
        re5_band,
        re6_band,
        swir11_band,
        aoi,
        tile_folder):

    # calculating the inputs for the Yield Propensity Score
    out_transform = wndwi_f(nir_band, swir11_band, aoi, tile_folder)[2]
    out_meta = wndwi_f(nir_band, swir11_band, aoi, tile_folder)[3]
    wndwi = wndwi_f(nir_band, swir11_band, aoi, tile_folder)[1]
    wdrvi = wdrvi_f(nir_band, red_band, aoi, tile_folder)[1]
    evi = evi_f(nir_band, red_band, blue_band, aoi, tile_folder)[1]
    ndvi = ndvi_f(nir_band, red_band, aoi, tile_folder)[1]
    osavi = osavi_f(nir_band, red_band, aoi, tile_folder)[1]
    psri = psri_f(red_band, blue_band, re6_band, aoi, tile_folder)[1]
    ireci = ireci_f(nir_band, red_band, re5_band, re6_band, aoi, tile_folder)[1]
    fcd = fcd_f(nir_band, red_band, green_band, blue_band, swir11_band, aoi, tile_folder)[1]
    
    # calculating the yield propensity
    yield_prop = wndwi + wdrvi + ((0.5 * evi) + (0.5 * osavi)) + ndvi + (ireci / psri) + fcd
    std_yield = std_array(in_array=yield_prop)

    raster_executor(
        "raw_yield.tif",
        std_yield,
        out_transform,
        out_meta,
        "yield_color.txt",
        tile_folder,
        "YIELD")

    return


# ---------------------

# ignore errors related to dividing null raster regions
np.seterr(divide='ignore', invalid='ignore')
