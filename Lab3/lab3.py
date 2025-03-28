import streamlit as st
import pandas as pd
import os
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

def change_ProvinceID(general_df: pd.DataFrame) -> None:
    replace_dict: dict = {key: value[0] for key, value in province_index_dict.items()}
    general_df['RegionID'] = general_df['RegionID'].replace(replace_dict)


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
    # display(df)

def parse_csv(path: str) -> pd.DataFrame: 
    for file in os.listdir(path):
        i = file.split(sep='_')[2]
        df = pd.read_csv(f'{path}/{file}', header = 1, names = headers)
        normalize_dataframe(df, i)
    return pd.concat(dfs).reset_index(drop=True)

class StreamlitPage():
    def __init__(self: "StreamlitPage", general_df: pd.DataFrame, true_regs: list) -> None:
        self.streamlit_defaults = {
            'selected_area': true_regs[0],
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
        self.left_column, self.right_column = st.columns([2.7, 1], gap='large')
        self.right_col_setup()
        self.left_col_setup()

    def initialize_default_streamlit(self: "StreamlitPage"):
        for key, value in self.streamlit_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def right_col_setup(self: "StreamlitPage")->None:
        with self.right_column:
            st.selectbox('Sort by', options=self.sort_data, key='sort_data')
            st.selectbox('Choose region', options=self.true_regs, key="selected_area")
            st.slider('Week range', min_value=1, max_value=52, key="week_range")
            st.slider('Year range', 1982, 2024, key='year_range')
            
            col1: st.delta_generator.DeltaGenerator
            col2: st.delta_generator.DeltaGenerator
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox('Ascending', key='ascending_key')
            with col2:
                st.checkbox('Descending', key='descending_key')
        
            if st.button('Reset filters'):
                for key in st.session_state.keys():
                    del st.session_state[key]
                self.initialize_default_streamlit()
                st.rerun()
    
    def left_col_setup(self: "StreamlitPage"):
        with self.left_column:
            st.write(self.general_df.head(53))

def main():
    general_df = parse_csv("..\\Lab2\\csv_files")
    true_regs = [region for _, region in true_regs_with_indexes.items()]
    StreamlitPage(general_df, true_regs)

if __name__ == "__main__":
    main()
    