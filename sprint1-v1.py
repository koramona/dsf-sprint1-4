import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import seaborn as sns
import pyreadstat
import geopandas as gpd
import warnings
from PIL import Image
warnings.filterwarnings('ignore')

## PH-HRIR-merged.csv dataset
df = pd.read_csv("data/PH-HRIR-merged.csv")
df_poor = df[(df["V190"] == 'Poorest') | (df["V190"] == 'Poorer')]

#arrange x wrt y
def arrange_x_y(array_x, array_y):
    for i in range(0, len(array_y)):
        x = array_x
        y = array_y
        for j in range(0, len(array_y)):
            if y[i] < y[j]:
                tempx = x[i]
                x[i] = x[j]
                x[j] = tempx
            
                tempy = y[i]
                y[i] = y[j]
                y[j] = tempy
    return x, y

#get percentage
def pct(array, total):
    percentage = []
    
    for k in range(0,len(array)):
        pct = (array[k] / total) * 100
        percentage.append(round(pct,1))
        
    return percentage

def mean(array):
    mean = 0
    for i in range(0, len(array)):
        mean = mean + array[i]
    return mean/len(array)


##start

my_page = st.sidebar.radio('Page Navigation', ['About the project', 'Data description', 'Where are the vulnerable sectors?', 'Do the poor know/avail LGU Health Programs?', 'Where do we need to intervene for government health programs?', 'How can we characterize the households to reach out to?', 'About the team'])

if my_page == 'About the project':
    st.title("Study Title")
    st.header("Can we use a data-driven approach to optimize the limited resources of LGUs and NGOs?")
    st.subheader("With the poor as one of the most vulnerable to health issues, we want to be help institutions on how to optimize their efforts in reaching them.")
        
elif my_page == 'Data description':
    st.title("Data")
    st.header("2017 Philippines Standard DHS Dataset")
    st.subheader("This study took our data from the 2017 Philippies Standard DHS Dataset, looking at the geospatial and household survey data. The dataset had a sample size of 25,074 and columns of 832.")
    if st.checkbox('Show sample data', value = True):
        st.subheader('Data')
        data_load_state = st.text('Loading data...')
        st.write(df.head(20))
        data_load_state.markdown('Loading data...**done!**')
    
elif my_page == 'Where are the vulnerable sectors?':
    st.title("Geospatial Analysis: Where are the vulnerable sectors?")
    st.subheader("With almost half of the respondents (45%) are considered as poor, it would be useful to identify where they are located across the Philippines.")
    
    wealth_index = np.array(df.groupby(["V190"]).size())
    widxname = ["Middle", "Poorer", "Poorest", "Richer", "Richest"]
    
    widx = []

    widx_X, widx_Y = arrange_x_y(widxname, wealth_index)

    fig0 = plt.figure(figsize=(8,6))
    
    widx_pct = pct(widx_Y, len(df.index))
    plt.title("Wealth Index Distribution")
    widx_barh = plt.barh(widx_X, widx_Y, color = "orange")
    ##plt.bar_label(widx_barh, widx_pct, label_type='edge')
    plt.ylabel("# of People")

    st.pyplot(fig0)
    
    
    ##geographic location
    st.text("We observed that there are higher concentrations of poor farther from metros")
    
    shapefile2 = gpd.read_file('data/geo/provinces/Provinces.shp')
    shapefile2["x"] = shapefile2.geometry.centroid.x
    shapefile2["y"] = shapefile2.geometry.centroid.y
    map_center = [14.583197, 121.051538]
    
    # Standardizing syntax of province columns for comparison
    sorted(shapefile2['PROVINCE'].unique()) # Unique province values in shapefile
    sorted(df['SPROV'].unique()) # Unique province values in df

    shp_list = [x.title() for x in shapefile2["PROVINCE"].unique()]
    df_list = [x.title() for x in df["SPROV"].unique()]
    
    # Recode the province columns
    df_recode = {'Isabela City' : 'Basilan', 
                 'Cotabato City': 'Maguindanao', 
                 'Caloocan/Malabon/Navotas/Valenzuela': 'Metropolitan Manila', 
                 'Las Pinas/Makati/Muntinlupa/Paranaque/Pasay/Taguig/Pateros': 'Metropolitan Manila', 
                 'Mandaluyong/Marikina/Pasig/San Juan/Quezon City': 'Metropolitan Manila', 
                 'Manila': 'Metropolitan Manila', 
                 'Cebu (Inc Cities)':'Cebu', 
                 'Samar (Western)':'Samar', 
                 'Compostella Valley':'Compostela Valley', 
                 'Cotabato (North)':'North Cotabato'}

    shp_recode = { 'Shariff Kabunsuan': 'Davao Occidental'}

    df['SPROV_'] = df['SPROV'].apply(lambda x: x.title()).replace(df_recode)
    shapefile2['PROVINCE_'] =  shapefile2['PROVINCE'].apply(lambda x: x.title()).replace(shp_recode)
    
    # Creating a province df
    province_df = df.groupby('SPROV_', as_index = False).agg(size=('CASEID','size'), ave_wealth_idx=('V191','mean'))

    # Merging shapefile2 with province df
    merged_data2 = pd.merge(shapefile2, province_df, left_on = 'PROVINCE_', right_on = 'SPROV_')
    
    variable = 'ave_wealth_idx'
    vmin, vmax = merged_data2[variable].min(), merged_data2[variable].max()

    fig1, ax = plt.subplots(1, figsize=(15, 10))

    merged_data2.plot(column=variable, cmap='Oranges_r', linewidth=0.8, ax=ax, edgecolor='0.8', vmin=vmin, vmax=vmax)
    plt.xlim(115,130)
    plt.ylim(0,25)
    plt.title("Wealth Index")
    sm = plt.cm.ScalarMappable(cmap='Oranges_r', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    cbar = fig1.colorbar(sm)

    st.pyplot(fig1)
    ##st.caption("There are higher concentrations of poor farther from metros")
    
elif my_page == 'Do the poor know/avail LGU Health Programs?':
    st.title("What LGU programs need interventions?")

    top5_prog_name_ = ["Free medical consultation", "Free Medicines", "Free immunization/vaccines", "Family planning programs", "Health and wellness programs"]

    top5_awr_prog = df_poor[["SH301A", "SH301B", "SH301D", "SH301I", "SH301J"]]
    top5_avl_prog = df_poor[["SH302A", "SH302B", "SH302D", "SH302I", "SH302J"]]

    Avail_Program_Most = []
    Aware_Program_Most = []

    for col in top5_avl_prog.columns:
        Value = top5_avl_prog[f'{col}']
        Most = Value.str.contains("Yes").sum()
        Avail_Program_Most.append(Most)

    for col in top5_awr_prog.columns:
        Value_ = top5_awr_prog[f'{col}']
        Most_ = Value_.str.contains("Yes").sum()
        Aware_Program_Most.append(Most_)
    
    avl_pct = pct(Avail_Program_Most, len(df_poor.index))
    awr_pct = pct(Aware_Program_Most, len(df_poor.index))
    
    x = Aware_Program_Most
    x_ = awr_pct
    y = Avail_Program_Most
    y_ = avl_pct
    z = top5_prog_name_

    for i in range(0, len(y)):
        for j in range(0, len(y)):
            if y[i] < y[j]:
                tempx = x[i]
                x[i] = x[j]
                x[j] = tempx

                tempy = y[i]
                y[i] = y[j]
                y[j] = tempy

                tempx_ = x_[i]
                x_[i] = x_[j]
                x_[j] = tempx_

                tempy_ = y_[i]
                y_[i] = y_[j]
                y_[j] = tempy_

                tempz = z[i]
                z[i] = z[j]
                z[j] = tempz
                
    data = {"Availment": y_, "Awareness": x_}
    new_df = pd.DataFrame(data, index = z)
    
    colors = {"Availment":'orange' ,"Awareness":'moccasin'}
    
    g = new_df.plot(kind = "barh", title = "Top 5 Awareness on LGU Programs and their Availment", color = colors)
    
    plt.axvline(x=19.46, color='orange', linestyle='--')
    plt.axvline(x=42.52, color='moccasin', linestyle='--')
    plt.xlabel("Percentages (%)")
    
    fig2 = g.figure
    st.pyplot(fig2)
    st.caption("There is a mid-low awareness and significantly lower availment of LGU Health Programs. Disproportionate awareness & availment of programs. Family planning and Health and Wellness remain considerably low.")
    
    
elif my_page == 'Where do we need to intervene for government health programs?':
    st.title("What regions should we prioritize for health & wellness and family planning programs?")
    
    ## health & wellness programs chart
    
    FP = df_poor[["V024", "SH301I", "SH302I"]]
    
    FP_aware = FP[FP["SH301I"] == "Yes"]
    FP_avail = FP[FP["SH302I"] == "Yes"]
    
    FPg_aware = FP_aware.groupby(["V024",]).size() 
    FPg_avail = FP_avail.groupby(["V024",]).size()
    
    x = np.array(FPg_aware)
    y = np.array(FPg_avail)
    z = np.array(FPg_aware.index)

    for i in range(0, len(y)):
        for j in range(0, len(y)):
            if y[i] < y[j]:
                tempx = x[i]
                x[i] = x[j]
                x[j] = tempx

                tempy = y[i]
                y[i] = y[j]
                y[j] = tempy

                tempz = z[i]
                z[i] = z[j]
                z[j] = tempz
     
    x_ = np.arange(17)
    width = 0.40
    
    h = plt.figure(figsize=(8,6))
    
    plt.barh(x_ - 0.2, y,width, color = 'orange')
    plt.barh(x_ + 0.2, x, width, color = '#ffe4b5')
    plt.xlabel("# of People")
    plt.yticks(x_, z)
    plt.legend(["Awareness", "Availment"])
    plt.title("Number of People per Region (Family Planning)")

    st.pyplot(h)
    st.caption("Cagayan, N. Mindanao, Socksargen, Ilocos & Calabarzon seems to have problems with awareness and availment of Health programs.")             
              
    ## Family Planning Chart      
    
    HWP = df_poor[["V024", "SH301J", "SH302J"]]
    
    HWP_aware = HWP[HWP["SH301J"] == "Yes"]
    HWP_avail = HWP[HWP["SH302J"] == "Yes"]
    
    HWPg_aware = HWP_aware.groupby(["V024",]).size() #number of people that took Family Planning
    HWPg_avail = HWP_avail.groupby(["V024",]).size()
    
    x1 = np.array(HWPg_aware)
    y1 = np.array(HWPg_avail)
    z1 = np.array(HWPg_aware.index)

    for i in range(0, len(y1)):
        for j in range(0, len(y1)):
            if y1[i] < y1[j]:
                tempx = x1[i]
                x1[i] = x1[j]
                x1[j] = tempx

                tempy = y1[i]
                y1[i] = y1[j]
                y1[j] = tempy

                tempz = z1[i]
                z1[i] = z1[j]
                z1[j] = tempz
    
    x_1 = np.arange(17)
    width = 0.40
    
    k  = plt.figure(figsize=(8,6))
    
    plt.barh(x_1 - 0.2, y,width, color = 'orange')
    plt.barh(x_1 + 0.2, x, width, color = '#ffe4b5')
    plt.yticks(x_1, z1)
    plt.xlabel("# of People")
    plt.legend(["Awareness", "Availment"])
    plt.title("Number of People per Region (Health and Wellness Programs)")
    
    st.pyplot(k)
    st.caption("NCR, Regions III, IV-A, IV-B and Ilocos seems to have problems with awareness and availment of Family Planning programs.")
    
elif my_page == 'How can we characterize the households to reach out to?':
    st.title("How can we characterize the households to reach out to?")
    st.subheader("Upon a cluster analysis (k-means) of the households, we've identified the following household segmentations:")
    
    cgroup1 = Image.open('sprint1-fig/cluster_group1.png')
    cgroup2 = Image.open('sprint1-fig/cluster_group2.png')
    cgroup3 = Image.open('sprint1-fig/cluster_group3.png')
    cgroup4 = Image.open('sprint1-fig/cluster_group4.png')
    
    st.image(cgroup1, caption='Cluster group 1: the introverts - aware of LGU programs but do not avail them. We can explore what their barriers are to availment as this group of households are located in rural areas. They share their household with members who have been sick/injured in the past 30 days.')
    st.image(cgroup2, caption='Cluster group 2: 4Ps members - 4Ps members tended to be aware and avail of LGU programs which may mean they are in compliance with the program and that they are reached by government efforts.')
    st.image(cgroup3, caption='Cluster group 3: ideal - households are aware and availing of LGU health programs while tending not to experience any member sick/injured in the past 30 days or confined in a hospital/clinic in the past 12 months.')
    st.image(cgroup4, caption='Cluster group 4: the extroverts - While they claim they are not aware of any LGU health program, they report to have availed of at least one government health program. There may be a gap in government communication campaigns that lead to a mismatch of the households understanding.')
    
elif my_page == 'About the team':
    st.title("About the team")
    st.markdown("The team is composed of **Karl Aleta**, **Ely Geniston**, **Nino Moreno**,  and **Christian Tan** who are data science fellows at Eskwelabs. They aim to learn, get hands-on experience, and apply their learnings in solving real-world issues.")