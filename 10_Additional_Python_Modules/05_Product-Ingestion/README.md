# CLCPlus_Product_Ingestion

This module serves as utility to upload quality checked FINAL CLC+ Backbone products to netCDF files.  
The product netCDF files will be accessed by the get_product API in https://api.clcplusbackbone.geoville.com/v1/.  
  
The code will be run within a docker container. In case the docker image does not exist yet (check with `docker images`), 
go to the directory where the Dockerfile lies and build it with the command `docker build -t backbone_product_ingestion .`. The image is now called **backbone_product_ingestion**.  
To run the code with that image in a docker container, you need to use a docker-run-command similar to the following:  
  
`docker run -u $UID -v /mnt:/mnt backbone_product_ingestion /bin/bash -c "python3 product_netcdf_upload.py -n Raster -u 161 -i /mnt/in/task2/output/161/CLMS_CLCplus_RASTER_2018_010m_PU161_03035_V1_0.tif`
  
Let's explain the command. The '-u $UID' uses the current user (gaf/geoville) within the docker container. This shall avoid file permission errors.   
The flag -v mirrors (mounts) a local directory to the respective docker container directory. 
Here we say that the local directory '/mnt', which contains the mounted s3 buckets (e.g. 'task2') of 'https://s3.waw2-1.cloudferro.com' 
as well as the output netCDF files, gets mirrored with the same path within the docker container.  
Subsequently, we mention the docker image we want to run (backbone_product_ingestion) before  executing the code with `/bin/bash -c "python3 product_netcdf_upload.py"`. 
You can execute `python3 product_netcdf_upload.py --help` in order to get help on the input parameters. You should see the following:  
  
usage: product_netcdf_upload.py [-h] -n  -u  -i  [-o]  
  
This script converts CLC+ Backbone products to netCDF files.  
  
optional arguments:  
  -h, --help      show this help message and exit  
  -n , --Name     Product Name  
  -u , --Unit     Unit for netCDF grouping (can be PU or SPU, but uniform  
                  across product)  
  -i , --Input    Path to the input raster (GeoTiff), input vector  
                  (Geopackage) or input vector attribute (csv)  
  -o , --Output   Not required, only for debugging! Path to the output netcdf  
                  file.  
   
In our example run, we want to insert the **Raster** product (-n) for the unit **161** (-u). The respective input path is given to the flag -i.  
  
Responsible for this repository and the task is Johannes Schmid (GeoVille).  
Backup for the raster products is Andre Stumpf (GAF) and for the vector product is Mirjam Ziselsberger (GeoVille).  


