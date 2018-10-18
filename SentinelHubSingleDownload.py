# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 14:40:39 2018

@author: Josie
"""

from sentinelhub import AwsProductRequest, AwsTile, DataSource, AwsTileRequest

downloadloc = r'D:/yuhanyuhan/pythonserver'
s2tile = '49MDV'
s2tiledate ='2018-6-06'

def downloadS2asSAFE(downloadfolder, tilename,tiledate):
    tileindex = 0
    productid = AwsTile(tile_name=tilename, time=tiledate, aws_index=tileindex, data_source=DataSource.SENTINEL2_L1C).get_product_id()
    print('Downloading following product to SAFE format: ', productid)

    product_request = AwsProductRequest(product_id=productid, data_folder=downloadfolder, safe_format=True)
    product_request.save_data()
    
downloadS2asSAFE(downloadloc, s2tile, s2tiledate)