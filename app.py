from segmentation.static_segmentation import StaticSegmentation

import streamlit as st

if __name__=='__main__':
    # dtm_path = './data/n12_e077_1arc_v3.tif'
    file_path = './output/low_lying_pts.csv'
    seg = StaticSegmentation(file_path=file_path)
    df = seg.segment()
    st.map(df,latitude='y',longitude='x',size=5)