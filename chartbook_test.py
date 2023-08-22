import pandas as pd
import numpy as np

from PIL import Image

import plotly.graph_objects as go

OUTPUT_PNG = False

periods = {
    'Q': 4,
    'M': 12,
    'W': 52,
}

yaxis_titles = {
    'YOY': "YoY %Ch",
    'NONE': "Level",
}


generic_layout = dict(
    autosize=True,
    # width=640,
    # height=480,
    margin={'l': 10, 'r': 15, 't': 40},
    paper_bgcolor="white",
    # plot_bgcolor="white",
    showlegend=False,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    xaxis={
        'ticks': 'inside',
        'showgrid': True,            # thin lines in the background
        'zeroline': False,           # thick line at x=0
        'visible': True,             # numbers below
        'showline': True,            # Show X-Axis
        'linecolor': 'black',        # Color of X-axis
        'tickfont_color': 'black',   # Color of ticks
        'showticklabels': True,      # Show X labels
        'mirror': True,              # draw right axis
    },
    yaxis={
        'ticks': 'inside',
        'showgrid': True,            # thin lines in the background
        'zeroline': False,           # thick line at x=0
        'visible': True,             # numbers below
        'showline': True,            # Show X-Axis
        'linecolor': 'black',        # Color of X-axis
        'tickfont_color': 'black',   # Color of ticks
        'showticklabels': True,      # Show X labels
        'side': 'left',
        'mirror': True,
    },
)


def do_transform(**kwargs):
    """given a dataframe, apply transforms like yoy"""
    df = kwargs['df']
    indicator = kwargs.setdefault('indicator', "")
    transform = kwargs.setdefault('transform', 'NONE')
    freq = kwargs.setdefault('freq', 'M')

    col = "%s_%s_%s" % (indicator, freq, transform)
    df = df.set_index(df.index.astype("period[%s]" % freq).to_timestamp(freq=freq))
    if transform == 'NONE':
        df[col] = df[df.columns[0]]

    if transform == 'YOY':
        if freq == 'D':
            # offset 1 year, prev business day if not business day
            df['date_1y'] = df.index - pd.offsets.DateOffset(years=1) + pd.offsets.Day() - pd.offsets.BDay()
            # get previous val
            df['prev_1y'] = df.apply(lambda x: df.loc[x.date_1y][indicator] if x.date_1y in df.index else np.nan,
                                     axis='columns')
            # any NAs, get previous row
            df['prev_1y'] = df['prev_1y'].ffill(axis=0)
            df[col] = df[indicator] / df['prev_1y'] * 100 - 100
        else:
            df[col] = df[indicator].pct_change(periods=periods[freq], freq=freq) * 100
    df = df.dropna()

    retdict = kwargs
    retdict['col'] = col
    retdict['yaxis_title'] = yaxis_titles[transform]
    retdict['df'] = df

    return retdict


def chart_generic(df=None,
                  col=None,
                  title=None,
                  xaxis_title=None,
                  yaxis_title=None,
                  recessions=False,
                  output_png=OUTPUT_PNG,
                  **kwargs
                  ):

    fig = go.Figure(
        data=[go.Scatter(y=df[col],
                         x=df.index.to_list(),
                         line_width=2,
                         # color_discrete_sequence=plotly.colors.qualitative.Dark24
                         ),
              ],
        layout=generic_layout)

    fig.update_layout(dict(title=title,
                           xaxis_title=xaxis_title,
                           yaxis_title=yaxis_title,
                           ))
    if output_png:
        fig.write_image("images/%s.png" % col)
        return Image.open("images/%s.png" % col)
    else:
        return fig
