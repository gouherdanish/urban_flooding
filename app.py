import streamlit as st
import pydeck as pdk
import geopandas as gpd
from shapely.geometry import mapping

from segmentation.raster_segmentation import RasterSegmentation
from segmentation.static_segmentation import StaticSegmentation

def get_initial_view_state(village_poly):
    """
    Creates initial view state for the map layer.
    Directs streamlit to got to the centroid of the given village
    Shows the map at zoom level 12 (default)
    """
    centroid_lon,centroid_lat = village_poly.centroid.x,village_poly.centroid.y
    return pdk.ViewState(
        latitude=centroid_lat,
        longitude=centroid_lon,
        zoom=12,
        pitch=50,
    )

def get_map_layers(low_points_in_village_df,selected_village_poly): 
    """
    Creates village boundary in a format that is accepted by Pydeck
    Creates polygon layer for showing Village Boundary on map
    Creates point layer for showing Low lying points on map
    """
    village_boundary = [list(coord) for coord in selected_village_poly.exterior.coords] 
    village_polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=[village_boundary],
        get_polygon='-',
        stroked=False,
        filled=True,
        get_fill_color="[255, 0, 100, 160]",
        pickable=True
    )
    low_points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=low_points_in_village_df.drop('geometry',axis=1),
        get_position="[x, y]",
        get_color="[200, 30, 0, 160]",
        get_radius=10,
        pickable=True
    )
    return  {
        "Low Lying Areas":low_points_layer,
        "Village Boundaries":village_polygon_layer,
    }

def select_layers(layers):
    """
    Creates a sidebar with radio buttons to enable selecting from `layers`
    """
    st.sidebar.markdown("### Map Layers")
    selected_layers = [
        layer
        for layer_name, layer in layers.items()
        if st.sidebar.checkbox(layer_name, True)
    ]
    return selected_layers

def create_map(selected_layers,village_poly):
    """
    Creates a Pydeck chart for the selected layers which is dispayed on Streamlit map
    """
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=get_initial_view_state(village_poly),
            layers=[selected_layers],
        )
    )
    

if __name__=='__main__':
    """
    Main entry point for streamlit app

    Step 1: Create low lying points data using suitable Image Segmentation Process
        a) Raster Segmentation - performs segmentation on raster afresh
        >>> dtm_path = './data/n12_e077_1arc_v3.tif'
        >>> seg = RasterSegmentation(dtm_path=dtm_path)

        b) Static Segmentation Data - reads already segmented and saved local data
        >>> low_points_file_path = './output/low_lying_pts.shp'
        >>> seg = StaticSegmentation(file_path=low_points_file_path)

        Note: Online segmentation using raster is expensive operation and causes latency on user's end.
        Therefore, the app uses static segmentation currently by default

    Step 2: Read Bangalore Villages Shpfile Data
    
    Step 3: Filter low lying points data for user-selected village

    Step 4: Create Streamlit Map for Selected Village and underlying low lying points
    """

    # Image Segmentation
    low_points_file_path = './output/low_lying_pts.shp'
    seg = StaticSegmentation(file_path=low_points_file_path)
    low_points_df = seg.segment()

    # Bangalore Villages
    bangalore_villages_file_path = './data/20_Bengaluru_Urban/20_Bengaluru _Urban.shp'
    village_polygons_df = gpd.read_file(bangalore_villages_file_path).to_crs('EPSG:4326')
    
    # User-selected Village
    options = village_polygons_df['KGISVill_2'].values
    selected_village = st.selectbox(
        label='Which village in Bengaluru do you live in ?',
        options=options,
        placeholder="Select your village..."
    )
    selected_village_df = village_polygons_df.loc[village_polygons_df['KGISVill_2']==selected_village,['geometry']].reset_index(drop=True).iloc[-1:,:]
    
    # Filtering Low lying points inside selected village
    low_points_in_village_df = gpd.sjoin(low_points_df,selected_village_df,predicate='within',how='inner').drop('index_right',axis=1).reset_index(drop=True)
    village_poly = selected_village_df.values[0][0]

    # Creating Layers for Streamlit Map
    layers = get_map_layers(low_points_in_village_df,village_poly)

    # Providing Option to select/un-select layers
    selected_layers = select_layers(layers)
    
    # Creating Streamlit Map
    if selected_layers:
        create_map(selected_layers,village_poly)
    else:
        st.error("Please choose at least one layer above.")