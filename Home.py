from networkx.generators import community
import streamlit as st
import streamlit.components.v1 as components
import itertools
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from networkx.readwrite.json_graph.node_link import node_link_data
from pyvis.network import Network

# Read dataset (CSV)
df_interact = pd.read_csv('PRODUCTOS_CLEAN29_06_2022.csv')

# Set header title
st.title('Visualización de la red de colaboración de la Alianza SÉNECA')

# Define list of selection options and sort alphabetically
redsel = ('Red de autores', 'Red de grupos', 'Red de instituciones')


# Selectbox con las redes posibles
atributos_selec = st.selectbox('Seleccione red a visualizar', redsel)
autores_encabezados = ['Autor 1',  'Autor 2', 'Autor 3', 'Autor 4', 'Autor 5', 'Autor 6', 'Autor 7',
    'Autor 8', 'Autor 9', 'Autor 10', 'Autor 11', 'Autor 12', 'Autor 13', 'Autor 14']
instituciones_encabezados = ['Inst Autor 1', 'Inst Autor 2', 'Inst Autor 3', 'Inst Autor 4', 'Inst Autor 5', 'Inst Autor 6',
 'Inst Autor 7', 'Inst Autor 8', 'Inst Autor 9', 'Inst Autor 10', 'Inst Autor 11', 'Inst Autor 12', 'Inst Autor 13', 'Inst Autor 14']
grupos_encabezados = ['Grupo Autor 1', 'Grupo Autor 2', 'Grupo Autor 3', 'Grupo Autor 4', 'Grupo Autor 5', 'Grupo Autor 6', 'Grupo Autor 7',
'Grupo Autor 8', 'Grupo Autor 9', 'Grupo Autor 10', 'Grupo Autor 11', 'Grupo Autor 12', 'Grupo Autor 13', 'Grupo Autor 14']

# establecer la red a representar
if len(atributos_selec) == 0:
    st.text('Seleccione al menos una red para comenzar')

if atributos_selec == 'Red de autores':
    encabezados = autores_encabezados
elif atributos_selec == 'Red de grupos':
     encabezados = grupos_encabezados
else:
    if atributos_selec == 'Red de instituciones':
        encabezados = instituciones_encabezados
periodo =10    
periodo = st.slider('Seleccione el rango de periodos a consultar', 2, 10, 10)

#Funcion que devuelve una red de cada articulo
def artnet(encabezados, df, i, p):
    
    

    actores = df[encabezados]
    listactores = actores.loc[i,:].values.tolist()
    listalimpia = [x for x in listactores if str(x)!= 'nan']
    bordes = list(itertools.combinations(listalimpia, 2))
    dfnet = pd.DataFrame(bordes, columns = ['source', 'target'])
    dfnet['periodo'] = df['Informe de reporte'].loc[i]
    dfnet['titulo'] = df['titulo'].loc[i]
    pernet =dfnet.loc[(dfnet['periodo']< p)] 
    
    senet = nx.from_pandas_edgelist(pernet, edge_attr=True)
    nx.set_node_attributes(senet, p, "periodo")
    nx.set_edge_attributes(senet, df['titulo'].iloc[i], "titulo")
    
    return senet


#Creacion de todas las redes de articulos y consolidacion en una sola
allnetlist = []

i=0
while i<df_interact.shape[0]:
    allnetlist.append(artnet(encabezados, df_interact, i, periodo))
    i=i+1

totalnet=nx.compose_all(allnetlist) 
totalnodes =pd.DataFrame(list(totalnet.nodes))
# totalnodes.to_csv('output\\nodes.csv')
dftotalnet = nx.to_pandas_edgelist(totalnet)
# dftotalnet.to_csv('output\\net.csv') 
nx.write_graphml_lxml(totalnet, "output\\net.graphml")



    
  
    # Initiate PyVis network object
autores_net = Network(height='600px',
                       width='100%',
                       bgcolor='#222222',
                       font_color='white'
                      )

    # Take Networkx graph and translate it to a PyVis graph format
autores_net.from_nx(totalnet)

    # Generate network with specific layout settings
autores_net.repulsion(node_distance=420,
                        central_gravity=0.33,
                        spring_length=110,
                        spring_strength=0.10,
                        damping=0.95
                       )

    # Save and read graph as HTML file (on Streamlit Sharing)
autores_net.save_graph('output\\htmlgraph.html')
HtmlFile = open('output\\htmlgraph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
components.html(HtmlFile.read(), height=600)
 
dens_red = nx.density(totalnet)
esta_conectada = nx.is_connected(totalnet)
componentes = nx.connected_components(totalnet)
comunidades = greedy_modularity_communities(totalnet)
st.metric(label = "Número de nodos", value= len(totalnodes) )
st.metric(label = 'Numero de productos', value = len(dftotalnet))
# Footer
st.markdown(
    """
    <br>
    <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
    <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
    <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
    """, unsafe_allow_html=True
    )