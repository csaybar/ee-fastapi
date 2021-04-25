<h1 align="center">
  <br>
      <img src=https://user-images.githubusercontent.com/16768318/116000659-73986280-a5f1-11eb-90bf-cd87ba525deb.png width=65%>
  <br>
      ee-fastapi: Flood Detection System
  <br>
</h1>


A **ee-fastapi** is a simple [FastAPI](https://fastapi.tiangolo.com/) web application for performing flood detection using Google Earth Engine in the backend. The module [src/model.py](src/model.py) was adapted and translated to Python from [Radar-based Flood Mapping](https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-radar-based-flood-mapping). If you want to cite the methodology, takes a look at the bibliography available [here](https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-flood-mapping/in-detail).


### Installation

1. Install [Docker Compose](https://docs.docker.com/compose/install/)

2. Install the [EarthEngine Python API](https://developers.google.com/earth-engine/guides/python_install). You must have an active Earth Engine account (the credentials are copied to the app through [volumes](https://docs.docker.com/storage/volumes/))

3. Run the command

  ```
  docker-compose up
  ```

and point your browser to

  ```
  0.0.0.0:80
  ```
to start work


### Functionality

**ee-fastapi** use ready-to-use data freely available in the [Earth Engine Data Catalog](https://developers.google.com/earth-engine/datasets). **ee-fastapi** use the following public dataset:

- [**Sentinel-1 GRD: C-band Synthetic Aperture Radar**](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD): A composite after and before the flood. Main resource.
- [**MERIT DEM: Multi-Error-Removed Improved-Terrain DEM**](https://developers.google.com/earth-engine/datasets/catalog/MERIT_DEM_v1_0_3): To avoid areas with high slope. 
- [**JRC Global Surface Water Metadata, v.1.2**](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_2_Metadata): To avoid water body areas.

<h1 align="center">
  <br>
      <img src=https://user-images.githubusercontent.com/16768318/116002085-48654180-a5f8-11eb-9c7b-458503a6c344.png width=65%>        
  <br>
</h1>


Flood range dates, a hand-selected ROI, and the flood threshold are sent from the front-end to the back-end using [fetch](https://github.com/csaybar/ee-fastapi/blob/43f25d171a5bb17171d64de15af2d4170ca43c12/static/js/main.js#L158). The users control the response through two buttons: **display** and **download**. The display button will attach XYZ map tile resources with the results to the OpenLayer map. These tiles are obtained after running the model and the [ee.data.getMapId](https://developers.google.com/earth-engine/apidocs/ee-data-getmapid) method. On the other hand, the download button will download the flood area in a GeoPackage vector format.

<h1 align="center">
  <br>
      <img src=https://user-images.githubusercontent.com/16768318/116000403-544d0580-a5f0-11eb-8e77-fa8e5e6e46a2.gif width=75%>        
  <br>
</h1>

### Design decisions

#### Why OpenLayer?

It was my first project using OpenLayer, and I can say that I did not miss Leaflet at all!. In my opinion, OpenLayers has much more advantages
over Leaflet. Here are some reasons from the point of view of a novice Web GIS user:

- OpenLayer counts with a complex API. There is no reason to load external plugins for simple tasks like in Leaflet.
- Great documentation and thousand of examples.
- Better map projection support
- I found the OpenLayer API more intuitive.

#### Why Google Earth Engine?

Google Earth Engine has everything: tons of publicly available datasets, a great well-documented API, and high-performance computing.

#### Why fetch?

Fetch API does not need to be installed as a dependency. It utilizes a modern JS syntax and is based on promise rather than callbacks.


### Student personal information

- **Name**: Cesar Luis Aybar Camacho
- **Program**: Copernicus Master in Digital Earth – CDE
- **Student ID**: s1078735
- **Course**: Geo-application Development
