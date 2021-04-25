from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.utils import searching_all_files, raster_to_vector
from src.model import db_creator, flood_estimation, display
from zipfile import ZipFile
import geopandas as gpd
import uvicorn
import ee, os, time

# from src.utils import load_credentials

# Init Earth Engine
# load_credentials() -> useful to deploy with heroku
ee.Initialize()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000"
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://0.0.0.0",
    "http://0.0.0.0:80",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static folder in the app
app.mount("/static", StaticFiles(directory="static"), name="static") 
app.mount("/output", StaticFiles(directory="output"), name="output") 

# Load html templates
templates = Jinja2Templates(directory="template")

# display map
@app.get("/")
async def map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.post("/flood_download")
async def flood_model(request: Request):
    # request parameters
    request_params = await request.json()
    
    # get parameters
    xmin, ymin, xmax, ymax = [float(x) for x in request_params["bbox"].split(",")]
    init_start = request_params["init_start"]
    init_last = request_params["init_last"]
    flood_start = request_params["flood_start"]
    flood_last = request_params["flood_last"]
    flood_threshold = float(request_params["flood_threshold"])
    
    # 1. Create geometry
    ee_rectangle = ee.Geometry.Rectangle(xmin, ymin, xmax, ymax)
    
    # 2. Create range dates
    base_period = (init_start, init_last)
    flood_period = (flood_start, flood_last)
    
    # 3. Run the flood model    
    dict_db = db_creator(base_period, flood_period, ee_rectangle)
    flood_added = flood_estimation(dict_db, difference_threshold=flood_threshold)
            
    # 4. Create GeoJSON
    geo_file_geojson = 'output/flood_area_%s.gpkg' % (time.strftime("%Y%m%d%H%M%S", time.gmtime()))
    final_flood_area = raster_to_vector(flood_added["flood_results"], ee_rectangle)
    final_flood_area_gpd = gpd.GeoDataFrame.from_features(final_flood_area["features"])
    final_flood_area_gpd[final_flood_area_gpd.label == 1].to_file(geo_file_geojson, driver="GPKG")    
    print(geo_file_geojson)
    return geo_file_geojson

# model 
@app.post("/flood_display")
async def flood_model(request: Request):
    # 1. request parameters
    request_params = await request.json()
    
    # 2. get parameters
    xmin, ymin, xmax, ymax = [float(x) for x in request_params["bbox"].split(",")]
    init_start = request_params["init_start"]
    init_last = request_params["init_last"]
    flood_start = request_params["flood_start"]
    flood_last = request_params["flood_last"]
    flood_threshold = float(request_params["flood_threshold"])
    
    # 3. Create geometry
    ee_rectangle = ee.Geometry.Rectangle(xmin, ymin, xmax, ymax)
    
    # 4. Create range dates
    base_period = (init_start, init_last)
    flood_period = (flood_start, flood_last)
    
    # 5. Run the flood model    
    dict_db = db_creator(base_period, flood_period, ee_rectangle)
    flood_added = flood_estimation(dict_db, difference_threshold=flood_threshold)    
    
    # 6. Upload gee tileid
    tileids = display(flood_added)
    
    return tileids

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)