from segmentation.static_segmentation import StaticSegmentation

import streamlit as st
import pydeck as pdk

def get_map_layers():
    # dtm_path = './data/n12_e077_1arc_v3.tif'
    file_path = './output/low_lying_pts.csv'
    seg = StaticSegmentation(file_path=file_path)
    df = seg.segment()
    return  {
        "Low Lying Areas":
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position="[x, y]",
                get_color="[200, 30, 0, 160]",
                get_radius=5,
            ),
    }

if __name__=='__main__':
    layers = get_map_layers()
    st.sidebar.markdown("### Map Layers")
    selected_layers = [
        layer
        for layer_name, layer in layers.items()
        if st.sidebar.checkbox(layer_name, True)
    ]
    if selected_layers:
        st.pydeck_chart(
            pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(
                    latitude=12.97,
                    longitude=77.74,
                    zoom=17,
                    pitch=50,
                ),
                layers=[selected_layers],
            )
        )
    else:
        st.error("Please choose at least one layer above.")