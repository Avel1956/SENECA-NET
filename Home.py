from networkx.generators import community
import streamlit as st
import streamlit.components.v1 as components
import itertools
import pandas as pd
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from networkx.readwrite.json_graph.node_link import node_link_data
from pyvis.network import Network


# Leer el archivo (CSV)
df_interact = pd.read_csv('PRODUCTOS_CLEAN29_06_2022.csv')

# Título de la página 
with st.sidebar:
    st.title('Visualización de la red de colaboración de la Alianza SÉNECA')

# Lista opciones de red
redsel = ('Red de autores', 'Red de grupos', 'Red de instituciones')

# Lista opciones de tipo de producto
prodsel = ( 'Todos', 'ARTICULO A1', 'ARTICULO A2', 'ARTICULO B', 'ARTICULO C', 
'CAPITULO DE LIBRO A1', 'CAPITULO DE LIBRO B', 'PONENCIA')

# Selectbox con las redes posibles
with st.sidebar:
    atributos_selec = st.selectbox('Seleccione red a visualizar', redsel)

autores_encabezados = ['Autor 1',  'Autor 2', 'Autor 3', 'Autor 4', 'Autor 5', 'Autor 6', 'Autor 7',
    'Autor 8', 'Autor 9', 'Autor 10', 'Autor 11', 'Autor 12', 'Autor 13', 'Autor 14']
instituciones_encabezados = ['Inst Autor 1', 'Inst Autor 2', 'Inst Autor 3', 'Inst Autor 4', 'Inst Autor 5', 'Inst Autor 6',
 'Inst Autor 7', 'Inst Autor 8', 'Inst Autor 9', 'Inst Autor 10', 'Inst Autor 11', 'Inst Autor 12', 'Inst Autor 13', 'Inst Autor 14']
grupos_encabezados = ['Grupo Autor 1', 'Grupo Autor 2', 'Grupo Autor 3', 'Grupo Autor 4', 'Grupo Autor 5', 'Grupo Autor 6', 'Grupo Autor 7',
'Grupo Autor 8', 'Grupo Autor 9', 'Grupo Autor 10', 'Grupo Autor 11', 'Grupo Autor 12', 'Grupo Autor 13', 'Grupo Autor 14']

# Selectbox tipo de producto
with st.sidebar:
    prod_sel = st.selectbox('Seleccione el tipo de producto de colaboración', prodsel)

# establecer la red a representar
if len(atributos_selec) == 0:
    with st.sidebar:
        st.text('Seleccione al menos una red para comenzar')



if atributos_selec == 'Red de autores':
    encabezados = autores_encabezados
elif atributos_selec == 'Red de grupos':
    encabezados = grupos_encabezados
else:
    if atributos_selec == 'Red de instituciones':
        encabezados = instituciones_encabezados
periodo =10
with st.sidebar:
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

# Lógica para la creación de la red de acuerdo al tipo de producto

if prod_sel == 'Todos':
    dfinal = df_interact
else:
    dfinal = df_interact.loc[lambda df: df['SUBPRODUCTO'] == prod_sel, :]
    dfinal =dfinal.reset_index()   

if len(dfinal)< 1:
    st.error("La configuración seleccionada no contiene suficentes datos para crear la red")
#Creacion de todas las redes de articulos y consolidacion en una sola
allnetlist = []

# Lógica para creación de la red seleccionada  
i=0
while i<dfinal.shape[0]:
    allnetlist.append(artnet(encabezados, dfinal, i, periodo))
    i=i+1

totalnet=nx.compose_all(allnetlist) 
totalnodes =pd.DataFrame(list(totalnet.nodes))
# totalnodes.to_csv('output\\nodes.csv')
dftotalnet = nx.to_pandas_edgelist(totalnet)
# dftotalnet.to_csv('output\\net.csv')

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#funcion para cambiar el color de los nodos

def sel_prop(net, name):
     #vector inicial seleccion
    #nx.set_edge_attributes(net, '#8E9F7D1', "color"  )
    nx.set_node_attributes(net, 0, "sel")
    #vector inicial de colores
    nx.set_node_attributes(net, 'white', "color")
    #Aplicacion del valor de seleccion al nodo seleccionado
    net.nodes[name]["sel"] = 1
    #Aplicacion de color al nodo (y los bordes conectados a este)
    net.nodes[name]["color"] = '#B2F227'
         
           
    
    return net
#Creación de caja de selección 

with st.sidebar:
    name = st.selectbox(
     'Seleccione el nodo principal ',
     list(totalnet.nodes()))
color_net = sel_prop(totalnet, name) 
nx.write_graphml_lxml(color_net, "output\\net.graphml")
#Creación de caja de selección del nodo 2 
with st.sidebar:
    name_target = st.selectbox(
     'Seleccione el nodo objetivo ',
     list(totalnet.nodes()))
color_net = sel_prop(totalnet, name) 
nx.write_graphml_lxml(color_net, "output\\net.graphml")

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Cálculo de métricas de la red
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Centralidad (degree)
#diccionario de los grados de cada nodo
dict_grado= dict(color_net.degree(color_net.nodes()))
#aplicar atributo de grado a los nodos
nx.set_node_attributes(color_net, dict_grado, 'grado')
#Mostrar centralidad del nodo seleccionado
med_cent = nx.betweenness_centrality(color_net)
eig_cent = nx.eigenvector_centrality(color_net)

#Asignacion como atributo de cada nodo
nx.set_node_attributes(color_net, med_cent, 'betweenness')
nx.set_node_attributes(color_net, eig_cent, 'eigenvector')

#Diccionario de métricas de nodo seleccionado 
node_metrics = {'Nodo': [name], 
'Grado': [color_net.nodes[name]['grado']],
'Centralidad de mediacion':[color_net.nodes[name]['betweenness']],
'Centralidad de eigenvector': [color_net.nodes[name]['eigenvector']]
}
#Dataframe a partir del diccionario de métricas para representación  
node_metrics_df = pd.DataFrame(data = node_metrics)
#--------------------------------
#Camino más corto entre nodos (shortest path) 
try:
    camino_mas_corto = nx.shortest_path(color_net, source = name, target = name_target)
except:
    camino_mas_corto = "No existe un camino entre los nodos seleccionados"

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#Estadísticas de red 
dens_red = nx.density(color_net)

#esta completamente conectada
esta_conectada = nx.is_connected(color_net)

#cuales son los componentes de la red
no_componentes = nx.number_connected_components(color_net)
componentes = nx.connected_components(color_net)

#Cual es el componente mas grande

componente_mayor = max(componentes, key = len)


#Detección de comunidades 
comunidades = greedy_modularity_communities(totalnet)
# Diccionario de métricas de la red
red_metrics = { 'Tipo red': [atributos_selec],
'densidad': [dens_red],
'Está completamente conectada': [esta_conectada],
'Cuantas subredes': [no_componentes]} 
#Dataframe de métricas de la red para representación  
red_metrics_df = pd.DataFrame(data = red_metrics)
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# inicialización del objeto pyvis
autores_net = Network(height='600px',
                       width='100%',
                       bgcolor='#020202',
                       
                       font_color='white'
                      )

# Convertir la red de networkx en red pyvis
autores_net.from_nx(color_net)
#opciones de visualizacion
autores_net.repulsion(node_distance=420,
                        central_gravity=0.33,
                        spring_length=110,
                        spring_strength=0.10,
                        damping=0.95
                       )


# guardar y leer el grafico como HTML (Streamlit Sharing)
autores_net.save_graph('output\\htmlgraph.html')
HtmlFile = open('output\\htmlgraph.html', 'r', encoding='utf-8')

# Cargar el archivo HTML en un componente HTML en Streamlit
components.html(HtmlFile.read(), height=600)
 
col1, col2 = st.columns(2)
with col1:
    st.metric(label = "Nodos", value= len(totalnodes) )
with col2:
    st.metric(label = 'Conexiones', value = len(dftotalnet))
st.header("Métricas principales del nodo seleccionado")
st.dataframe(node_metrics_df)
st.header("Métricas de la red")
st.dataframe(red_metrics)
#Mostrar la lista de nodos que conforman el camino más corto entre 
# los nodos seleccionados 
st.write("Camino más corto entre los nodos seleccionados es")

st.write(camino_mas_corto)


# Pie de pagina
st.markdown(
    """
    <br>
    <h6><a href="https://github.com/Avel1956/SENECA-NET" target="_blank">GitHub Repo</a></h6>
    <h6><a href="https://www.udea.edu.co/wps/portal/udea/web/inicio/investigacion/seneca" target="_blank">SÉNECA</a></h6>
    <h6>*Aviso*: Esta aplicación está aún en desarrollo, si observa algún error, por favor contactar a jaime.velezz@udea.edu.co</h6>
    """, unsafe_allow_html=True
    )