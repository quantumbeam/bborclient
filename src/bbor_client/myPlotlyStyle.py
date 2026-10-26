import plotly.graph_objects as go
import plotly.io as pio

axisStyle = dict(
    showline=False,
    linecolor='grey',
    linewidth=0.5,
    ticks='inside',
    ticklen = 8,
    tickmode='auto',
    tickcolor='grey',
    tickwidth=1.1,
    tickfont=dict(size=14,
                  color='grey'),
    minor=dict(ticks='inside',
               ticklen=4,
               tickcolor='grey'),
    gridcolor='whitesmoke',
    gridwidth=0.1,
    zeroline=True,
    zerolinecolor='whitesmoke',
    zerolinewidth=0.1,
    title_font=dict(size=18,
                   color='grey',),
    )
markerStyle = dict(
    color = 'royalblue',
    colorscale = [[0, 'royalblue'], [1, 'orange']],
    size=8,
    line=dict(
        width=1,
        color='DarkSlateGrey',
        colorscale = [[0, 'DarkSlateGrey'], [1, 'darkorange']],
    )
)
errorStyle = dict(
    color='darkgrey',
    thickness=0.5,
    width=3.0,
)
titleStyle = dict(
    yref='container',
    xanchor='center',
    x=0.5
)
legendStyle = dict(
        bordercolor='lightgrey',
        borderwidth=1.0,
        font=dict(size=14, color='grey')
    )
layout = dict(
    xaxis = axisStyle,
    yaxis = axisStyle,
    title = titleStyle,
    showlegend = True,
    legend = legendStyle,
    font_family = 'メイリオ',
    margin=dict(l=80, r=0, b=50, t=50, pad=0),
    plot_bgcolor='white',
    shapes = [dict(
        name='rect',#必須
        type='rect',
        xref='paper', yref='paper',
        x0=0, y0=0,
        x1=1, y1=1,
        line=dict(width=0.5,color='black'),
        )],
    )
pio.templates["mystyle"] = go.layout.Template(
    layout = layout,
    data = dict(scatter = [
        go.Scatter(marker=markerStyle, error_y = errorStyle)
    ])
)
