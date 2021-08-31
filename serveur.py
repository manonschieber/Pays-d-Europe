# Projet/serveur.py
#
# Ce serveur correspond à TD3-s7.py amputé de la route /time
#
import http.server
import socketserver
import sqlite3
import json

from urllib.parse import urlparse, parse_qs, unquote

    
    
#
# Définition du nouveau handler
#
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  # version du serveur
  server_version = 'serveur'

#Récupération de la base de données sous forme d'un dictionnaire
  
  #
  # On surcharge la méthode qui traite les requêtes GET
  #
  def do_GET(self):
    # on récupère les paramètres
    self.init_params()

    if self.path_info[0] == "location":   #pour localiser les différents pays 
      data=self.send_location()
      self.send_json(data)

    # requete description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
    elif self.path_info[0] == "description":
        self.send_country(self.path_info[1])

    # requête générique
    elif self.path_info[0] == "service":
      self.send_html('<p>Path info : <code>{}</p><p>Chaîne de requête : <code>{}</code></p>' \
          .format('/'.join(self.path_info),self.query_string));

    # ou pas...
    else:
      self.send_static()

  def db_get_country(self,country):
    M=self.send_description()
    return M[int(country)]
    
  def send_country(self,country):   #renvoie la description du pays en format html
    r=self.db_get_country(country)     
    lien='https://en.wikipedia.org/wiki/'+r['wp']
    flag=r['flag']
    body = '<ul>'
    body += '<li>{}: {}</li>'.format('Nom complet',r['name'].capitalize())
    body += '<li>{}: {}</li>'.format('Capital',r['capital'])
    body += '<li>{}: {:.3f}</li>'.format('Latitude',r['lat'])
    body += '<li>{}: {:.3f}</li>'.format('Longitude',r['lon'])
    body += '<li>{}: {:.3f}</li>'.format('Population',r['pop'])
    body += '<li>{}: {}</li>'.format('Read more on','<a href='+lien+'> wikipedia </a>')
    body +='<br><br><img src="/flags/' + flag + '"></i>'
    body += '</ul>'

    self.send_html(body)
  
  
  def send_location(self):    #renvoie les éléments de la base de données nécessaires à la localisation des pays
    conn = sqlite3.connect('pays.sqlite')
    cursor = conn.cursor()
    cursor.execute("""SELECT wp,latitude,longitude FROM countries """)
    L = cursor.fetchall()
    
    n = len(L)
    M = []
    for i in range(n):
        a = L[i]
        name = a[0]
        lattitude = a[1]
        longitude = a[2]
        d = {'id':i,'lat':lattitude,'lon':longitude,'name':name}
        M.append(d)
      
    return M
    
  def send_description(self):   #renvoie les éléments de la base de données nécessaires à la description des pays
    conn = sqlite3.connect('pays.sqlite')
    cursor = conn.cursor()
    cursor.execute("""SELECT wp,name,capital,latitude,longitude,population,flag FROM countries """)
    L = cursor.fetchall()
    
    n = len(L)
    M = []
    for i in range(n):
        a = L[i]
        wp=a[0]
        name=a[1]
        capital=a[2]
        latitude = a[3]
        longitude = a[4]
        population = a[5]
        flag=a[6]
        d={'id':i,'wp':wp,'name':name,'capital':capital,'lat':latitude,'lon':longitude,'pop':population,'flag':flag}   #format d'un dictionnaire
        M.append(d)
    return M
  #
  # On surcharge la méthode qui traite les requêtes HEAD
  #
  def do_HEAD(self):
    self.send_static()

  def do_POST(self):
    self.init_params()

    # requête générique
    if self.path_info[0] == "service":
      self.send_html(('<p>Path info : <code>{}</code></p><p>Chaîne de requête : <code>{}</code></p>' \
          + '<p>Corps :</p><pre>{}</pre>').format('/'.join(self.path_info),self.query_string,self.body));

    else:
      self.send_error(405)
      
  #
  # On envoie le document statique demandé
  #
  def send_static(self):

    # on modifie le chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
     
  # on envoie un document html dynamique
  def send_html(self,content):
     headers = [('Content-Type','text/html;charset=utf-8')]
     html = '<!DOCTYPE html><title>{}</title><meta charset="utf-8">{}' \
         .format(self.path_info[0],content)
     self.send(html,headers)
     
  # on envoie un contenu encodé en json
  def send_json(self,data,headers=[]):
    body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body)

  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''

  #
  # On renvoie les informations d'un pays au format json
  #
  def send_json_country(self,country):

    # on récupère le pays depuis la base de données
    r = self.db_get_country(country)

    # on n'a pas trouvé le pays demandé
    if r == None:
      self.send_error(404,'Country not found')

    # on renvoie un dictionnaire au format JSON
    else:
      data = {k:r[k] for k in r.keys()}
      json_data = json.dumps(data, indent=4)
      headers = [('Content-Type','application/json')]
      self.send(json_data,headers)


  #
  # On envoie les entêtes et le corps fourni
  #
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(encoded)

 
#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('pays.sqlite')

# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()

