import streamlit as st
import pydeck as pdk
from pymongo import MongoClient
import pandas as pd

from constants import Constants

class App:
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
    def __init__(self) -> None:
        self.db_client = MongoClient(**st.secrets['mongo'])
        self.user_requests_collection = self.db_client[Constants.DATABASE_NAME][Constants.USER_REQUESTS_COLLECTION_NAME]
        self.last_searched_collection = self.db_client[Constants.DATABASE_NAME][Constants.LAST_SEARCHED_COLLECTION_NAME]


    def get_initial_view_state(self,village_poly):
        """
        Creates initial view state for the map layer.
        Directs streamlit to got to the centroid of the given village
        Shows the map at zoom level 12 (default)
        """
        centroid_lon,centroid_lat = village_poly.centroid.x,village_poly.centroid.y
        return pdk.ViewState(
            latitude=centroid_lat,
            longitude=centroid_lon,
            zoom=13,
            pitch=50,
        )
    
    def select_from(self,options,index):
        """
        Provides a dropdown for user to select/enter his village name
        """
        return st.selectbox(
            label='Which village in Bengaluru do you live in ?',
            options=options,
            index=index,
            placeholder="Select your village..."
        )

    def get_map_layers(self,low_points_in_village_df,selected_village_poly): 
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
            get_fill_color="[255, 0, 100, 30]",
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

    def select_layers(self,layers):
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

    def create_map(self,selected_layers,village_poly):
        """
        Creates a Pydeck chart for the selected layers which is dispayed on Streamlit map
        """
        st.pydeck_chart(
            pdk.Deck(
                map_style=None,
                initial_view_state=self.get_initial_view_state(village_poly),
                layers=[selected_layers],
            )
        )
    
    def error(self,err):
        return st.error(err)
    
    def fetch(self):
        df = pd.DataFrame(self.user_requests_collection.find()).drop('_id',axis=1)
        return df if len(df) != 0 else "None"
    
    def persist(self,village):
        self.user_requests_collection.update_one(
            { "village": village },
            { "$inc": { "count": 1 }, "$set": { "last": True }},
            upsert = True
        )
        self.user_requests_collection.update_many(
            { "village": {"$ne": village }},
            { "$set": { "last": False } }
        )
    
    def search_history(self):
        """
        Creates a sidebar with radio buttons to enable selecting from `layers`
        """
        st.sidebar.markdown("### Search History")
        st.sidebar.write(self.fetch())

    def last_searched_village(self):
        last_searched_village = self.user_requests_collection.find_one({"last":True})
        return last_searched_village if last_searched_village else {"village": None}