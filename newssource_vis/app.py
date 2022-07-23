from dash import Dash, dcc, html, Input, Output
import os
import pandas
import plotly.express as px
import json


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# description
markdown_desc = '''
### What?

This page shows the 3D visualization of how news sources are represented in the vector space, 
based on how they are shared on various subreddits. We can see that some *similar* news sources 
are closer together, suggesting that perhaps we could use the information of how news sources are 
shared on various subreddits to characterize news sources, by inferring their labels from 
the news sources that are close in their neighborhoods.

(Here I will talk about the different meanings of *similar*)

### How?

The steps to create this visualization:
1. Represent news sources using the statistics of how they are shared in various subreddits (e.g. sharing frequency, upvote ratio, number of comments).
2. Employ Principal Component Analysis (PCA) to reduce the dimension of news source representations.
3. Utilize t-SNE to project down to 3D to visualize
4. Use Dash to create this webpage

### Why?

This webpage is created as part of the deliverable of Junita's honor thesis in the 
Computer Science department. For the complete thesis, visit this link.
'''

app.layout = html.Div([
    html.H1(
        children='News Sources Vector Visualizations',
        style={
            'textAlign': 'center'
        }),
    html.Label('Similarity Criterion'),
    dcc.RadioItems(
        options={
            'reliability' : 'Reliability',
            'country' : 'Country',
            'political_leaning' : 'Political leaning',
            'media_type' : 'Media type'
        },
        value='reliability',
        id='similarity-type',
        inline=True,
        inputStyle={'margin-left':'100px'}),
    html.Br(),
    dcc.Graph(id="tsne-graph",
    style={'width': '90vw', 'height': '90vh'}),
    html.Br(),
    dcc.Markdown(children=markdown_desc)
], style={'marginBottom': 50, 'marginTop': 50, 'marginLeft': 50, 'marginRight': 50})

# ======================== preparing data ==============================
tsne_3d = json.load(open("tsne_wow.json", "r", encoding="utf-8"))

ns_fixed = json.load(open("ns_fixed_wow.json", "r", encoding="utf-8"))
reliability = json.load(open("reliability.json", "r", encoding="utf-8"))
political_leaning = json.load(open("political_leaning.json", "r", encoding="utf-8"))
media_type = json.load(open("media_type_current.json", "r", encoding="utf-8"))
country = json.load(open("country.json", "r", encoding="utf-8"))

xt = [k[0] for k in tsne_3d]
yt = [k[1] for k in tsne_3d]
zt = [k[2] for k in tsne_3d]

reliability_colors = []
for k in ns_fixed:
    if k not in reliability:
        reliability_colors.append("(unknown)")
    elif reliability[k] == "reliable":
        reliability_colors.append("reliable")
    elif reliability[k] == "unreliable":
        reliability_colors.append("unreliable")

political_leaning_colors = []
for k in ns_fixed:
    if k not in political_leaning:
        political_leaning_colors.append("(unknown)")
    else:
        political_leaning_colors.append(political_leaning[k])

media_type_colors = []
for k in ns_fixed:
    if media_type[k] == '':
        media_type_colors.append("(unknown)")
    else:
        media_type_colors.append(media_type[k])

country_colors = []
for k in ns_fixed:
    if country[k] == '':
        country_colors.append("(unknown)")
    else:
        country_colors.append(country[k])

df = pandas.DataFrame({"pc1": xt,
                   "pc2": yt,
                   "pc3": zt,
                   "source": ns_fixed,
                   "reliability": reliability_colors,
                   "political_leaning": political_leaning_colors,
                   "media_type": media_type_colors,
                   "country": country_colors})

# ==================================================================================

@app.callback(
    Output(component_id='tsne-graph', component_property='figure'),
    Input(component_id='similarity-type', component_property='value'))
def update_figure(similarity):
    fig = px.scatter_3d(df, x='pc1', y='pc2', z='pc3',
                    color=similarity,
                    hover_name='source', opacity=0.4,
                    labels = ns_fixed,
                    title="Colored based on " + similarity)

    fig.update_traces(marker_size = 3)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)