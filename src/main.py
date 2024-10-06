import geopandas as gpd

from segmentation.raster_segmentation import RasterSegmentation
from segmentation.static_segmentation import StaticSegmentation
from app import App

if __name__=='__main__':
    app = App()

    # Image Segmentation
    low_points_file_path = '../data/low_lying_points/low_lying_pts.shp'
    seg = StaticSegmentation(file_path=low_points_file_path)
    low_points_df = seg.segment()

    # Bangalore Villages
    bangalore_villages_file_path = '../data/20_Bengaluru_Urban/20_Bengaluru _Urban.shp'
    village_polygons_df = gpd.read_file(bangalore_villages_file_path).to_crs('EPSG:4326')
    
    # User-selected Village
    options = village_polygons_df['KGISVill_2'].values
    selected_village = app.select_from(options)
    selected_village_df = village_polygons_df.loc[village_polygons_df['KGISVill_2']==selected_village,['geometry']].reset_index(drop=True).iloc[-1:,:]
    
    # Filtering Low lying points inside selected village
    low_points_in_village_df = gpd.sjoin(low_points_df,selected_village_df,predicate='within',how='inner').drop('index_right',axis=1).reset_index(drop=True)
    village_poly = selected_village_df.values[0][0]

    # Creating Layers for Streamlit Map
    layers = app.get_map_layers(low_points_in_village_df,village_poly)

    # Providing Option to select/un-select layers
    selected_layers = app.select_layers(layers)
    
    # Creating Streamlit Map
    if selected_layers:
        app.create_map(selected_layers,village_poly)
    else:
        app.error("Please choose at least one layer above.")