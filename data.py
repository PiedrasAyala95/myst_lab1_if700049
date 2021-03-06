
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Laboratorio1                                                                               -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: PiedrasAyala95                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/PiedrasAyala95/MyST_LAB1_APA                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
 


import pandas as pd
from os import listdir
from os.path import isfile, join


pd.set_option('display.max_rows', None)                   
pd.set_option('display.max_columns', None)                
pd.set_option('display.width', None)                      
pd.set_option('display.expand_frame_repr', False)         

# -------------------------------------------------------------------------------------------------------------------- PASO 1.1  -- #
 
RUTA = r'C:\Users\Andres\Desktop\Traiding\NAFTRAC_holdings'   #Ruta de donde estan todos los archivos
archivos = [f[8:-4] for f in listdir(RUTA) if isfile(join(RUTA, f))]  #Obtienes todos los numeros de fechas de cada archivo
archivos = ['NAFTRAC_' + i.strftime('%d%m%y') for i in sorted(pd.to_datetime(archivos))] #Agregamos 'NAFTRAC_' con todas las fechas



# -------------------------------------------------------------------------------------------------------------------- PASO 1.2 -- #
#Diccionario
 
data_archivos = {} #Creamos un diccionario vacio

for i in archivos: #Creamos un for donde corre desde i hasta la cantitad total de los archivos
    data = pd.read_csv('C:/Users/Andres/Desktop/Traiding/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None) #importamos archivos
    data.columns = list(data.iloc[0, :]) #Renombramos columnas
    data = data.loc[:, pd.notnull(data.columns)] #Se quito columnas (NAN)
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False) #Reseteamos el index
    data['Precio'] = [i.replace(',', '') for i in data['Precio']] #Se quito las comas en el precio
    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']] #Sequitaron los asteriscos en la columna de ticker
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float} #Cambiamos el tipo de dato a ciertas columnas
    data = data.astype(convert_dict) #Transmite un objeto pandas a un tipo de formato específico
    data['Peso (%)'] = data['Peso (%)']/100 #En la columna de "Peso" lo dividimos entre 100 para dejarlo en el formato deseado 
    data_archivos[i] = data #Lo guardomos en el diccionario
 

#---------------------------------------------------------------------------------------------------------------------- PASO 1.3 -- # 


"""


# estas serviran como etiquetas en dataframe y para yfinance
i_fechas = [i.strftime('%Y-%m-%d') for i in sorted([pd.to_datetime(z[8:]).date() for z in archivos])]
 

#----------------------------------------------------------------------------------------------------------------------- PASO 1.4 -- #
#Descarga de activos y limpieza 


tickers = []  #Creamos una lista vacia

for i in archivos: #Creamos un for donde corre desde i hasta la cantitad total de los archivos
    l_tickers = list(data_archivos[i]['Ticker']) #Hacemos una lista de Ticker de todos los archivos
    [tickers.append(i + '.MX') for i in l_tickers] #Le pegamos el ".MX" a todos los tickes de la lista
global_tickers = np.unique(tickers).tolist() #Creamos una variable donde se guarda los valores unicos de los tickers




# SI EN ESTA PARTE CORREMOS LA DESCARGA DE LOS PRECIOS, ENCONTRAMOS QUE HAY VARIA INFORMACION
# NO SE ENCUENTRA O QUE POSIBLEMNTE HAYA CAMBIADO DE NOMBRE
#inicio = time.time()
#data = yf.download(global_tickers, start="2018-01-31", end="2020-08-21", actions=False,group_by="close", interval='1d', auto_adjust=False, prepost=False, threads=True)




global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers] #Renombramos en todos los archivos 'GFREGIOO.MX' por 'RA.MX'
global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers] #Renombramos en todos los archivos 'MEXCHEM.MX' por 'ORBIA.MX'
global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers] #Renombramos en todos los archivos 'LIVEPOLC.1.MX' por 'LIVEPOLC-1.MX'

[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX','KOFUBL.MX', 'BSMXB.MX']] #Eliminamos varios activos de global tickers
 
#prueba1 = pd.DataFrame(tickers,columns=(['Value']))
#prueba1 = prueba1.groupby('Value')['Value'].count()
 


# -------------------------------------------------------------------------------------------------------------------------- PASO 1.5 -- #
# -- Descargar y acomodar todos los precios historicos


Data_Yahoo = yf.download(global_tickers, start="2018-01-31", end="2020-12-31", actions=False,group_by="close", 
                   interval='1d', auto_adjust=False, prepost=False, threads=True) #Descargamos de yahoo todos los activos que estan en globla tickers
Close= pd.DataFrame({i: Data_Yahoo[i]['Close'] for i in global_tickers}) #Creamos una variable donde agarramos los cierres de todas las acciones
Fechas_list=sorted(list(set(Close.index.astype(str).tolist()) & set(i_fechas))) #Creamos una lista de fechas
Precio_Adj_Close = Close.iloc[[int(np.where(Close.index.astype(str)==i)[0]) for i in Fechas_list]] #Creamos una variable con todos los "Adj_close" de las acciones

precios =  Precio_Adj_Close.reindex(sorted(Precio_Adj_Close.columns), axis=1) #Almacenamos todos los precios
 

# -------------------------------------------------------------------------------------------------------------------------- PASO 1.6 -- #


k = 1000000 #capital inicial
c = 0.00125 # comisiones por transaccion

List_Activos = ['KOFL','KOFUBL', 'BSMXB', 'MXN', 'USD'] #Lista de activos que vamos a quitar 
pasiva_p = {'TIMESTAMP': ['31-01-2018'], 'CAPITAL': [k]} #Creamos una lista con la capital y un timestamp
Datos_Peso = data_archivos[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Peso (%)']] #Agarramos los pesos del archivo "0" (NAFTRAC_310118)
Activos_acti = list(Datos_Peso[Datos_Peso['Ticker'].isin(List_Activos)].index) #Obtemos la lista de los activos que deseamos quitar 
Datos_Peso.drop(Activos_acti, inplace=True) #Quitamos los activos de "Datos_Peso"



# -------------------------------------------------------------------------------------------------------------------------- PASO 1.7 -- #
#Limpieza


Datos_Peso.reset_index(inplace=True, drop=True) #Reseteamos el index y con el "Drop" en true, le decimos que no tome el indice que estaba
Datos_Peso['Ticker'] = Datos_Peso['Ticker'].replace('LIVEPOLC.1','LIVEPOLC-1') #Volvemos a renombrar "LIVERPOL"
Datos_Peso['Ticker'] = Datos_Peso['Ticker'].replace('MEXCHEM','ORBIA') #Volvemos a renombrar "MEXCHEM"
Datos_Peso['Ticker'] = Datos_Peso['Ticker'].replace('GFREGIOO','RA') #Volvemos a renombrar "GFREGIDO"
Datos_Peso['Ticker'] = Datos_Peso['Ticker'] + '.MX' #Volvemos a agregar el ".MX" a nuestro indice de Ticker en la tabla de datos_peso
df_pasiva_Final = Datos_Peso #Creamos una variable donde vamos a tener nuestro pavisa final



# -------------------------------------------------------------------------------------------------------------------------- PASO 1.8 -- #



# -- Obtener posiciones historicas
df_pasiva_Final['TIMESTAMP'] = (Fechas_list[0]) #Agregamos la fecha de inicio de los datos
df_pasiva_Final['PRECIO'] = (np.array([precios.iloc[0, precios.columns.to_list().index(i)] for i in df_pasiva_Final['Ticker']])) #Se creo una nueva columna con los precios, hacemos una union de 2 tablas
df_pasiva_Final['CAPITAL'] = df_pasiva_Final['Peso (%)'] * k - df_pasiva_Final['Peso (%)'] * k * c #Se creo una nueva columna con las operaciones para sacar la capital de cada activo. Capital(dinero que gastaste en activos sin comision)
df_pasiva_Final['TITULOS'] = (df_pasiva_Final['CAPITAL'] // df_pasiva_Final['PRECIO']) #Se creo una columna con las operaciones para sacar los titulos de cada activo
df_pasiva_Final['COMISIONES'] = (df_pasiva_Final['PRECIO'] * c * df_pasiva_Final['TITULOS']) #Se creo una columna con las operaciones para sacar las comisiones
df_pasiva_Final['INVERSION'] = (df_pasiva_Final['PRECIO'] * df_pasiva_Final['TITULOS'] ) #Se creo una columna CON LAS INVERSION 

Dinero = np.round(k - df_pasiva_Final['INVERSION'].sum() - df_pasiva_Final['COMISIONES'].sum()) #Obtenemos la suma del dinero despues de invertir

df_operaciones = pd.DataFrame() #Creamos un dataframe vacio
df_operaciones['TITULOS']= df_pasiva_Final['TITULOS'] #Creamos una columna con los titulos
df_operaciones['PRECIO']= df_pasiva_Final['PRECIO'] #Creamos una columna con los precios
df_operaciones['COMISIONES']= df_pasiva_Final['COMISIONES'] #Creamos una columna con las comisiones
df_operaciones['COMISIONES_ACUM']= df_pasiva_Final['COMISIONES'] #Creamos una columna con las comisiones acum

for i in range(1 ,len(df_operaciones)): #creamos un for donde empezamos desde 1 hasta el tamaño de df_operaciones
    df_operaciones.loc[i,'COMISIONES_ACUM'] = df_operaciones.loc[i,'COMISIONES'] + df_operaciones.loc[i-1,'COMISIONES_ACUM'] #Creamos una columnas y acemos la operacion correspondiente



# -------------------------------------------------------------------------------------------------------------------------- PASO 1.9 -- #


#Lo tenemos que hacer para todos los meses pero ahora no hay comisiones
for i in range(len(sorted(list(set(Fechas_list))))): #Creamos un for que va desde i a un rango,tamañ y orden de la lista de las fechas
    df_pasiva_Final['PRECIO'] = np.array([precios.iloc[i, precios.columns.to_list().index(j)] for j in df_pasiva_Final['Ticker']]) #Nos entrega todos los precios de los activos de la ultima fecha
    df_pasiva_Final['COMISIONES'] = 0 #Toda la columna de comisiones la convertimos en 0 por que no va a tener comisiones
    df_pasiva_Final['INVERSION'] = (df_pasiva_Final['PRECIO'] * df_pasiva_Final['TITULOS']) #Hacemos la nueva operacion de la inversion con los nuevos precios (Ultimos precios)
    pasiva_p['TIMESTAMP'].append(Fechas_list[i]) #Pegamos todas las fechas en la variable anterior
    pasiva_p['CAPITAL'].append(sum(df_pasiva_Final['INVERSION'])+Dinero) #Agregamos en capital los datos correspondientes



df_pasiva = pd.DataFrame() #Creamos una variable con tipo dataframe
df_pasiva['TIMESTAMP'] = pasiva_p['TIMESTAMP'] #Creamos una columna con los datos de TAimestamp
df_pasiva['CAPITAL'] = pasiva_p['CAPITAL'] #Creamos una columna con los datos de la capital 
df_pasiva['REND'] = 0 #Creamos una columna donde vamos a obtener el Rendimiento
df_pasiva['REND_ACUM'] = 0 #Creamos una columna nueva donde vamos a obtener el rendimiento acumulado
df_operaciones['TIMESTAMP'] = pasiva_p['TIMESTAMP'] 
df_operaciones = df_operaciones[['TIMESTAMP','TITULOS','PRECIO','COMISIONES','COMISIONES_ACUM']]




for i in range(1,len(df_pasiva)): #Creamos un for que va de i hasta df_pasiva saltando el primer renglon 
    df_pasiva.loc[i,'REND'] = (df_pasiva.loc[i,'CAPITAL'] - df_pasiva.loc[i-1,'CAPITAL']) / df_pasiva.loc[i-1,'CAPITAL'] #Se va registro x registro haciendo la operacion para rend
    df_pasiva.loc[i,'REND_ACUM'] = df_pasiva.loc[i,'REND'] + df_pasiva.loc[i-1,'REND_ACUM'] #Se va registro x registro haciendo la operacion para rend acum


df_pasiva


# -------------------------------------------------------------------------------------------------------------------------- PASO 1.10 -- #

Plot1=plt.plot(df_pasiva['TIMESTAMP'],df_pasiva['REND']) #Graficamos el rendimiento atraves del tiempo
Plot2=plt.plot(df_pasiva['TIMESTAMP'],df_pasiva['REND_ACUM']) #Graficamos el rendimiento acumulado atraves del tiempo
Plot3=plt.bar(df_pasiva['TIMESTAMP'],df_pasiva['CAPITAL']) #Graficamos el capital atraves del tiempo

"""





 






