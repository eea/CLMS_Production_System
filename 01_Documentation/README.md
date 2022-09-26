## Documentation

---

## Contributors
* Johannes Schmid
* Samuel Carraro
* Michek Schwandner

## BACKBONE SYSTEM  - MANUAL API

- Issue: 1.1
- Date: 23/05/2022
- Compiled by:GEOVILLE & GAF AG

### Document Description

| Settings | Value |
|--|--|
|Document Title| Backbone System Manual: API |
|Project Title| Copernicus Land Monitoring Service – CLC+ Backbone Production, including Raster and Vector Products based on Satellite Input Data from 2017/2018/2019|
|Document Author(s)| GAF AG and GeoVille |
|Project Owner| Hans Dufourmont (EEA) |
|Project Manager| Tobias Langanke (EEA)|
|Doc. Issue/Version| 1.1 |
|Date| 23/05/2022 |
|Distribution List| Consortium and EEA |
|Confidentiality| - |

### Document Release Sheet 

| Name | Role | Date |
|--|--|--|
|Johannes Schmid (GeoVille)|Creation| 19/11/2021
|Tanja Gasber (GeoVille)|Creation| 19/11/2021
|Inés Ruiz  (GAF)|Revision|-|
|Tobias Langanke (EEA) (GAF)|Approval|-|

### Document History & Change Record

| Issue / Version | Release Date | Created by | Description of Issue / Change(s)|
|--|--|--|--|
|1.0|18.12.2021GeoVille / GAF AG |-|
|1.1|-|GAF / GeoVille|Vector products|

### Table of Contents

* 1. Executive Summary
* 2. EEAs Credentials
* 3. Ordering Steps 
  * 1. Step 1: Get a bearer token 
  * 2. Step 2: Order of the packaging into Raster or Vector 
  * 3. Step 3: Checking the status of the Order 
* 4. Step 4: Downloading the Product
* 5. Example Visualization within QGIS of the Raster data and the Vector data


### 1 Executive Summary

This manual is intended to aim as step by step how-to for accessing and using the CLC+ Backbone “get_Product
API”. This API Endpoint will provide access to the products (i.e., Raster or Vector) stored within the WEkEO
CLC+ Backbone Data store (NetCDF with HDF5).

By using this document an implementation of the CLC+ Backbone Product API into the Copernicus Land
Monitoring System can be achieved.

### 2 EEAs Credentials

Please insert your credentials (user_id and client_secret) to create your bearer token to be able to order your
products by following the steps addressed below.

### 3 Ordering Steps

#### 3.1 Step 1: Get a bearer token

Swagger Endpoint for Testing

https://api.clcplusbackbone.geoville.com/v1/

**➔ auth (Authentication related operations)**

**POST**: /auth/get_bearer_token

* Click - “Try it out” button. When clicking this button, the black window box turns white (Figure 1) allowing the insertion of credentials. 
* Insert the requested credentials in the payload white box (Figure 2). 
* Once inserted, click on the “Execute” button (Figure 2).

It will look similar to the following curl example:

After running “Execute”, a successful response (200) returns a valid token, which will be valid at the moment
for 100 days. After its implementation in the CLMS portal, this value will be adjusted to a value compatible
to security guidelines. The access token needs to be then copied for the next step.

#### 3.2 Step 2: Order of the packaging into Raster or Vector

In order to call for a product, three endpoints can be used:

* /products/get_product
* /products/get_national_product
* /products/get_product_europe

While requesting products with „get_product“ requires an Area of Interest (AoI), the „get_national_product“
endpoint requires the name of the desired country. The endpoint „get_product_europe“ does not need any
spatial information, because it returns the product for entire Europe.

In contrast to the other requests, „get_national_product“ does not return data in the projection LAEA (EPSG:
3035) but in the respective national projection.

While requesting the Raster product returns one GeoTiff regardless of the endpoint, the Vector product will
be provided by a list of GeoPackages due to the data size and the performance of Geographical Information
Systems.
**
In the following example, a product will be requested by providing an AoI. The example will be executed on
Swagger, the API documentation. The execution of the remaining two endpoints only differ in regard to the
request payload.

**➔ Products (Order final products)**

**POST** /products/get_products

* Click the “Try it out” button. When clicking it, the black window box turns white, allowing the insertion of credentials. (Figure 5).
* While being enabled, insert the access token into the Authorization box. Please note that it has to be written as: “Bearer” Access_token
* First, select the product type:
  * Raster
  * Vector
* Second, provide the AoI as Well-known text (WKT) in WGS84 (EPSG: 4326).
* Finally, add the user_id

After doing so, click on the “Execute” button. The system will prepare the product in the backend by cutting
the data cubes and converting it into an OGC conformal GeoTIFF for the Raster and GeoPackage for the
Vector Product. The output prjection is LAEA (EPSG: 3035).

The respective curl command would look as follows (Figure 6). 

After the product was successfully ordered, the system schedules the extraction and starts to process the
data.

The order status can be retrieved by using the “/services/order_status” endpoint. This endpoint requires
the order ID which was received from the former POST request (see the red box in Figure 7).

#### 3.3 Step 3: Checking the status of the Order

**➔ Services (Service related operations)**

**GET** /services/order_status/{order_id}

With the endpoint services/order_status/{order_id} the status of the order can be checked. The possible
states are:

* FAILED: An unexpected error occurred during the execution of the service
* SUCCESS: Service was successful - > RESULT String will deliver the download link
* QUEUED: Submitted request is in the waiting list
* RECEIVED: API received the service request and created an order ID
* RUNNING: Service is being calculated at the moment
* INVALID: It indicates that there is wrong input provided

Note: The cutting of the data takes some time to be donw, depending on the size of the provided geometry.
Average runtimes for ~10.000 km2 are within minutes (Raster being the faster delivered products,
compared to Vector ones).

* Click the “Try it out” button. 
* Insert the access token from Step 2 into the Authorization box. (i.e. Bearer zZYqplU66dFTb9BZRg1ekyWhrWwBxpbJqdnZfPNU1S)
* Provide the order_id from step 2.
* After doing so, click on the “Execute” button. In case the Order is successful the Response will carry the result paths to the S3 object-store at WEkEO.

A Curl example for a status check of an order with the order_id d371e64324033b2d8cd0a35a9d693975
would look as in the figure below.

In case the order is successful the response will carry a link that allows the user to download the result from
the S3 object-store at WEkEO.

### Step 4: Downloading the Product

To download the product to the customer from the S3 storage. For this procedure, @WEkEO standard S3
mechanisms can be implemented. Note that the Filename is of your response.

**Here the example with boto3 and Python:**

* The access_key_id = “bc8e686837c2476ba4dcef06ba7272ca
* The secret_access_key = “2e7516dc941f4bdcae1204d51c354bee”

➔ Please copy the product id from Step 4 into the red box and add a path and filename where you want to save your data.

The data itself will contain the following files:


### 5. Example Visualization within QGIS of the Raster data and the Vector data

* tfw - Images are stored as raster data wherein each cell in the image has a row and column number. Vector data, such as feature classes in geodatabases, shapefiles, and coverages, is stored in real-world coordinates. To display images with this vector data, it is necessary to establish an image-to-world transformation that converts the image coordinates to real-world coordinates. This transformation information is typically stored with the image.
* .tif – dataset itself
* .xml - standard XML Files and widely adopted by many systems to store and read metadata that might or might not be in the header of the file
* aux.xml - the histogram information for the image - which is often only a .aux file rather than having .xml on the end of that.
* .tif.vat.cpg - a code page file, which gives the character encoding for whatever it refers to. In this case that dbf file. Note that .vat is a value attribute table aka raster attribute table
* .tif.ovr - the pyramid file, basically some lower resolution duplicates of the image to speed up redraw when zoomed out
* .tif.clr - The Colormap function is a type of raster data renderer. It transforms the pixel values to display the raster data as either a grayscale or a color (RGB) image based on specific colors in a color map file, or based on a color ramp. You can use a color map to represent analyzed data, such as a classified image, or when displaying a topographic map (or index color-scanned image). When the Colormap function is used, ArcGIS will display the mosaic dataset using the color map renderer or with a specified
color ramp.
* .qml - A file with .qml extension is a XML file that stores layer styling information for QGIS layers. QGIS is an open-source cross-platform GIS application used to display geospatial data with the capability of organizing data in the form of layers. QML files contain information that is used by the QGIS to render feature geometries including  symbol definitions, sizes and rotations, labelling, opacity, blend mode, and much more. Unlike the QLR files, QML files contains all the styling information in itself.
* txt – same information as the .clr and .qml but also explaining the classes by names