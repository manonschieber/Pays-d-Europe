#
# import du module d'accès à la base de données
#
import sqlite3

#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('pays.sqlite')
cursor = conn.cursor()
cursor.execute("""SELECT wp,latitude,longitude FROM countries """)
L = cursor.fetchall()
#print(L)

#import matplotlib.image as mpimg
#import numpy as np
#im = mpimg.imread(u[0])
#import matplotlib.pyplot as plt
#plt.imshow(im)
#plt.show()

n = len(L)
M = []
for i in range(n):
    a = L[i]
    name = a[0]
    lattitude = a[1]
    longitude = a[2]
    d = {'id':i,'lat':lattitude,'lon':longitude,'name':name}
    M.append(d)

print(M)
#print(M[1]['lat'])

conn = sqlite3.connect('pays.sqlite')
cursor = conn.cursor()
sql='SELECT * FROM countries WHERE wp=?'
    
cursor.execute(sql,('France',))
#print(cursor.fetchone())




