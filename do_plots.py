#!/usr/bin/env python

import json

import numpy as np

import datetime as dt

import matplotlib.pyplot as plt


from ipyleaflet import Map, GeoJSON, basemaps, basemap_to_tiles

from IPython.core.display import display

import ipywidgets as widgets

from ipywidgets import interact, interactive, fixed, interact_manual

from utils import extract_roi_data_ndre

BANDS = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 
         'B8A', 'B11', 'B12', 'CLD']
FIELDS = ['01 - Hoosfield',
 '02 - Bones_Colose',
 '03 - Delafield',
 '04 - None',
 '05 - Fosters_Corner',
 '06 - Furze',
 '07 - Great_Knott_1',
 '08 - Great_Knott_2',
 '09 - Little_Hoos',
 '10 - Little_Knott',
 '11 - Long_Hoos_2',
 '12 - Long_Hoos_4',
 '13 - Long_Hoos_5',
 '14 - Long_Hoos_6-7',
 '15 - Pastures',
 '16 - Sawyers_2',
 '17 - Sawyers_3',
 '18 - Sawyers_4',
 '19 - Summerdells_1',
 '20 - Summerdells_2',
 '21 - West_Barnfield_1-2',
 '22 - Whitehorse_1',
 '23 - Whitehorse_2',
 '24 - Whitlocks',
 '25 - None',
 '26 - None',
 '27 - None',
 '28 - Blackhorse',
 '29 - Bylands',
 '30 - Drapers',
 '31 - Flint',
 '32 - Meadow',
 '33 - Osier',
 '34 - Scout',
 '35 - Ver',
 '36 - Webbs',
 '37 - None',
 '38 - None',
 '39 - Delharding',
 '40 - None',
 '41 - Great_Harpenden_1',
 '42 - None',
 '43 - ELA',
 '44 - None',
 '45 - None',
 '46 - Highfield_7-8-9',
 '47 - None',
 '48 - New_Zealand',
 '49 - None',
 '50 - Stackyard',
 '51 - None',
 '52 - Weighbridge',
 '53 - None',
 '54 - Great_Harpenden_2',
 '55 - Highfield_5-6',
 '56 - Claycroft',
 '57 - Great_Knott_3',
 '58 - Sawyers_1',
 '59 - Long_Hoos_3',
 '60 - None']


def field_analysis(field_id, img_db, b0i, b1i, cld_thresh=20):
    
    b0 = BANDS.index(b0i)
    b1 = BANDS.index(b1i)
    field_no = FIELDS.index(field_id) + 1
    field_name = field_id
    roi_file = f"carto/Field_{field_no:02d}.geojson"
    with open(roi_file, 'r') as f:
        loc_data = json.load(f)

    m = Map(center=(51.81, -0.37), zoom=14, )
    geo_json = GeoJSON(data=loc_data, 
                    style = {'color': 'red', 'opacity':1, 'weight':1.9,
                             'fillOpacity':0.1})
    m.add_layer(geo_json)

    display(m)

    analysis_data =  extract_roi_data_ndre(img_db,b0=b0, b1=b1, 
                                           cld_thresh=cld_thresh,
                                           roi=roi_file)
    n_acqs = len(analysis_data)
    n_rows = int(np.floor(np.sqrt(n_acqs)))
    n_cols = n_rows -1
    n_plots = n_cols*n_rows
    while  n_plots < n_acqs:
        n_cols = n_cols + 1
        n_plots = n_cols*n_rows
    
    fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, sharex=True,
                            sharey=True, figsize=(18,18))
    axs = axs.flatten()
    cmap=plt.cm.viridis
    cmap.set_bad("0.3")
    for ii, (k,v) in enumerate(analysis_data.items()):
        im =axs[ii].imshow(v, interpolation="nearest", vmin=0.1, vmax=0.8, )
        axs[ii].set_title(k.strftime("%d %b %Y"), fontsize=7)
        axs[ii].set_xticks([])
        axs[ii].set_yticks([])
    fig.tight_layout()
    fig.colorbar(im, ax=axs.tolist(), orientation="horizontal", pad=0.01)
    fig.savefig(f"time_series1_{field_name:s}.png", dpi=142, bbox_inches="tight")
    data = []
    doys = []
    tx = []
    for ii, (k,v) in enumerate(analysis_data.items()):
        tx.append(k)
        doys.append(int(k.strftime("%j")))
        mask = np.isfinite(v.flatten())
        data.append(v.flatten()[mask])
    isort = np.argsort(tx)
    doys = [doys[i] for i in isort]
    tx = [tx[i] for i in isort]
    data = [data[i] for i in isort]
    plt.figure(figsize=(17,8))    
    bp = plt.boxplot(data, positions=doys, notch=True, widths=2,
                     meanline=True, patch_artist=True, labels=tx)
    _ = plt.xticks(rotation="vertical")
    _ = plt.ylim([0, 1])
    _ = [patch.set_facecolor("#8DA0CB") for patch in bp['boxes']]
    plt.tight_layout()
    fig.savefig(f"time_series2_{field_name:s}.png", dpi=142, bbox_inches="tight")
    print("-->Saved plots under "
          f"time_series1_{field_name:s}.png" 
          f"time_series2_{field_name:s}.png")
    
def interactive_field_analysis(img_db):
    return interact_manual(field_analysis, field_id=widgets.Dropdown(options=FIELDS),
                           img_db=fixed(img_db),
                           b0i=widgets.Dropdown(options=BANDS,
                           value='B04'),
                           b1i=widgets.Dropdown(options=BANDS,
                           value='B08'),
                           cld_thresh=widgets.IntSlider(min=5, max=90, value=60))