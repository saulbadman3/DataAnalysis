import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display

headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
province_index_dict = {
    1: (22, 'Черкаська'), 2: (24, 'Чернігівська'), 3: (23, 'Чернівецька'), 4: (25, 'Крим'), 5: (3, 'Дніпропетровська'), 
    6: (4, 'Донецька'), 7: (8, 'Івано-Франківська'), 8: (19 , 'Харківська'), 9: (20, 'Херсонська'), 10: (21, 'Хмельницька'),
    11: (9, 'Київська'), 13: (10, 'Кіровоградська'), 14: (11, 'Луганська'), 15: (12, 'Львівська'), 16: (13, 'Миколаївська'), 
    17: (14, 'Одеська'), 18: (15, 'Полтавська'), 19: (16, 'Рівненська'), 21: (17, 'Сумська'), 22: (18, 'Тернопільська'),
    23: (6, 'Закарпатська'), 24: (1, 'Вінницька'), 25: (2, 'Волинська'), 26: (7, 'Запорізька'), 27: (5, 'Житомирська')
    }

true_regs_with_indexes: dict = dict(sorted({region[0]: region[1] for key, region in province_index_dict.items()}.items()))
dfs: list = []

# Method to change province id based on ukrainian alphabet
def change_ProvinceID(general_df: pd.DataFrame) -> None:
    replace_dict: dict = {key: value[0] for key, value in province_index_dict.items()}
    general_df['RegionID'] = general_df['RegionID'].replace(replace_dict)

# Method to normalize dataframes
def normalize_dataframe(df: pd.DataFrame, i: int) -> None:
    # dropping NaN values
    df = df.dropna(subset=['VHI']).drop(columns=['empty'])
    df = df.drop(df.loc[df['VHI'] == -1].index)
    # normalizing data
    df["Year"] = df["Year"].str.extract(r"(\d+)").astype(int)
    df['Week'] = df['Week'].astype(int)

    #Adding ids for all provinces
    df.insert(0, 'RegionID', [int(i)] * df.shape[0])
    change_ProvinceID(df)
    df.insert(1, 'Region', 0)
    df['Region'] = df['RegionID'].map(true_regs_with_indexes)
    dfs.append(df)

# Method to parse csv files
def parse_csv(path: str) -> pd.DataFrame: 
    for file in os.listdir(path):
        i = file.split(sep='_')[2]
        df = pd.read_csv(f'{path}/{file}', header = 1, names = headers)
        normalize_dataframe(df, i)
    return pd.concat(dfs).reset_index(drop=True)

# Class to implement streamlit page
class StreamlitPage():
    # Class initializer
    def __init__(self: "StreamlitPage", general_df: pd.DataFrame, true_regs: list) -> None:
        self.streamlit_defaults = {
            'selected_region': true_regs[0],
            'week_range': (1, 52),
            'year_range': (1982, 2024),
            'sort_data': 'VHI',
            'ascending_key': False,
            'descending_key': False,
        }

        self.sort_data: list = ['VCI', 'TCI', 'VHI']
        self.true_regs = true_regs
        self.general_df = general_df
        st.set_page_config(layout="wide")
        st.title('Vegetation Health stats per region in Ukraine')
        self.initialize_default_streamlit()
        self.left_column, self.right_column = st.columns([3, 1], gap='large')
        self.right_col_setup()
        self.left_col_setup()

    # Initialize streamlit session state
    def initialize_default_streamlit(self: "StreamlitPage") -> None:
        for key, value in self.streamlit_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # Callback function when "ascending" checkbox is ticked
    def toggle_ascending(self: "StreamlitPage") -> None:
        if st.session_state['ascending_key']:
            st.session_state['descending_key'] = False

    # Callback function when "descending" checkbox is ticked
    def toggle_descending(self: "StreamlitPage") -> None:
        if st.session_state['descending_key']:
            st.session_state['ascending_key'] = False

    # Method to setup right column of the app (interactive part)
    def right_col_setup(self: "StreamlitPage") -> None:
        with self.right_column:
            st.selectbox('Sort by', options=self.sort_data, key='sort_data')
            st.selectbox('Choose region', options=self.true_regs, key="selected_region")
            st.slider('Week range', min_value=1, max_value=52, key="week_range")
            st.slider('Year range', 1982, 2024, key='year_range')
            
            col1: st.delta_generator.DeltaGenerator
            col2: st.delta_generator.DeltaGenerator
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox('Ascending', key='ascending_key', on_change=self.toggle_ascending)
            with col2:
                st.checkbox('Descending', key='descending_key', on_change=self.toggle_descending)
        
            if st.button('Reset filters'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                self.initialize_default_streamlit()
                st.rerun()

    
    # Method to create filtered dataframe for exact region, week range, year range sorted by sort data in exact sorting order
    def filter_df(self: "StreamlitPage", region_id: int, week_range: tuple, year_range: tuple, sort_data: str, sort_order: bool) -> pd.DataFrame:
        filtered_df = self.general_df[(region_id==self.general_df['RegionID']) & 
                                      (self.general_df['Week'].between(week_range[0], week_range[1])) &
                        (self.general_df['Year'].between(year_range[0], year_range[1]))].sort_values(by=sort_data, ascending = sort_order)
        filtered_df['Full_date'] = pd.to_datetime(filtered_df['Year'].astype(str) + '-' + filtered_df['Week'].astype(str) + '-0', format="%Y-%W-%w").dt.date
        return filtered_df[['RegionID', 'Region', 'Year', 'Week', 'Full_date', 'VCI', 'TCI', 'VHI']]

    # Nethod to create filtered dataframe of compare data for all regions to compare in specific year range
    def filter_compare_df(self: "StreamlitPage", year_range: tuple, compare_data: str) -> pd.DataFrame:
        filtered_compare_df =  self.general_df[(self.general_df['Year'].between(year_range[0], year_range[1]))][['Region', 'Year', 'Week', compare_data]]
        return filtered_compare_df.pivot_table(index='Region', 
                                            columns='Year', 
                                            values=st.session_state['sort_data'],
                                            aggfunc='mean')

    # Method to setup the left column with plots and dataframes in separate tabs
    def left_col_setup(self: "StreamlitPage") -> None:
        with self.left_column:
            tab1, tab2, tab3 = st.tabs(['Filtered data table', 'Filtered data plot', 'Comparison plot'])
            filtered_df = self.filter_df(next(region_id for region_id, region_name in true_regs_with_indexes.items() if region_name == 
                                st.session_state['selected_region']), 
                                st.session_state['week_range'], 
                                st.session_state['year_range'],
                                 st.session_state['sort_data'],  
                                 True if not st.session_state['ascending_key'] and not st.session_state['descending_key'] else st.session_state['ascending_key'])
            filtered_compare_df = self.filter_compare_df(st.session_state['year_range'], st.session_state['sort_data'])
            
            with tab1:
                st.dataframe(data=filtered_df[['RegionID', 'Region', 'Year', 'Week', 'VCI', 'TCI', 'VHI']], use_container_width=True)
            
            with tab2:
                st.header(f'Line chart for {st.session_state['selected_region']} region')
                st.line_chart(data=filtered_df, x='Full_date', y=self.sort_data)
            
            with tab3:
                st.header(f"Heatmap of {st.session_state['sort_data']} for regions "
                          f"in year range {st.session_state['year_range'][0]}-{st.session_state['year_range'][1]}")
                fig, ax = plt.subplots(figsize=(15, 15))
                sns.heatmap(filtered_compare_df, annot=False, cmap="Blues", linewidths=0.5, ax=ax)
                st.pyplot(fig)

# main method
def main():
    general_df: pd.DataFrame = parse_csv("..\\Lab2\\csv_files")
    true_regs = [region for _, region in true_regs_with_indexes.items()]
    StreamlitPage(general_df, true_regs)

if __name__ == "__main__":
    main()
    