from segmentation.raster_segmentation import RasterSegmentation
from segmentation.static_segmentation import StaticSegmentation

import streamlit as st
import pydeck as pdk

def get_initial_view_state():
    return pdk.ViewState(
        latitude=12.969,
        longitude=77.739661,
        zoom=15,
        pitch=50,
    )

def get_map_layers(low_points_df,village_polygons_df):
    return  {
        "Low Lying Areas":
            pdk.Layer(
                "ScatterplotLayer",
                data=low_points_df,
                get_position="[x, y]",
                get_color="[200, 30, 0, 160]",
                get_radius=5,
                xspickable=True
            ),
        "Village Boundaries":
            pdk.Layer(
                "PolygonLayer",
                data=village_polygons_df,
                stroked=False,
                get_polygon='-',
                get_fill_color=[0, 0, 0, 20],
                pickable=True
            ),
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
    low_points_file_path = './output/low_lying_pts.csv'
    bangalore_villages_file_path = './data/20_Bengaluru_Urban/20_Bengaluru _Urban.shp'
    seg = StaticSegmentation(file_path=low_points_file_path)
    low_points_df = seg.segment()
    layers = get_map_layers(low_points_df)
    selected_layers = select_layers(layers)
    if selected_layers:
        create_map(selected_layers)
    else:
        st.error("Please choose at least one layer above.")