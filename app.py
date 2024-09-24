import streamlit as st
import pydeck as pdk
import geopandas as gpd
from shapely.geometry import mapping

from segmentation.raster_segmentation import RasterSegmentation
from segmentation.static_segmentation import StaticSegmentation

def get_village_boundary(village_polygons_df,selected_village):
    village_poly = village_polygons_df.loc[village_polygons_df['KGISVill_2']==selected_village,'geometry'].values[0]
    village_boundary = [list(coord) for coord in village_poly.exterior.coords]  
    return [village_boundary]

def get_initial_view_state():
    return pdk.ViewState(
        latitude=12.969,
        longitude=77.739661,
        zoom=15,
        pitch=50,
    )

def get_map_layers(low_points_df,village_polygons_df):
    options = village_polygons_df['KGISVill_2'].values
    selected_village = st.selectbox(
        label='Which village in Bengaluru do you live in ?',
        options=options,
        index=None,
        placeholder="Select your village...")
    village_boundary = get_village_boundary(village_polygons_df,selected_village)
    village_polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=village_boundary,
        get_polygon='-',
        stroked=False,
        filled=True,
        get_fill_color=[122, 255, 100, 20],
        pickable=True
    )
    low_points_layer = pdk.Layer(
        "ScatterplotLayer",
        data=low_points_df.drop('geometry',axis=1),
        get_position="[x, y]",
        get_color="[200, 30, 0, 160]",
        get_radius=5,
        pickable=True
    )
    return  {
        "Low Lying Areas":low_points_layer,
        "Village Boundaries":village_polygon_layer,
    }

def select_layers(layers):
    st.sidebar.markdown("### Map Layers")
    selected_layers = [
        layer
        for layer_name, layer in layers.items()
        if st.sidebar.checkbox(layer_name, True)
    ]
    return selected_layers

def create_map(selected_layers):
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=get_initial_view_state(),
            layers=[selected_layers],
        )
    )
    

if __name__=='__main__':
    # dtm_path = './data/n12_e077_1arc_v3.tif'
    # seg = RasterSegmentation(dtm_path=dtm_path)
    low_points_file_path = './output/low_lying_pts.shp'
    bangalore_villages_file_path = './data/20_Bengaluru_Urban/20_Bengaluru _Urban.shp'
    
    seg = StaticSegmentation(file_path=low_points_file_path)
    low_points_df = seg.segment()
    village_polygons_df = gpd.read_file(bangalore_villages_file_path).to_crs('EPSG:4326')
    layers = get_map_layers(low_points_df,village_polygons_df)
    selected_layers = select_layers(layers)
    if selected_layers:
        create_map(selected_layers)
    else:
        st.error("Please choose at least one layer above.")