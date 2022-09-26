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
  * 3.1. Step 1: Get a bearer token 
  * 3.2. Step 2: Order of the packaging into Raster or Vector 
  * 3.3 Step 3: Checking the status of the Order 
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

➔ auth (Authentication related operations)

**POST**: /auth/get_bearer_token

- Click – “Try it out” button. When clicking this button, the black window box turns white (Figure 1) allowing the insertion of credentials. 
- Insert the requested credentials in the payload white box (Figure 2). 
- Once inserted, click on the “Execute” button (Figure 2).

It will look similar to the following curl example:

After running “Execute”, a successful response (200) returns a valid token, which will be valid at the moment
for 100 days. After its implementation in the CLMS portal, this value will be adjusted to a value compatible
to security guidelines. The access token needs to be then copied for the next step.

#### 3.2 Step 2: Order of the packaging into Raster or Vector
#### 3.3 Step 3: Checking the status of the Order

### Step 4: Downloading the Product

TODO

### 5. Example Visualization within QGIS of the Raster data and the Vector data

TOOD