from tkinter import *
import sched, time
from tkinter import messagebox
import boto3
from boto3.dynamodb.conditions import Key, Attr
import matplotlib.pyplot as plt
#from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import pandas as pd
from pandas import DataFrame
import threading
stop=False
################################################################################

root = Tk()
root.title('Viriathus')
cb = IntVar()

# time
def tick():
     time_str = time.strftime("%H:%M")
     clock.config(text=time_str)
     clock.after(200,tick)

clock = Label(root, bd=1, relief=SUNKEN, anchor=E)
tick()

################################################################################
# Database
ACCESS_ID = ''  #Removed for security and privacy reasons
ACCESS_KEY = '' #Removed for security and privacy reasons

# connect to database AWS
user=boto3.client("dynamodb", region_name='eu-west-1', aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)
dynamodb=boto3.resource('dynamodb', region_name='eu-west-1', aws_access_key_id=ACCESS_ID, aws_secret_access_key=ACCESS_KEY)
tableDB = dynamodb.Table('SensorData')

def dados():
    response = tableDB.scan()
    data = response['Items']
    while 'ID' in response:
        response=tableDB.query(ScanIndexForward=False, Limit=1)
        ScanIndexForward = True
        data.extend(response['Items'])

    data=sorted(data, key=lambda item: item['ID'], reverse=TRUE)
    return data

def dados1():
    response = tableDB.query(ScanIndexForward=False, Limit=1)
    return response['Items'][-1]

def lambda_handler():
    response = tableDB.query(KeyConditionExpression=Key('ID').eq('1'),ScanIndexForward=False,Limit = 1)
    return response['Items'][-1]


def detect_motion():
    last_read = 0

    response = tableDB.scan()
    data = response['Items']
    while 'ID' in response:
        response = tableDB.query(ScanIndexForward=False, Limit=1)
        ScanIndexForward = True
        data.extend(response['Items'])

    data = sorted(data, key=lambda item: item['ID'], reverse=TRUE)
    last_read = data[0]['ID']
    while(not stop):
        time.sleep(5)
        response=tableDB.scan(FilterExpression= 'ID > :last', ExpressionAttributeValues={':last': last_read})['Items']
        print(response)
        if len(response) > 0:
            last_read = response[-1]['ID']
            for i in range(len(response)):
                pir = response[i]['PIR']
                hall = response[i]['Hall']
                loud = response[i]['Loudness']
                if (hall == 1) or (loud > 1500) or (pir > 15000):
                    onClick()
    return

t1 = threading.Thread(target=detect_motion)

def onClick():
    messagebox.showinfo("Aviso",  "Movimento detetado!")

#ALARME
def alarme():
    data = dados()
    ID = data[0]['ID']
    lista = query_board(ID)
    pir = lista[0]['PIR']
    hall = lista[0]['Hall']
    loud = lista[0]['Loudness']
    if (hall == 1) or (loud > 1500) or (pir > 15000):
        onClick()

def isChecked():
    if cb.get() == 1:
        t1.start()
        btn['state'] = NORMAL
        btn.configure(text='Ligado!')

    elif cb.get() == 0:
        btn['state'] = DISABLED
        btn.configure(text='Desligado!')
        stop=True
    else:
        messagebox.showerror('PythonGuides', 'Something went wrong!')

def query_board(id, dynamodb=None):
    response_query = tableDB.query(KeyConditionExpression=Key('ID').eq(id))
    return response_query['Items']

################################################################################


def graph_loudness():
    data=dados()
    ID0 = data[0]['ID']; ID1 = data[1]['ID']; ID2 = data[2]['ID']; ID3 = data[3]['ID']; ID4 = data[4]['ID']
    lista0 = query_board(ID0); lista1 = query_board(ID1); lista2 = query_board(ID2);lista3 = query_board(ID3);lista4 = query_board(ID4)
    loud0 = lista0[0]['Loudness']; loud1 = lista1[0]['Loudness']; loud2 = lista2[0]['Loudness']; loud3 = lista3[0]['Loudness']; loud4 = lista4[0]['Loudness']
    temp0 = lista0[0]['Timestamp']; temp1 = lista1[0]['Timestamp']; temp2 = lista2[0]['Timestamp']; temp3 = lista3[0]['Timestamp']; temp4 = lista4[0]['Timestamp']
    data = {'Tempo': [temp0,temp1,temp2,temp3,temp4],
            'Ruído': [loud0, loud1, loud2, loud3, loud4]}

    df = DataFrame(data, columns=['Tempo','Ruído'])
    # Convert DataFrame columns to int
    df['Tempo'] = df['Tempo'].astype(int)
    df['Ruído'] = df['Ruído'].astype(int)



    figure1 = plt.Figure(figsize=(5, 4), dpi=100)
    ax1 = figure1.add_subplot(111)
    bar1 = FigureCanvasTkAgg(figure1, root)
    bar1.get_tk_widget().grid(row=5, column=1, columnspan=5, rowspan=100)
    df = df[['Tempo','Ruído']].groupby('Tempo').sum()
    df.plot(kind='bar', legend=True, ax=ax1)
    #ax1.set_title('Ruído')

def graph_pir():
    data = dados()
    ID0 = data[0]['ID']; ID1 = data[1]['ID']; ID2 = data[2]['ID']; ID3 = data[3]['ID']; ID4 = data[4]['ID']
    lista0 = query_board(ID0); lista1 = query_board(ID1); lista2 = query_board(ID2); lista3 = query_board(ID3); lista4 = query_board(ID4)
    loud0 = lista0[0]['PIR']; loud1 = lista1[0]['PIR']; loud2 = lista2[0]['PIR']; loud3 = lista3[0]['PIR'];  loud4 = lista4[0]['PIR']
    temp0 = lista0[0]['Timestamp']; temp1 = lista1[0]['Timestamp']; temp2 = lista2[0]['Timestamp']; temp3 = lista3[0]['Timestamp']; temp4 = lista4[0]['Timestamp']
    data = {'Tempo': [temp0, temp1, temp2, temp3, temp4],
            'Movimento': [loud0, loud1, loud2, loud3, loud4]}

    df = DataFrame(data, columns=['Tempo', 'Movimento'])
    # Convert DataFrame columns to int
    df['Tempo'] = df['Tempo'].astype(int)
    df['Movimento'] = df['Movimento'].astype(int)
    #print(df)

    figure1 = plt.Figure(figsize=(5, 4), dpi=100)
    ax1 = figure1.add_subplot(111)
    bar1 = FigureCanvasTkAgg(figure1, root)
    bar1.get_tk_widget().grid(row=5, column=1, columnspan=5, rowspan=100)
    df = df[['Tempo','Movimento']].groupby('Tempo').sum()
    df.plot(kind='bar', legend=True, ax=ax1)
    #ax1.set_title('Movimento')

def graph_hall():
    data = dados()
    ID0 = data[0]['ID'];    ID1 = data[1]['ID'];    ID2 = data[2]['ID'];    ID3 = data[3]['ID'];    ID4 = data[4]['ID']
    lista0 = query_board(ID0);    lista1 = query_board(ID1);    lista2 = query_board(ID2);    lista3 = query_board(ID3);    lista4 = query_board(ID4)
    loud0 = lista0[0]['Hall'];    loud1 = lista1[0]['Hall'];    loud2 = lista2[0]['Hall'];    loud3 = lista3[0]['Hall'];    loud4 = lista4[0]['Hall']
    temp0 = lista0[0]['Timestamp'];    temp1 = lista1[0]['Timestamp'];    temp2 = lista2[0]['Timestamp'];    temp3 = lista3[0]['Timestamp'];    temp4 = lista4[0]['Timestamp']
    data = {'Tempo': [temp0, temp1, temp2, temp3, temp4],
            'Presença': [loud0, loud1, loud2, loud3, loud4]}

    df = DataFrame(data, columns=['Tempo', 'Presença'])
    # Convert DataFrame columns to int
    df['Tempo'] = df['Tempo'].astype(int)
    df['Presença'] = df['Presença'].astype(int)
    #print(df)

    figure1 = plt.Figure(figsize=(5, 4), dpi=100)
    ax1 = figure1.add_subplot(111)
    bar1 = FigureCanvasTkAgg(figure1, root)
    bar1.get_tk_widget().grid(row=5, column=1, columnspan=5, rowspan=100)
    df = df[['Tempo', 'Presença']].groupby('Tempo').sum()
    df.plot(kind='bar', legend=True, ax=ax1)
    #ax1.set_title('Presença')

################################################################################
check1 = Checkbutton(root, text="Alarme",font=("Verdana 11 bold"), variable=cb, onvalue=1, offvalue=0, command=isChecked)
btn = Button(root, text='Desligado!', state=DISABLED, padx=20, pady=5)
button2 = Button(root, text="Ruído", command=lambda:graph_loudness(), width=20)
button3 = Button(root, text="Movimento", command=lambda:graph_pir(), width=20)
button4 = Button(root, text="Presença", command=lambda:graph_hall(), width=20)
################################################################################
check1.grid(row=0,column=2,sticky=N,padx=0, pady=0)
btn.grid(row=1,column=2,sticky=NS,padx=5, pady=5)
texto = Label(root, text = "Última atividade", font="Verdana 11 bold",relief= 'groove').place(x = 180, y = 80)
button2.grid(row=3, column=1, padx=5, pady=40)
button3.grid(row=3, column=2, padx=5, pady=40)
button4.grid(row=3, column=3, padx=5, pady=40)
clock.grid(row=101, column=0, columnspan=10, sticky=W+E)



root.mainloop()
