import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from PIL import Image


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
    
    slide1 = Image.open('sprint1-fig/slide1.png')
    st.image(slide1, caption='')
    
    
    ##geographic location
    st.text("We observed that there are higher concentrations of poor farther from metros")
    
    slide2 = Image.open('sprint1-fig/slide2.png')
    st.image(slide2, caption='')
  
    
elif my_page == 'Do the poor know/avail LGU Health Programs?':
    st.title("What LGU programs need interventions?")

    slide3 = Image.open('sprint1-fig/slide3.png')
    st.image(slide3, caption='There is a mid-low awareness and significantly lower availment of LGU Health Programs. Disproportionate awareness & availment of programs. Family planning and Health and Wellness remain considerably low.')
   
    
elif my_page == 'Where do we need to intervene for government health programs?':
    st.title("What regions should we prioritize for health & wellness and family planning programs?")
    
    ## health & wellness programs chart
    
    slide4 = Image.open('sprint1-fig/slide4.png')
    st.image(slide4, caption=' ')
    
          
              
    ## Family Planning Chart      
    
    slide5 = Image.open('sprint1-fig/slide5.png')
    st.image(slide5, caption=' ')
    
elif my_page == 'How can we characterize the households to reach out to?':
    st.title("How can we characterize the households to reach out to?")
    st.header("Upon a cluster analysis (k-means) of the households, we've identified the following household segmentations:")
    
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