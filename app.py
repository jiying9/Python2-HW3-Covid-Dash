import os
import pathlib
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_counties.csv"))
)
df_lat_lon["FIPS "] = df_lat_lon["FIPS "].apply(lambda x: str(x).zfill(5))

df_full_data = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "us_counties_covid19_daily.csv")
    )
)

df_full_data['mounth']=df_full_data['date'].apply(lambda x:str(x).split("/")[1])



df_full_data=df_full_data.groupby([df_full_data['mounth'],df_full_data['county']],as_index=False).max()

df_full_data["County"] = (
    df_full_data["county"] + ", " + df_full_data.state.map(str)
)

df_full_data=df_full_data.dropna()
df_full_data["County Code"] = df_full_data["fips"].apply(
    lambda x: str(int(x)).zfill(5)
)


MOUNTHS = range(1,13)
#set legend
BINS = [
    "0",
    "1-500",
    "501-1000",
    "1001-1500",
    "1501-2200",
    "2201-3000",
    "3001-4000",
    "4001-5000",
    "5001-6000",
    "6001-7000",
    "7001-8000",
    "8001-9000",
    "9001-10000",
    "10001-11500",
    "11500-13000",
    "-13001",
]
def map_bins(x):
    if x==0:
        return "0"
    elif x in range(1,500):
        return "1-500"
    elif x in range(501,1000):
        return "501-1000"
    elif x in range(1001,1500):
        return "1001-1500"
    elif x in range(1501,2200):
        return "1501-2200"
    elif x in range(2201,3000):
        return "2201-3000"
    elif x in range(3001,4000):
        return "3001-4000"
    elif x in range(4001,5000):
        return "4001-5000"
    elif x in range(5001,6000):
        return "5001-6000"
    elif x in range(6001,7000):
        return "6001-7000"
    elif x in range(7001,8000):
        return "7001-8000"
    elif x in range(8001,9000):
        return "8001-9000"
    elif x in range(9001,10000):
        return "9001-10000"
    elif x in range(10001,11500):
        return "10001-11500"
    elif x in range(11500,13000):
        return "11500-13000"
    elif x >=13001:
        return "-13001"

df_full_data["bins"] = df_full_data["cases"].apply(
    lambda x: map_bins(x)
)

DEFAULT_COLORSCALE = [
    "#ffffff",
    "#fee1d0",
    "#fdc3a1",
    "#fca572",
    "#fb8743",
    "#fa6914",
    "#f94ae5",
    "#f82cb6",
    "#f70e87",
    "#f5f058",
    "#f4d229",
    "#f3b3fa",
    "#f295cb",
    "#f1779c",
    "#f0596d",
    "#ef3b36",
]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Number of Novel Corona Virus 2019 cases in USA"),
                html.P(
                    id="description",
                    children="Coronaviruses are a large family of viruses which may cause illness in animals or humans. In humans, several coronaviruses are known to "+\
                    "cause respiratory infections ranging from the common cold to more severe diseases such as Middle East Respiratory Syndrome (MERS) and Severe Acute Respiratory Syndrome (SARS). The most recently discovered coronavirus causes coronavirus disease COVID-19 - World Health Organization "+\
                    "The number of new cases are increasing day by day around the world. This dataset has information from 50 US states and the District of Columbia at daily level.",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(MOUNTHS),
                                    max=max(MOUNTHS),
                                    value=min(MOUNTHS),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in MOUNTHS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of age adjusted mortality rates \
                            from poisonings in year {0}".format(
                                        min(MOUNTHS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Histogram of total number of deaths (single mounth)",
                                    "value": "show_absolute_deaths_single_mounth",
                                },
                                {
                                    "label": "Absolute cases per mounth",
                                    "value": "Absolute_cases_per_mounth",
                                }
                            ],
                            value="Absolute_cases_per_mounth",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

#using call back function for map
@app.callback(
    Output("county-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(year, figure):
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))

    data = [
        dict(
            lat=df_lat_lon["Latitude "],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Number of infected people<br>per county per mounth</b>",
            font=dict(color="#1B9CFC"),
            bgcolor="#1f2630",
            x=0.95,
            y=0.95,
        )
    ]

    for i, bin in enumerate(reversed(BINS)):
        color = cm[bin]
        annotations.append(
            dict(
                arrowcolor=color,
                text=bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#1f2630",
                font=dict(color="#1B9CFC"),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    base_url = "https://raw.githubusercontent.com/lometheus/us_mapbox/master/"
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base_url + str(year) + "/" + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            # CHANGE THIS
            fill=dict(outlinecolor="#afafaf"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Heatmap of counties covid19 daily in mounth {0}".format(
        year
    )


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, year):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#1B9CFC"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    pts = selectedData["points"]
    fips = [str(pt["text"].split("<br>")[-1]) for pt in pts]
    for i in range(len(fips)):
        if len(fips[i]) == 4:
            fips[i] = "0" + fips[i]
    dff = df_full_data[df_full_data["County Code"].isin(fips)]


    dff["Age Adjusted Rate"] = dff["cases"]

    if chart_dropdown != "death_rate_all_time":
        title = "Absolute cases per mounth, <b>{0}</b>".format(year)
        AGGREGATE_BY = "cases"
        dff = dff[dff.mounth == str(year)]
        if "show_absolute_deaths_single_mounth" == chart_dropdown:
            dff = dff[dff.mounth == str(year)]
            AGGREGATE_BY = "deaths"
            title = "Absolute deaths per mounth, <b>{0}</b>".format(year)

        dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
        deaths_or_rate_by_fips = dff.groupby("County")[AGGREGATE_BY].sum()
        deaths_or_rate_by_fips = deaths_or_rate_by_fips.sort_values()
        # Only look at non-zero rows:
        deaths_or_rate_by_fips = deaths_or_rate_by_fips[deaths_or_rate_by_fips > 0]
        fig = deaths_or_rate_by_fips.iplot(
            kind="bar", y=AGGREGATE_BY, title=title, asFigure=True
        )

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = deaths_or_rate_by_fips.values.tolist()
        fig_data[0]["marker"]["color"] = "#1B9CFC"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#1B9CFC"
        fig_layout["title"]["font"]["color"] = "#1B9CFC"
        fig_layout["xaxis"]["tickfont"]["color"] = "#1B9CFC"
        fig_layout["yaxis"]["tickfont"]["color"] = "#1B9CFC"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig

    fig = dff.iplot(
        kind="area",
        x="Year",
        y="Age Adjusted Rate",
        text="County",
        categories="County",
        colors=[
            "#1b9e77",
            "#d95f02",
            "#7570b3",
            "#e7298a",
            "#66a61e",
            "#e6ab02",
            "#a6761d",
            "#666666",
            "#1b9e77",
        ],
        vline=[year],
        asFigure=True,
    )

    for i, trace in enumerate(fig["data"]):
        trace["mode"] = "lines+markers"
        trace["marker"]["size"] = 4
        trace["marker"]["line"]["width"] = 1
        trace["type"] = "scatter"
        for prop in trace:
            fig["data"][i][prop] = trace[prop]

    # Only show first 500 lines
    fig["data"] = fig["data"][0:500]

    fig_layout = fig["layout"]

    fig_layout["yaxis"]["title"] = "Age-adjusted death rate per county per year"
    fig_layout["xaxis"]["title"] = ""
    fig_layout["yaxis"]["fixedrange"] = True
    fig_layout["xaxis"]["fixedrange"] = False
    fig_layout["hovermode"] = "closest"
    fig_layout["title"] = "<b>{0}</b> counties selected".format(len(fips))
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#1f2630"
    fig_layout["plot_bgcolor"] = "#1f2630"
    fig_layout["font"]["color"] = "#1B9CFC"
    fig_layout["xaxis"]["tickfont"]["color"] = "#1B9CFC"
    fig_layout["yaxis"]["tickfont"]["color"] = "#1B9CFC"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"

    if len(fips) > 500:
        fig["layout"][
            "title"
        ] = "Age-adjusted death rate per county per year <br>(only 1st 500 shown)"

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
