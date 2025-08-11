# Import relevant libraries
import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go

nav_df = pd.read_csv("data/nav.csv")
derivatives_df = pd.read_csv("data/derivatives.csv")
assets_df = pd.read_csv("data/assets.csv")
strategy_df = pd.read_csv("data/investmentstrategy.csv")
geo_df = pd.read_csv("data/geo.csv")

# Extract unique values
unique_fund_types = nav_df['FundType'].dropna().unique()
unique_countries = nav_df['Country'].dropna().unique()

# Dash setup
external_stylesheets = [
    "assets/base.css",
    "assets/bootstrap.min.css",
    "assets/dashboard.css"
]

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "Investment Fund Statistics"

app.layout = html.Div(id="react-entry-point", children=[
    html.Div(id="jur-modal", children=[
        html.Div(className="header_wrapper", children=[
            html.Div(className="header_content", children=[
                html.Div(className="header_logo", style={"display": "flex", "alignItems": "center"}, children=[
                    html.Img(src="assets/logo.png", style={"width": "100px", "marginRight": "12px"}),
                    html.H1("Investment Fund Statistics", style={"margin": "0", "font-weight": "600", "fontSize": "30px"})
                ]),
                html.Div(className="header_dropdown", children=[
                    html.Div(className="h_year_drop", children=[
                        html.P("Year"),
                        dcc.Dropdown(id="year_dropdown", options=[{"label": "2024", "value": "2024"}],
                                     value="2024", className="dash-dropdown")
                    ]),
                    html.Div(className="h_fund_drop", children=[
                        html.P("Fund Type"),
                        dcc.Dropdown(id="fund_dropdown", options=[{"label": ft, "value": ft} for ft in unique_fund_types],
                                     value=unique_fund_types[0], className="dash-dropdown")
                    ]),
                    html.Div(className="h_jur_drop", children=[
                        html.P("Jurisdiction", id="jur_dropdown_head"),
                        dcc.Dropdown(id="country_dropdown",
                                     options=[{"label": c, "value": c} for c in unique_countries],
                                     value=unique_countries[0], className="dash-dropdown")
                    ])
                ]),
                html.Div(className="header_button_div", children=[
                    html.Button("Regional", id="region_button", className="button-l"),
                    html.Button("Jurisdictional", id="jur_button", className="button-r")
                ])
            ])
        ]),
        html.Div(className="content_wrapper", children=[
            html.Div(className="market_list", children=[
                html.Div(className="market_list_item", children=[
                    html.Div(className="market_data_head", children=[
                        html.H5(id="fund_p")
                    ]),
                    html.Div(className="market_data_boxes", children=[
                        html.Div(className="market_data_box", children=[
                            html.H5(id="tot_nav"),
                            html.P("Total NAV")
                        ]),
                        html.Div(className="market_data_box", children=[
                            html.H5(id="tot_funds"),
                            html.P("Total Funds")
                        ])
                    ]),
                    html.Div(className="market_data_alt left-b", children=[
                        html.P(id="jurisdictions_reporting")
                    ])
                ]),
                html.Div(className="market_list_item", children=[
                    html.Div(className="jur_data_head", children=[html.H5(id="country_head")]),
                    html.Div(className="jur_data_boxes", children=[
                        html.Div(className="jur_data_box", children=[
                            html.H5(id="country_nav"),
                            html.P(id="country_pct_nav")
                        ]),
                        html.Div(className="jur_data_box", children=[
                            html.H5(id="country_funds"),
                            html.P(id="country_pct_funds")
                        ]),
                        html.Div(className="jur_data_box", children=[
                            html.H5(id="lev_1"),
                            html.Span([html.P("Gross Leverage"), html.I("(incl. IR and FX Derivatives)")])
                        ]),
                        html.Div(className="jur_data_box", children=[
                            html.H5(id="lev_2"),
                            html.Span([html.P("Gross Leverage"), html.I("(excl. IR and FX Derivatives)")])
                        ]),
                        html.Div(className="jur_data_box", children=[
                            html.H5(id="lev_3"),
                            html.P("Synthetic Leverage")
                        ])
                    ]),
                    html.Div(className="jur_data_alt", children=[html.P(id="reg_jur_count")])
                ])
            ]),
            html.Div(className="graph_list", children=[
                html.Div(className="graph_list_item", children=[
                    html.Div(id="graph_1_fig", className="dash-graph graph_col_1", children=[
                        dcc.Graph(id="derivatives_graph")
                        ])
                    ]),

                html.Div(className="graph_list_item", children=[
                    html.Div(id="graph_2_fig", className="dash-graph graph_col_2", children=[
                       dcc.Graph(id="geo_graph", config={"scrollZoom": True, "displayModeBar": True},
                                )
                        ])
                ]),
                html.Div(className="graph_list_item", children=[
                    html.Div(id="graph_3_fig", className="dash-graph graph_col_3", children=[
                        dcc.Graph(id="assets_graph")
                        ])
                ]),
                html.Div(className="graph_list_item", children=[
                    html.Div(id="graph_4_fig", className="dash-graph graph_col_4", children=[
                        dcc.Graph(id="strategy_graph")
                        ])
                ])
            ])
        ])
    ])
])

@app.callback(
    Output("fund_p", "children"),
    Output("jurisdictions_reporting", "children"),
    Output("tot_nav", "children"),
    Output("tot_funds", "children"),
    Output("country_head", "children"),
    Output("country_nav", "children"),
    Output("country_pct_nav", "children"),
    Output("country_funds", "children"),
    Output("country_pct_funds", "children"),
    Output("lev_1", "children"),
    Output("lev_2", "children"),
    Output("lev_3", "children"),
    Input("fund_dropdown", "value"),
    Input("country_dropdown", "value")
)

def update_metrics(fund_type, country):
    filtered = nav_df[nav_df["FundType"] == fund_type]
    country_df = filtered[filtered["Country"] == country]

    total_nav = filtered["NAV"].sum()
    total_funds = filtered["No."].sum()
    country_nav = country_df["NAV"].sum()
    country_funds = country_df["No."].sum()

    pct_nav = f"{(country_nav / total_nav * 100):.1f}%" if total_nav else "0%"
    pct_funds = f"{(country_funds / total_funds * 100):.1f}%" if total_funds else "0%"

    lev1 = f"{country_df['GrossLeverage(incl)'].mean():.2f}x NAV" if not country_df.empty else "0.0x NAV"
    lev2 = f"{country_df['GrossLeverage(excl)'].mean():.2f}x NAV" if not country_df.empty else "0.0x NAV"
    lev3 = f"{country_df['SyntheicLeverage'].mean():.2f}x NAV" if not country_df.empty else "0.0x NAV"

    name_map = {
        "Hedge Funds": "All QHFs*",
        "Open Ended Funds": "All OEFs*",
        "Close Ended Funds": "All CEFs*"
    }

    return (
        name_map.get(fund_type, ""),
        f"* For {filtered['Country'].nunique()} Reporting Jurisdictions",
        f"USD {total_nav:.1f}T",
        f"{int(total_funds):,} Funds",
        country,
        f"USD {country_nav:.1f}T",
        f"{pct_nav} of Total Nav",
        f"{int(country_funds)} Funds",
        f"{pct_funds} of Total Funds",
        lev1,
        lev2,
        lev3
    )


@app.callback(
    Output("derivatives_graph", "figure"),
    Input("country_dropdown", "value")
)
def update_derivatives_graph(selected_country):
    df = derivatives_df[derivatives_df["Country"] == selected_country].sort_values(by="Derivative", ascending=True)

    if df.empty:
        return {
            "data": [],
            "layout": {
                "title": f"No Derivatives data for {selected_country}",
                "paper_bgcolor": "#e5ecf6",
                "plot_bgcolor": "#e5ecf6"
            }
        }

    import plotly.express as px

    fig = px.bar(
        df,
        x="Derivative",
        y="GrossNotionalExposure",
        labels={"GrossNotionalExposure": "Gross Notional Exposure (in USD Trillions)"},
        title="Derivatives",
        color="Derivative",
        color_discrete_sequence=["#b8c1e7", "#4e63c2", "#8291d3", "#273261", "#374587"]
    )

    fig.update_layout(
        title={
            "text": "Derivatives",
            "x": 0.5,
            "xanchor": "center",
            "pad": {"t": 20, "b": 10, "l": 5, "r": 5},
            "font": {"size": 18, "family": "Arial", "color": "#273261"}
        },
        showlegend=False,
        height=350,
        xaxis_title=None,
        yaxis_title="Gross Notional Exposure (in USD)",
        yaxis_tickformat=".1f",
        plot_bgcolor="#e5ecf6",
        paper_bgcolor="#f0f3f5"
    )
    fig.update_layout(margin=dict(t=40, b=20, l=20, r=20))
    fig.update_layout(yaxis_title_font=dict(size=12))
    fig.update_layout(
    xaxis=dict(tickfont=dict(size=12)),
    yaxis=dict(tickfont=dict(size=12))
    )
    return fig

@app.callback(
    Output("assets_graph", "figure"),
    Input("country_dropdown", "value")
)
def update_assets_graph(selected_country):
    df = assets_df[assets_df["Country"] == selected_country]

    if df.empty:
        return {
            "data": [],
            "layout": {
                "title": f"No Asset data for {selected_country}",
                "paper_bgcolor": "#f0f3f5",
                "plot_bgcolor": "#f0f3f5"
            }
        }

    # Optional: Define custom order if you want fixed sorting
    asset_order = [
        "CIU", "Cash", "Commodities", "Conv. Bonds", "Corp. Bonds", "Digital Assets", "L. EQ",
        "Loans", "Muni./Oth. Pub. Local Debt", "Other", "Oth. Asset Classes",
        "Real Estate", "Repo", "Sov. Bonds", "Str./Sec. Products", "UL EQ"
    ]
    df["Asset"] = pd.Categorical(df["Asset"], categories=asset_order, ordered=True)
    df = df.sort_values("Asset")

    fig = px.bar(
        df,
        x="Asset",
        y="GrossExposure",
        labels={"Gross Exposure": "Gross Exposure (in USD)"},
        title="Assets",
        color="Asset",
        color_discrete_sequence=["#000032", "#7485cf", "#cdd2e2",  "#8291d3", "#374587", "#b08ce8", "#65409b", "#482e70", "#905cdf", "#4dadaa", "#00615f", "#004644", "#008b87", "#ffeb87"]
    )

    fig.update_layout(
        title={"text": "Assets", "x": 0.5},
        showlegend=False,
        height=350,
        xaxis_title=None,
        yaxis_title="Gross Exposure (in USD)",
        yaxis_tickformat=".1f",
        plot_bgcolor="#e5ecf6",
        paper_bgcolor="#f0f3f5",
        margin=dict(t=40, b=40, l=40, r=40),
        xaxis_tickangle=-45,
        xaxis=dict(tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12), title_font=dict(size=12))
    )

    return fig


@app.callback(
    Output("strategy_graph", "figure"),
    Input("country_dropdown", "value")
)
def update_strategy_graph(selected_country):
    df = strategy_df[strategy_df["Country"] == selected_country]

    if df.empty:
        return {
            "data": [],
            "layout": {
                "title": f"No strategy data for {selected_country}",
                "paper_bgcolor": "#f0f3f5",
                "plot_bgcolor": "#f0f3f5"
            }
        }

    df = df.groupby("Strategy", as_index=False)["Net Assets (USD)"].sum()
    df["Percent"] = df["Net Assets (USD)"] / df["Net Assets (USD)"].sum() * 100

    fig = px.pie(
        df,
        names="Strategy",
        values="Net Assets (USD)",
        title="Investment Strategy",
        color_discrete_sequence=["#000032","#273261","#4e63c2","#7485cf","#b8c1e7","#cdd2e2","#d6c2ec","#905cdf","#b08ce8","#65409b","#8ac4bb","#4dadaa","#00615f","#004644","#008b87","#ffeb87"]
        
    )

    fig.update_traces(
        textinfo="percent",
        hole=0.3,
        textposition="inside",
        insidetextorientation="radial"
    )

    fig.update_layout(
        title={"x": 0.5, "font": {"size": 18, "family": "Arial", "color": "#273261"}},
        height=350,
        paper_bgcolor="#f0f3f5",
        plot_bgcolor="#e5ecf6",
        margin=dict(t=40, b=40, l=20, r=20),
        legend=dict(
            font=dict(size=11),
            orientation="v",
            yanchor="middle",
            y=0.5,
            x=1.05,
            xanchor="left"
        )
    )

    return fig


@app.callback(
    Output("geo_graph", "figure"),
    Input("country_dropdown", "value") 
)
def update_geo_graph(selected_country):
    df = geo_df[geo_df["Country"] == selected_country]
    df["Perc"] = df["Amounts"] / df["Amounts"].sum()
    df["Text"] = df["Label"].replace({"World": "Global"}) + ": " + (df["Perc"] * 100).round(1).astype(str) + "%"

    # Manual coordinates for label placement
    coord_map = {
        "North America": {"lat": 40, "lon": -100},
        "Europe": {"lat": 54, "lon": 15},
        "Asia": {"lat": 30, "lon": 95},
        "South America": {"lat": -15, "lon": -60},
        "World": {"lat": 25, "lon": -45},  # "World" becomes "Global"
        "Africa": {"lat": 5, "lon": 25}
    }

    fig = go.Figure()

    # ✅ Choropleth layer (optional - shown only if valid country names present)
    valid_locations = df["Investment Area"].dropna().tolist()
    if all(isinstance(x, str) and x.lower() not in ["world", "global", "asia", "europe", "north america", "south america", "africa"] for x in valid_locations):
        fig.add_trace(go.Choropleth(
            locationmode='country names',
            locations=df["Investment Area"],
            z=df["Perc"],
            colorscale="Purples",
            showscale=False,
            marker_line_color='white',
            zmin=0,
            zmax=1
        ))

    # (A) invisible markers that carry hover info
    fig.add_trace(go.Scattergeo(
        lon=[coord_map[r]["lon"] for r in order],
        lat=[coord_map[r]["lat"] for r in order],
        mode="markers",
        marker=dict(size=24, opacity=0),  # invisible but easy to hover
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"          # Region label
            "Share: %{customdata[1]:.1f}%<br>"     # Percent
            "Amount: %{customdata[2]:,.0f} USD<extra></extra>"
        ),
        customdata=list(
            zip(
                df["Label"].replace({"World": "Global"}),
                (df["Amounts"] / df["Amounts"].sum() * 100),
                df["Amounts"],
            )
        ),
        showlegend=False,
    ))

    # (B) your visible text labels on top
    fig.add_trace(go.Scattergeo(
        lon=[coord_map[r]["lon"] for r in order],
        lat=[coord_map[r]["lat"] for r in order],
        mode="text",
        text=df["Label"].replace({"World": "Global"}) + ": " +
             (df["Amounts"] / df["Amounts"].sum() * 100).round(1).astype(str) + "%",
        textfont=dict(size=16),
        hoverinfo="skip",   # hover comes from the markers above
        showlegend=False,
    ))

    
    # ✅ Text annotation layer
    fig.add_trace(go.Scattergeo(
        lon=[coord_map[region]["lon"] for region in coord_map],
        lat=[coord_map[region]["lat"] for region in coord_map],
        mode="text",
        showlegend=False,
        text=df["Text"],
        textfont=dict(
            color="black",
            size=12
        )
    ))

    # ✅ Final map layout
    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showframe=False,
            showcoastlines=True,
            landcolor="white",
            bgcolor="#e5ecf6"
        ),
        paper_bgcolor="#f7f7f7",
        margin=dict(t=40, b=10, l=0, r=0),
        title=dict(
            text="Geographical Investment Areas of Large Hedge Funds",
            x=0.5
        ),
        height=350
    )
    fig.update_layout(uirevision="geo")  # preserves pan/zoom across dropdown changes


    return fig



if __name__ == '__main__':
    app.run(debug=False)
