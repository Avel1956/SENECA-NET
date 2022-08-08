import os.path
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
import matplotlib.pyplot as plt
# from googleapiclient.discovery import build
import numpy as np
import pandas as pd
# import seaborn as sns
# import spacy
import os
import csv
import datetime
import json
import time











def open_csv (filename):
#Esta funcion tiene como entrada el nombre de un archivo en el workpath con formato 
#.csv y devuelve un dataframe con los contenidos del archivo con los 
#contenidos de la primera fila como encabezados.
    df = pd.read_csv (filename)
    return df


 
def col_perc_nan(df, percentaje):
    # Muestra el numero de celdas por columna con datos faltantes   
    total_files = df.shape[0]
    num_dat_falt = df.isnull().sum() 
    print("El resumen del número de celdas con NAN:\n" + str(num_dat_falt))


    cutoff_percentage = percentaje
    a = (cutoff_percentage * total_files)/100
    nan_cell_by_column = num_dat_falt[num_dat_falt > a]


    descending = nan_cell_by_column.sort_values(ascending=False)

    plt.figure(figsize= (16,6))
    plt.title("Dimensiones vs #Nan")
    sns.barplot(descending.index, descending.values) 
    plt.show() 

def toke_vect(df, column_header):
    #Esta funcion toma un dataframe, tokeniza la columna requerido (column_header) en el (df) y
    #retorna una lista con los textos vectorizados
    nlp = spacy.load('en_core_web_lg')
    with nlp.disable_pipes():
        vectors_abstract = np.array([nlp(df[column_header]).vector for idx, df in df.iterrows()])
    return vectors_abstract


def write_csv(data):
    today = datetime.datetime.today().strftime("%d-%m-%Y-%S")

    if not os.path.exists("xplore_query"):

        os.makedirs("xplore_query")

    xplore_query = open("xplore_query/"+today+"-xquery.csv", "a+")

    

    writer = csv.writer(xplore_query)

    datos = data

    xplore_query.write("\n".join(datos))

    print("Hashtags written to file.")

    xplore_query.close()

def write_json(data):
    #Esta función guarda localmente un archivo json con la informacion de
    #data
    today = datetime.datetime.today().strftime("%d-%m-%Y-%H-%M-%S")

    if not os.path.exists("xplore_query"):

        os.makedirs("xplore_query")

    with open("xplore_query/"+today+"-xquery.json", 'w', encoding='utf-8') as xplore_query:

        json.dump(data, xplore_query)

    

    

    print("JSON guardado.")

    xplore_query.close() 