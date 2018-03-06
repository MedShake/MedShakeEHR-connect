#!/usr/bin/env python3
##
# This file is part of MedShakeEHR.
#
# Copyright (c) 2017
# fr33z00 <https://github.com/fr33z00>
# http://www.medshake.net
#
# MedShakeEHR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# MedShakeEHR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MedShakeEHR.  If not, see <http://www.gnu.org/licenses/>.
#
##

##
# Connect: Saisir une mesure et l'envoyer dans le dossier patient
#
# @author fr33z00 <https://github.com/fr33z00>
##

import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.ttk as tkttk
import tkinter.messagebox as tkmb
import serial
import serial.tools.list_ports
import requests
import configparser
import os
import threading
import base64
import datetime

principale = tk.Tk()
principale.title('MedShakeEHR-connect')
principale['bg']='white'

def read_from_port(s):
    while (s.is_open):
      try:
        nb = s.inWaiting()
        if (nb > 0):
          entree['state']='normal'
          entree.insert('insert', s.read(nb).decode('ascii'))
          entree['state']='disabled'
      except:
        False

def stop():
  sp.close()
  thread.join()
  boutonSend['state']='normal'
  boutonGet['text']="Acquérir"
  boutonGet['command']=get

def get():
  global thread
  boutonGet['text']="Stop"
  boutonGet['command']=stop
  worklist = requests.get(config['SERVEUR']['adresse']+ "/rest/getPatientInfo/", auth=(selecteduser.get(), selectedpassword.get())).json()
  patient = worklist["patient"]["3"]+" "+worklist["patient"]["2"]+" "+worklist["patient"]["1"]+"\n"
  entree['state']='normal'
  entree.delete('1.0', 'end')
  entree.insert('insert', patient)
  for i in range(1, len(patient)):
    entree.insert('insert', "=")
  entree.insert('insert', "\n")
  entree['state']='disabled'
  bitstab={'7':serial.SEVENBITS, '8':serial.EIGHTBITS}
  paritetab={'Aucune':serial.PARITY_NONE, 'Paire':serial.PARITY_EVEN, 'Impaire':serial.PARITY_ODD}
  stoptab={'1':serial.STOPBITS_ONE, '1.5': serial.STOPBITS_ONE_POINT_FIVE, '2': serial.STOPBITS_TWO}
  sp.port=selectedport.get()
  sp.baudrate=int(selectedbauds.get())
  sp.bytesize=bitstab[selectedbits.get()]
  sp.parity=paritetab[selectedparite.get()]
  sp.stopbits=stoptab[selectedstop.get()]
  try:
    sp.open()
    thread = threading.Thread(target=read_from_port, args=(sp,))
    thread.start()
  except:
    if (sp.is_open == False):
      tkmb.showinfo("Erreur", "Le port séléctionné n'a pas pu être ouvert")
    entree['state']='normal'
    entree.delete('1.0', 'end')
    entree['state']='disabled'
    boutonGet['text']="Acquérir"
    boutonGet['command']=get

def send():
  requests.post(config['SERVEUR']['adresse']+ "/rest/uploadNewDoc/?timestamp="+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'&title='+selectedtitre.get()+'&filename='+selectedtitre.get()+'.txt', auth=(selecteduser.get(), selectedpassword.get()), data=bytes(entree.get('1.0', 'end'), 'utf-8'))
  boutonSend['state']='disabled'

def save():
  config['GENERAL']={'titres' :  selectedtitres.get()}
  config['SERVEUR']={'adresse' :  selectedadresse.get(), 'user' : selecteduser.get(), 'password' : str(base64.b64encode(bytes(selectedpassword.get(), "utf-8")), 'utf-8')}
  config['PORTSERIE']={'port' :  selectedport.get(), 'bauds' : selectedbauds.get(), 'bits' : selectedbits.get(), 'parite' : selectedparite.get(), 'stop': selectedstop.get()}
  with open(os.path.expanduser('~/MedShakeEHR-connect.ini'), 'w') as configfile:
    config.write(configfile)
  configuration.withdraw()
  
def configure():
  configuration.deiconify()

def quitconfig():
  configuration.withdraw()
  readconfig()

def readconfig():
  if config.read(os.path.expanduser('~/MedShakeEHR-connect.ini')):
    configuration.withdraw()
    if 'GENERAL' in config:
      selectedtitres.set(config['GENERAL']['titres'])
    if 'SERVEUR' in config:
      selectedadresse.set(config['SERVEUR']['adresse'])
      selecteduser.set(config['SERVEUR']['user'])
      selectedpassword.set(str(base64.b64decode(config['SERVEUR']['password']), 'utf-8'))
    if 'PORTSERIE' in config:
      selecteurport.set(config['PORTSERIE']['port'])
      selecteurbauds.set(config['PORTSERIE']['bauds'])
      selecteurbits.set(config['PORTSERIE']['bits'])
      selecteurparite.set(config['PORTSERIE']['parite'])
      selecteurstop.set(config['PORTSERIE']['stop'])

###################################
# fenêtre de configuration
configuration = tk.Toplevel(principale)
configuration.transient(principale)
configuration.title('Configuration')
configuration.attributes("-topmost", True)
configuration.wm_protocol("WM_DELETE_WINDOW", quitconfig)
configuration['bg']='white'
# frame Général
frameG = tk.LabelFrame(configuration, borderwidth=2, text='Général', relief='groove', background='white')
frameG.pack(padx=10, pady=5)
selectedtitres = tk.StringVar()
labeltitres = tk.Label(frameG, background='white', text="Titres (séparés par virgules)")
labeltitres.pack(anchor='w', padx=5, pady=5)
inputtitres = tk.Entry(frameG, textvariable=selectedtitres, width=30)
inputtitres.pack(padx=5, pady=(0,10))

# frame serveur
frameS = tk.LabelFrame(configuration, borderwidth=2, text='Serveur', relief='groove', background='white')
frameS.pack(padx=10, pady=5)
selectedadresse = tk.StringVar()
labeladresse = tk.Label(frameS, background='white', text="adresse")
labeladresse.pack(anchor='w', padx=5, pady=5)
inputadresse = tk.Entry(frameS, textvariable=selectedadresse, width=30)
inputadresse.pack(padx=5)

selecteduser = tk.StringVar()
labeluser = tk.Label(frameS, background='white', text="utilisateur")
labeluser.pack(anchor='w', padx=5, pady=5)
inputuser = tk.Entry(frameS, textvariable=selecteduser, width=30)
inputuser.pack(padx=5)

selectedpassword = tk.StringVar()
labelpassword = tk.Label(frameS, background='white', text="mot de passe")
labelpassword.pack(anchor='w', padx=5, pady=5)
inputpassword = tk.Entry(frameS, textvariable=selectedpassword, width=30, show='*')
inputpassword.pack(padx=5, pady=(0,10))

# frame port série
framePS = tk.LabelFrame(configuration, borderwidth=2, text='Port série', relief='groove', background='white')
framePS.pack(padx=10, pady=5)

labelport = tk.Label(framePS, background='white', text="port")
labelport.pack(anchor='w', padx=5, pady=5)
listeports = [port.device for port in serial.tools.list_ports.comports()]
selectedport = tk.StringVar()
selecteurport = tkttk.Combobox(framePS, values=listeports, textvariable=selectedport, state='readonly', background = 'white')
selecteurport.set(listeports[0])
selecteurport.pack(padx=(5,74))

labelbauds = tk.Label(framePS, background='white', text="baudrate")
labelbauds.pack(anchor='w', padx=5, pady=5);
listebauds = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
selectedbauds = tk.StringVar()
selecteurbauds = tkttk.Combobox(framePS, values=listebauds, textvariable=selectedbauds, state='readonly', background = 'white')
selecteurbauds.set(listebauds[12])
selecteurbauds.pack(padx=(5,74))

labelbits = tk.Label(framePS, background='white', text="nombre de bits")
labelbits.pack(anchor='w', padx=5, pady=5);
listebits = ['7','8']
selectedbits = tk.StringVar()
selecteurbits = tkttk.Combobox(framePS, values=listebits, textvariable=selectedbits, state='readonly', background = 'white')
selecteurbits.set(listebits[1])
selecteurbits.pack(padx=(5,74), pady=(0,10))

labelparite = tk.Label(framePS, background='white', text="parité")
labelparite.pack(anchor='w', padx=5, pady=5);
listeparite = ["Aucune", "Paire", "Impaire"]
selectedparite = tk.StringVar()
selecteurparite = tkttk.Combobox(framePS, values=listeparite, textvariable=selectedparite, state='readonly', background = 'white')
selecteurparite.set(listeparite[0])
selecteurparite.pack(padx=(5,74), pady=(0,10))

labelstop = tk.Label(framePS, background='white', text="bits de stop")
labelstop.pack(anchor='w', padx=5, pady=5);
listestop = ["1", "1.5", "2"]
selectedstop = tk.StringVar()
selecteurstop = tkttk.Combobox(framePS, values=listestop, textvariable=selectedstop, state='readonly', background = 'white')
selecteurstop.set(listestop[0])
selecteurstop.pack(padx=(5,74), pady=(0,10))


boutonOk = tk.Button(configuration, text='Sauver', command=save)
boutonOk.pack(side='right',padx=5, pady=10)

config = configparser.ConfigParser()
readconfig()
####################################

entree = tkst.ScrolledText(principale, width=80, height=30, background='#eeeeee', state='disabled')
entree.grid(row=0,column=0,columnspan=3)

labeltitre=tk.Label(principale, background='white', text='Titre de l\'examen')
labeltitre.grid(row=1,column=0, pady=10)
selectedtitre = tk.StringVar()
listetitres=selectedtitres.get().split(',')
selecteurtitre = tkttk.Combobox(principale, values=listetitres, textvariable=selectedtitre, state='readonly', background = 'white')
selecteurtitre.set(listetitres[0])
selecteurtitre.grid(row=1,column=1, pady=10)

boutonConfig = tk.Button(principale, text="Configuration", command=configure)
boutonConfig.grid(row=2,column=0, pady=10, padx=0)

boutonGet = tk.Button(principale, text="Acquérir", command=get)
boutonGet.grid(row=2,column=1, pady=10)

boutonSend = tk.Button(principale, text="Envoyer", command=send, state='disabled')
boutonSend.grid(row=2,column=2, pady=10, padx=0)

sp = serial.Serial()

principale.mainloop()
