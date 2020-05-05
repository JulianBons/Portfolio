#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 13:18:00 2020

@author: julianbons
"""

import os
import pandas as pd
import plotly.graph_objs as go
import matplotlib.cm
from sklearn.preprocessing import MinMaxScaler

#Import data containing the mental disorder cases
disorders = pd.read_csv('Data/number-with-mental-health-disorders-by-sex.csv')
disorders.columns = ['Country', 'Code', 'Year', 'Males', 'Females']

#Import data containing the specific disorders
prev_dis = pd.read_csv('Data/prevalence-by-mental-and-substance-use-disorder.csv')
prev_dis = prev_dis.rename(columns = {'Entity': 'Country'})


#Import data containing the countries populations
pop = pd.read_csv('Data/projected-population-by-country.csv')
pop.columns = ['Country', 'Code', 'Year', 'Population']


#Only keep relevant years
pop['Year'] = pop[(pop['Year'].str.len() == 4)]['Year'].astype('int64')
population = pop[(pop['Year'] <= 2016) & (pop['Year'] >= 1990)]


#Merge and clean the data
df_dis = pd.merge(disorders, prev_dis, on=['Country', 'Year', 'Code'], how='left')
df = pd.merge(df_dis, population, on=['Country', 'Year', 'Code'], how='left')

df.dropna(inplace=True)
df['Country'].replace('Micronesia (country)', 'Federated States of Micronesia', inplace=True)

#Drop the "world" entry, as we will use the actual data later anyway to aggregate for Continents 
df = df[(df['Country'] != 'World')]




#Summarize data by year
year = df.groupby(['Year'], as_index = False).agg('sum')

year['total'] = year[['Males', 'Females']].sum(axis=1)
year['prevalence'] = year['total']/year['Population']


#Base boarder color on value
bord_col = year[['prevalence']]
bord_col = MinMaxScaler().fit_transform(bord_col)
rgba = matplotlib.cm.get_cmap('viridis')(bord_col)
rgba_list = []
for el in range(len(rgba)):
    rgba_list.append('rgba(' + str(rgba[el][0][0]) + ', ' + str(rgba[el][0][1]) + ', ' +  str(rgba[el][0][2]) + ', ' + str(rgba[el][0][3]) + ')')


#Add text and avoide x-flag
hovertexts = []
for indx in range(len(year['Year'])):
      hovertexts.append('Year: <b>{x}</b> <br>Prevalence: <b>{y:.2%}'.format(x=year['Year'][indx], y=year['prevalence'][indx]))


#Construct scatterplot; Mental disorders by year
fig1 = go.Figure(
    data = [go.Scatter(
        x = year['Year'],
        y = year['prevalence'],
        mode = 'lines+markers',
        marker = dict(
            size = 10, 
            color = year['prevalence'], 
            colorscale = 'Viridis'
        ),
        line_color = 'Lightsteelblue',
        opacity = 0.8,
        hovertext = hovertexts, 
        #hovertemplate = 'Year: <b>%{x}</b> <br>Prevalence: <b>%{y:.2%}<extra></extra>',
        hoverinfo = 'text',
        hoverlabel = dict(
            bgcolor = '#f5f5f5',
            bordercolor = rgba_list,
            align = 'left',
            font_size = 12, 
            font_color = 'black',
            font_family = 'Arial'),
        )
    ], 
    layout = (dict(
        width = 700, 
        height = 600,
	
        yaxis = dict(
            title = '12 month prevalence in %',
            gridcolor = 'lightgrey',
            gridwidth = 1,
            range = [0.1199, 0.1301],
            tickformat = '.1%',
	    fixedrange = True,   
        ),
        xaxis = dict(
            title = 'Year',
            showgrid = False,
            ticks = 'outside',
	    fixedrange = True,   
            showspikes = True, 
            spikemode = 'across',
            spikethickness = 1,
            spikedash = 'solid',
            spikecolor = 'lightgray'
        ),
        spikedistance = -1,
        hovermode = 'x',
        paper_bgcolor = 'white',
        plot_bgcolor = 'white', 
        margin_pad = 10,
        margin_r = 5,
        margin_t = 80,
        annotations = [dict(
            text = '1990 to 2016',
            x = 2001.25, 
            y = 13.1,
            showarrow = False,
            font_size = 15)]
        )
    )
)




    
#Percentage of women/men of total cases
year_2016 = year[year['Year'] == 2016]
y = [float(year_2016['Males']/year_2016['total']), 
     float(year_2016['Females']/year_2016['total'])]

#Construct second graph: Piechart, percentage of women, men
fig2 = go.Figure(
    data = [go.Pie(
        labels = ['Male', 'Female'],
        values = y, 
        marker_colors = ['steelblue', 'indianred'],
        pull = 0.01,
        hoverinfo = 'skip',
        hole = .5,
        texttemplate = '<b>%{label}</b><br>%{value:.2%}',
        textposition = 'outside',
        textinfo = 'percent+label',
        ),      
    ],
    layout = dict(
        width = 500,
        height = 500,
        yaxis_showticklabels = False,
	xaxis_fixedrange = True,
	yaxis_fixedrange = True,
        paper_bgcolor = 'white', 
        plot_bgcolor = 'white',
        annotations = [
            dict(
                text = str(float(year_2016['total']))[:3] + ' MM.', 
                x = 0.5, 
                y = 0.5, 
                font_size = 25, 
                showarrow = False), 
            dict(
                text = '2016',
                x = 0.5,
                y = 0.45,
                font_size = 15,
                showarrow = False)
            ],
        showlegend = False,
        margin = dict(
            l = 50, 
            r = 50,
            b = 0
        )
    )
)




#Prepare percentage of disorders 
ges_dis = df[df['Year'] == 2016].groupby(['Year'], as_index = False).agg('mean').sort_values(0, axis = 1)

x = ges_dis.iloc[:, 0:7].values[0]
y = [i[:-3] for i in ges_dis.columns[0:7]]

#Add the value labels
annot = [round(float(i), 2) for i in x]
annotations = []
for xd, yd in zip(annot, y):
    annotations.append(dict(xref='x1', yref='y1',
                            y=yd, x=xd + 0.3,
                            text = str(xd) + '%',
                            font = dict(family = 'Arial', size=15,
                                      color = 'black'),
                            showarrow = False))

#Construct 3 graph. Percentage of the disorders in the population
fig3 = go.Figure(
    data = [go.Bar(
        x = x,
        y = y,
        marker = dict(
            color = ges_dis.iloc[:, 0:7].values[0], 
            colorscale = 'Blues',
            cmax = 8, 
            cmin = -8,
            line_width = 1.1
        ),
        orientation = 'h',
        hoverinfo = 'skip',
        )
    ],
    layout = dict(
        width = 700,
        height = 500,
        xaxis_showticklabels = False,
	xaxis_fixedrange = True,
	yaxis_fixedrange = True,
        yaxis = dict(
            title = '12 month prevalence worldwide in %',
        ),
        paper_bgcolor = 'white', 
        plot_bgcolor = 'white',
        annotations = annotations,
        margin = dict(
            l = 10, 
            r = 10, 
            t = 80, 
            b = 0
        ),
    )
)


