# sivtools.py
# !/usr/bin/env python3
"""Library for providing a simple API into data science tools

Available functions:
- calendar_plot_by_year
- map_points
"""

__version__ = '0.01'
__author__ = 'Aly Sivji'

import matplotlib.pyplot as plt
import calmap
import folium
from folium import plugins
import pandas as pd

def calendar_plot_by_year(series_to_plot, normalize_each_year=False):
    """Creates a calendar heatmap of of data contained in a Series

    Arg:
        series_to_plot: Pandas Series object [index = dates]
        normalize_each_year: Boolean flag to separately color each year
    """

    # calculate number of years
    start_year = series_to_plot.sort_index().index[0].year
    end_year = series_to_plot.sort_index().index[-1].year
    num_years = end_year - start_year + 1

    # send directly to function if we want to few heatmap across full time period
    if not normalize_each_year:
        calmap.calendarplot(series_to_plot, cmap='YlGn', fillcolor='grey', \
            linewidth=.05, daylabels=['M', 'T', 'W', 'T', 'F', 'S', 'S'], \
            fig_kws=dict(figsize=(12, 2*num_years)))
        return

    # plot each year and build figure
    fig = plt.figure(figsize=(12, 2*num_years))
    for i, year in enumerate(range(start_year, end_year + 1), 1):
        year_to_plot = series_to_plot[series_to_plot.index.year == year]

        # plot
        axes = fig.add_subplot(num_years, 1, i)
        calmap.yearplot(year_to_plot, year=year, cmap='YlGn', fillcolor='grey', linewidth=.05, \
                        daylabels=['M', 'T', 'W', 'T', 'F', 'S', 'S'], ax=axes)
        axes.set_ylabel(year)


def map_points(df, lat_col='latitude', lon_col='longitude', zoom_start=11, \
                plot_points=False, pt_radius=15, \
                draw_heatmap=False, heat_map_weights_col=None, \
                heat_map_weights_normalize=True, heat_map_radius=15):
    """Creates a map given a dataframe of points. Can also produce a heatmap overlay

    Arg:
        df: dataframe containing points to maps
        lat_col: Column containing latitude (string)
        lon_col: Column containing longitude (string)
        zoom_start: Integer representing the initial zoom of the map
        plot_points: Add points to map (boolean)
        pt_radius: Size of each point
        draw_heatmap: Add heatmap to map (boolean)
        heat_map_weights_col: Column containing heatmap weights
        heat_map_weights_normalize: Normalize heatmap weights (boolean)
        heat_map_radius: Size of heatmap point

    Returns:
        folium map object
    """

    ## center map in the middle of points center in
    middle_lat = df[lat_col].median()
    middle_lon = df[lon_col].median()

    curr_map = folium.Map(location=[middle_lat, middle_lon],
                          zoom_start=zoom_start)

    # add points to map
    if plot_points:
        for _, row in df.iterrows():
            folium.CircleMarker([row[lat_col], row[lon_col]],
                                radius=pt_radius,
                                popup=row['name'],
                                fill_color="#3db7e4", # divvy color
                               ).add_to(curr_map)

    # add heatmap
    if draw_heatmap:
        # convert to (n, 2) or (n, 3) matrix format
        if heat_map_weights_col is None:
            cols_to_pull = [lat_col, lon_col]
        else:
            # if we have to normalize
            if heat_map_weights_normalize:
                df[heat_map_weights_col] = \
                    df[heat_map_weights_col] / df[heat_map_weights_col].sum()

            cols_to_pull = [lat_col, lon_col, heat_map_weights_col]

        stations = df[cols_to_pull].as_matrix()
        curr_map.add_children(plugins.HeatMap(stations, radius=heat_map_radius))

    return curr_map
