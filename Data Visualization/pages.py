#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 13:36:23 2020

@author: julianbons
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from figures import *

page1 = html.Div([
    html.H1('Welcome', style = {'fontSize' : 50, 'text-align': 'center', 'font_family': 'Arial'}),
    html.Br(),
    html.P('Mental disorders are among the most common causes of disability. \
            They cause significant distress, impair personal functioning and can reduce life quality.\
            In this widget, I display some informations about mental disorders. \
            For further information and the sources, click on the the link below.', 
           style = {'fontSize': 20, 'text-align': 'center'}),
    html.Br(),
    dcc.Link('Click here to learn more', href='https://ourworldindata.org/mental-health', target='_blank',
             style = {'display':'flex', 'justifyContent':'center'})
], style={'marginTop': 250})

page2 = dbc.Container([
        dcc.Store(id='store'),
        dbc.Row(
            [
                dbc.Col([
                    html.H2('One in seven',  style={'marginBottom':0, 'fontSize':50, 'text-align': 'center'}),
                    html.H5('people suffer from mental disorders', style={'marginTop':0.1, 'marginBottom':10, 'text-align': 'center'}),
                    html.P('Over the last couple of years, this prevalence remained almost constant.', style = {'text-align': 'center'})
                ], style = {'marginTop': 50},
                    md=4),
                dbc.Col([
                    dcc.Graph(id='mental_disorders_over_time', figure=fig1, config={'displayModeBar': False, 'scrollZoom': False})
                ],
                    md=8),
            ])
        ]
 
)    

page3 = dbc.Container([
        dcc.Store(id='store'),
        dbc.Row(
            [
                dbc.Col([
                    html.H2(str(int(year[year['Year'] == 2016]['total']))[:3] + ' million',  style={'marginBottom':0.01, 'fontSize':50, 'text-align': 'center'}),
                    html.H5('cases in 2016', style={'marginTop':0.01, 'marginBottom': 20, 'text-align': 'center'}),
                    html.P('Women are slightly more often affected than men.', style = {'text-align': 'center'})
                ], style = {'marginTop': 200},
                    md = 4),
                dbc.Col([
                    dcc.Graph(id='mental_disorders_over_time', figure=fig2, config={'displayModeBar': False, 'scrollZoom': False})
                ],
                    md = 8),
            ])
        ]
 
)  
                
                
page4 = dbc.Container([
        dcc.Store(id='store'),
        dbc.Row(
            [
                dbc.Col([
                    html.H2('Taxonomy', style={'marginBottom':0.01, 'fontSize':50, 'text-align': 'center'}),
                    html.H5('of mental disorders', style={'marginBottom': 10, 'text-align': 'center'}),
                    html.P('The ICD-10 differentiates 10 groups of mental and behavioral disorders. \
                            Most common are anxiety disorders and depression.', style={'text-align': 'center'})
                ], style = {'marginTop': 350},
                    md = 4),
                dbc.Col([
                    dcc.Graph(id='mental_disorder_by_disorder', figure=fig3, config={'displayModeBar': False, 'scrollZoom': False})
                ],
                    md = 8),
            ])
])                 
                
                
                
                
                
                
                
                
                
                
                
                
                