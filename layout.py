#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 13:32:58 2020

@author: julianbons
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from style import *

sidebar = html.Div(
    [
        html.H2('Mental Disorders', 
                className='display-4'),
        html.Hr(),
        html.P(
            'Click to learn more', 
            className='lead'
        ),
        dbc.Nav(
            [
                dbc.NavLink('Start Page', href='/page-1', id='page-1-link'),
                dbc.NavLink('By year', href='/page-2', id='page-2-link'),
                dbc.NavLink('By sex', href='/page-3', id='page-3-link'),
                dbc.NavLink('By Disorder', href='/page-4', id='page-4-link'),
            ],
            vertical = True,
            pills = True,
        ),
    ],
    style = SIDEBAR_STYLE,
)
        
content = html.Div(id='page-content', style=CONTENT_STYLE)

footer = html.Div(
    [
        html.Footer("Source: Ritchie, H. & Roser, M.(2020). Mental Health. Published online at OurWorldInData.org.\
                                Retrieved from: 'https://ourworldindata.org/mental-health' [Online Resource]",
                    style = {'fontSize': 13}, id = 'source'),
    ],
    style = FOOTER_STYLE
)


        