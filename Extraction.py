# -*- coding: utf-8 -*-
"""
PROJET: Traitement et Analyse des données

AUTEURS Thibault AZAIS & Thibault PHILIBERT
Partie 1: Extraction
"""
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import re

#______________________________________________________________________________
###############################################################################
#Configuration
###############################################################################
"""
On créé notre environement de travail. on utilise un chemin absolue car cela 
fonctionne mieux sur mon ordinateur
On a aussi remarquer que l'url etait toujours constitué de la même structure:
https://www.thomann.fr/ + autre chose.html
"""
Env_trav = r'C:\Users\hp\Bureau\Pro\Cours Scholaire\fac\master\M2\M2 S1\Python\Projet de fin de cour\Traitement et Analyse des données\Data'
os.chdir(Env_trav)


url_depart = "https://www.thomann.fr/instruments_clavier.html"
url_commun = "https://www.thomann.fr/"
headers = {
 'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.0;en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6"
}

#______________________________________________________________________________
###############################################################################
#Fonction utilisé
###############################################################################
"""
On a créé 2 conction pour nous facilité la tache:
    - Une fonction qui nettoie les noms des variables pour évitez de créé des problemes sur les chemins
    - Une qui permet de regarder quelle type de page est la page analysé. Si c'est une page
    sous dossier il faut continuer a extraire les différentes catégorie puis lorsque
    on est sur la page produit on va récuperer le nom des différents produit et on 
    va pouvoir extraire les données.
    
"""
def nettoyer_les_noms_var(texte):
    #evite les noms de variables qui pourrais faire planté mon chemin de l'ordi
    return texte.replace("/", "-").replace("\\", "_").replace(":", "").replace('"', "").strip()

def analyser_type_de_page(soup): 
    #Renvoie "1" si c'est une page de sous-dossiers.
    #Renvoie "0" si c'est une page finale avec des produits.
    #Renvoie "2" si c'est une page bizarre.
    is_categorie = soup.find("div", class_="fx-category-grid")
    is_article = soup.find("div", class_="fx-product-list-entry")
    if is_categorie:
        return "1"
    elif is_article:
        return "0"
    else:
        return "2"

###############################################################################
#Script de récupération des données
###############################################################################
"""
On va le faire en 3 parties:
1) On va tout d'abord créé les sous catégorie de  "base"
2) On récupère larchitecture du site: le site est composé de sous catégorie qui
s'impbrique les unes dans les autres. On va récuperer toutes ses sous partie et
les créé comme chemin dans le dossier data. On s'arrette quand on a récuperé toutes
les sous catégories et que on les a toutes créées.
3) on telecharge les page HTML des différents produit.

Pour toutes ses partie on va utiliser un timeout de 10 et un time sleep random entre
3 et 5. il est random pour évité d'avoir une erreur 429
Si on a un code 429 on aura une pose de 1 min pour ne pas être banni completment du site
De plus on va faire une boucle essai entre 1 et 3 pour que si le sut a un petit bug
le scrapping se fasse quanf même et que on relance quand même. Si il n'a pas réussi
il y a peux être un soucis autre
On va aussi créé des petit fichier texte qui servirons de repère et qui decrirons 
l'état du document.
"""
#1) Démarage : creation des première sous catégorie
if not os.listdir(Env_trav): 
    try:
        req = requests.get(url_depart, headers=headers, timeout=10)
        if req.status_code == 200:       
            nom_fichier = 'page_acceuil.html'
            with open(nom_fichier, "w", encoding="utf-8") as f:
                f.write(req.text)
        else:
            print(f" Erreur du site : {req.status_code}")
    except Exception as e:
        print(f"Crash critique : {e}")

    # On lit le fichier
    with open(nom_fichier, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    type_page = analyser_type_de_page(soup)
    
    #on verifie la type de la page même si normalement c'est bon
    if type_page == "1" :
        zone_sous_cat = soup.find("div", class_="fx-category-grid")
        # tout les élémenets de nos sous catégorie sont dans la classe
        #"fx-category-grid" ça créé une sorte de sous zone ou recuperer les catégorie "a" 
        #sans attraper tout les catégorie inutiles
        sous_cat = zone_sous_cat.find_all("a")
        for cat in sous_cat:
            nom_brut = cat.text.strip()
            
            # On nettoit le nom que on a trouver
            nom = nettoyer_les_noms_var(nom_brut)
            url = cat["href"]# c'est comme un dictionnaire 
            
            # On verifie que le liens est bien ce que on attent: autrechose.html
            if not url.startswith("http"):
                url = url_commun + url.lstrip("/")
            chemin_dossier = os.path.join(Env_trav, nom)
            os.makedirs(chemin_dossier, exist_ok=True)
            with open(os.path.join(chemin_dossier, "url.txt"), "w", encoding="utf-8") as f:
                f.write(url)
        
    else:
        print("Gros problème : On a pas de catégorie dans la page de départ")
        exit()
else:
    print(" Les initialisation on déja été fait")


# 2) La boucle qui récupère toute toutes l'architecture

Un_doc_cree_en_plus = True
nombre_passage = 1

#Fait une methode ittérative il va relancer la boucle tant que un nouvelle élément a été créé

while Un_doc_cree_en_plus :
    
    Un_doc_cree_en_plus = False # on le passe en faut pour que on puisse le 
    #remettre vrai si on a un nouvelle élément

    for root, dirs, files in os.walk(Env_trav):
        # On traite si : url.txt existe, pas de Fini.txt, et pas de sous-dossiers déja créé
        if "url.txt" in files and "Fini.txt" not in files and not dirs:
            
            # Lecture URL
            with open(os.path.join(root, "url.txt"), "r", encoding="utf-8") as f:
                url_cible = f.read().strip()
            
            #Téléchargement du HTML
            contenu_page = None# on la créé avant le for pour si apres les 3 essaie
            #il reste vide on passe a la suite
            
            for essai in range(3):
                time.sleep(random.uniform(3.0, 5.0))
                
                try:
                    req = requests.get(url_cible, headers=headers, timeout=10)
                    
                    if req.status_code == 200:
                        contenu_page = req.text
                        break # Succès
                    elif req.status_code == 429: # On c'est fait ban
                        print("Pause forcée (429) - 60s")
                        time.sleep(60)
                    else:
                        print(f"Erreur {req.status_code}")
                        break
                except Exception as e:
                    print(f"Erreur réseau : {e}")
            
            # Si ça marche pas après 3 essai
            if not contenu_page :
                continue
            
            with open(os.path.join(root, "navigation.html"), "w", encoding="utf-8") as f:
                f.write(contenu_page)

            #On regarde si c'est une page produit ou une page catégorie
            soup = BeautifulSoup(contenu_page , "html.parser")
            type_page = analyser_type_de_page(soup)
            
            # Premier possibilité : c'est une catégorie on créé donc les dossiers
            if type_page == "1":
                grille = soup.find("div", class_="fx-category-grid")
                if grille:
                    liens = grille.find_all("a", href=True)
                    for lien in liens:
                        nom = nettoyer_les_noms_var(lien.text)
                        url = lien["href"]
                        if not url.startswith("http"): url = url_commun + url.lstrip("/")
                        
                        path = os.path.join(root, nom)
                        os.makedirs(path, exist_ok=True)
                        with open(os.path.join(path, "url.txt"), "w", encoding="utf-8") as f:
                            f.write(url)
                        print(f"On a fait {nom}")
                    
                    Un_doc_cree_en_plus = True

            # Deuxieme possibilité : c'est une page produit. on s'arret la
            elif type_page == "0":
                with open(os.path.join(root, "Fini.txt"), "w", encoding="utf-8") as f:
                    f.write("PRET") 
            #Dernier cas on a une page bizarre on ignore la page et on marque quand 
            #même le chemin pour verifier a manuelement 
            else:
                print(f"Page ignorée.{root}")
        else:
            print (f"{os.path.basename(root)} OK")# os.path.basename c'est pour
            # avoir le nom de la dernière catégorie
    if Un_doc_cree_en_plus :
        nombre_passage += 1
    else:
        print("Partie 2 fini!!!!!!")
        

#3 recuperation de toute les données.

# Cette fois on ne peux pas faire de methode itérative car si il y a des pages 
#produit qui sont plus disponible ou qui n'ont plus de page web fonctionnel

compteur_telechargement = 0
# pour connaitre combien de fichier on été télécharger et avoir un idée de s'il
# eu des erreurs

for root, dirs, files in os.walk(Env_trav):
    
    # On cible les dossiers " bout de ligne" ( ou on c'est arréter avant)
    if not dirs and "url.txt" in files:
        
        # Si déjà fait, on passe
        if "scrapping_fait.txt" in files:
            continue
        
        # Lire l'URL de base pour le vérifier
        with open(os.path.join(root, "url.txt"), "r", encoding="utf-8") as f:
            base_url = f.read().strip()
        #comme les url page se mette comme ça :
        #(ex :https://www.thomann.fr/methodes_d_apprentissage_piano1.html?ls=50&pg=1 
        #on verifie qu'il y a bien pas de ? dans l'url
        if "?" in base_url:
            base_url = base_url.split("?")[0]

        #detection du nombre de page
        url_page_1 = f"{base_url}?ls=50&pg=1"
        last_page = 1
        #on force la page 1 et 50 item max pour etre sur
        #on récupere la page 1 
        for essai_page in range(3):
            try:
                time.sleep(random.uniform(3.0, 5.0))                
                req = requests.get(url_page_1, headers=headers, timeout=10)                
                if req.status_code == 200:
                    patern = r'"currentPage":\s*\d+,\s*"lastPage":\s*(\d+)'
                    match = re.search(patern, req.text)
                    if match:
                        last_page = int(match.group(1))#on transforme en nombre
                        #(le chirffre sort en texte)
                        print(f" On a :{last_page} page(s).")
                    else:
                        print("Probleme on a pas trouver de page")
                    break # Sortie boucle essai               
                elif req.status_code == 429:
                    print(" Erreur 429 on c'est fait ban quelque temps donc pause")
                    time.sleep(60)
                else:
                    print(f"Erreur {req.status_code}")
                    break
            except Exception as e:
                print(f" Erreur réseau : {e}")
                time.sleep(5)

        # On va donc récuperer tout les liens des différentes pages
        tout_les_liens_prod = []
        
        for p in range(1, last_page + 1):
            url_actuelle = f"{base_url}?ls=50&pg={p}"
            
            succes_navig = False
            for essai_nav in range(3):
                try:
                    time.sleep(random.uniform(3.0, 5.0))
                    
                    resp = requests.get(url_actuelle, headers=headers, timeout=10)
                    
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        count_page = 0
                        for a in soup.select('.fx-product-list-entry a.product__content'):
                            url_prod = a.get('href')
                            if url_prod:
 #on verifie que les url on pas changer (que les url ne sont pas complet)
                                if not url_prod.startswith("http"):
                                    # On enlève le slash du début s'il y est, pour coller proprement
                                    url_prod = url_prod.lstrip("/")
                                    url_prod = url_commun + url_prod
                                    
                                if url_prod not in tout_les_liens_prod : 
                                    tout_les_liens_prod.append(url_prod)
                                    count_page += 1
                        succes_navig = True
                        break # Page OK on continue
                        
                    elif resp.status_code == 429:
                        print("Erreur 429 on c'est fait ban quelque temps donc pause")
                        time.sleep(60)
                        
                except Exception as e:
                    print(f"Erreur réseau page {p}: {e}")
            
            if not succes_navig:
                print(f"Impossible de lire la page {p}, on continue...")

        total_liens = len(tout_les_liens_prod)
        print(f"{total_liens} produits trouvé")

        if total_liens == 0:
            with open(os.path.join(root, "scrapping_fait.txt"), "w") as f: f.write("VIDE")
            continue
#dans notre document témoins on  va dire que le dossier est vide. cela nous servira
#pour la partie veririfications des potentielles erreurs.

        # téléchargement des pages html des produit
        reussites = 0
        
        #On verifie si le produit n'existe pas dans notre base de donnée.        
        for i, link in enumerate(tout_les_liens_prod):
            
            nom_fichier = f"item_{i+1}.html"
            chemin_fichier = os.path.join(root, nom_fichier)
            
            if os.path.exists(chemin_fichier):
                reussites += 1
                continue
#/!\ le numéros du produit ( 1, 2, 3 ....) est attribuer en fonction de la place
# du liens dans la liste donc le liens 1 c'est celui a la place 0 (i+1)
            # On a pas déja le produit
            for essai in range(3):
                try:
                    wait_time = random.uniform(3.0, 5.0)
                    time.sleep(wait_time)
                    req_prod = requests.get(link, headers=headers, timeout=10)
                    
                    if req_prod.status_code == 200:
                        with open(chemin_fichier, "w", encoding="utf-8") as f:
                            f.write(req_prod.text)
                        reussites += 1
                        compteur_telechargement += 1
                        
                        # Log tous les 5 produits
                        if i % 5 == 0:
                            print(f"{i+1}/{total_liens} ok")
                        break # Succès, on passe au produit suivant
                        
                    elif req_prod.status_code == 429:
                        print("Erreur 429 on c'est fait ban quelque temps donc pause")
                        time.sleep(60)
                        # Pas de break, on réessaie le même produit après la pause
                    else:
                        print(f"Erreur HTTP {req_prod.status_code}")
                        break # Erreur fatale (404 etc), on lâche l'affaire pour ce produit
                        
                except Exception as e:
                    print(f"Bug réseau produit : {e}")
                    time.sleep(5)

        # On mets une validation (pour permettre une verification)
        # On valide même s'il manque des produit mets on le mentionne on pourra donc 
        # les rajouter lors de la veriffication et de la correction des potentiels problème
        with open(os.path.join(root, "scrapping_fait.txt"), "w", encoding="utf-8") as f:
            f.write(f"OK - {reussites}/{total_liens} produits")
            
        print(f" On a récupérer ({reussites}/{total_liens})")

print(f"On a fini !!!!! Il y a {compteur_telechargement} fichiers téléchargés.")

time.sleep(360)
# on fait une pose de 10 min entre la fin de l'extraction de donnée et la correction 
# de donnée pour évité que le site nous concidère comme un robot
#______________________________________________________________________________
###############################################################################
#Verification et correction des différents problème
###############################################################################
"""
Dans cette partie on va verifier une fois les erreurs potentielles faite lors 
du téléchargement des données. Pour cela on va le faire en 2 étapes:
1) On repère les differents dossier avec des problemes grace au document 
   scrapping_fait on le supprime
2) On relance le script de récuperation de donnée car on avais déjà géré la
   Possibilité d'avoir des dossier déjà créé et a affecter un " numéros unique"
   a chacun des item ( dumoins dans le dossier)
"""
#On repere les probleme et ou il y en a on supprime le fichier "scrapping fait"
for root, dirs, files in os.walk(Env_trav):
    if "scrapping_fait.txt" in files:
        with open(os.path.join(root, "scrapping_fait.txt"), "r") as f:
            content = f.read().strip()
# il y a 2 possibilité sois il y a marqué VIDE, sois : OK - x/y produits avec 
#x et y des chiffres ( égales ou non)
        #On gere la possibilité VIDE
        if content == "VIDE":
            os.remove(os.path.join(root, "scrapping_fait.txt"))
            print (f"attention on a eu un dossier vide {root} a surveiller")
        # On gére la possibilité que x ne sois pas égale a y ( il manque des données)
        else:
            match = re.search(r'(\d+)/(\d+)', content)
            if match:
                x = int(match.group(1)) #c'est le nombre de page télécharger
                y = int(match.group(2)) # C'est le nombre de produit dans la catégorie
                
                if x == y:
                    continue
                else:
                    os.remove(os.path.join(root, "scrapping_fait.txt"))
                    
#On va récupérer les données qui nous manques.

compteur_telechargement = 0
# pour connaitre combien de fichier on été télécharger et avoir un idée de s'il
# eu des erreurs

for root, dirs, files in os.walk(Env_trav):
    
    # On cible les dossiers " bout de ligne" ( ou on c'est arréter avant)
    if not dirs and "url.txt" in files:
        
        # Si déjà fait, on passe
        if "scrapping_fait.txt" in files:
            continue
        
        # Lire l'URL de base pour le vérifier
        with open(os.path.join(root, "url.txt"), "r", encoding="utf-8") as f:
            base_url = f.read().strip()
        #comme les url page se mette comme ça :
        #(ex :https://www.thomann.fr/methodes_d_apprentissage_piano1.html?ls=50&pg=1 
        #on verifie qu'il y a bien pas de ? dans l'url
        if "?" in base_url:
            base_url = base_url.split("?")[0]

        #detection du nombre de page
        url_page_1 = f"{base_url}?ls=50&pg=1"
        last_page = 1
        #on force la page 1 et 50 item max pour etre sur
        #on récupere la page 1 
        for essai_page in range(3):
            try:
                time.sleep(random.uniform(3.0, 5.0))                
                req = requests.get(url_page_1, headers=headers, timeout=10)                
                if req.status_code == 200:
                    patern = r'"currentPage":\s*\d+,\s*"lastPage":\s*(\d+)'
                    match = re.search(patern, req.text)
                    if match:
                        last_page = int(match.group(1))#on transforme en nombre
                        #(le chirffre sort en texte)
                        print(f" On a :{last_page} page(s).")
                    else:
                        print("Probleme on a pas trouver de page")
                    break # Sortie boucle essai               
                elif req.status_code == 429:
                    print(" Erreur 429 on c'est fait ban quelque temps donc pause")
                    time.sleep(60)
                else:
                    print(f"Erreur {req.status_code}")
                    break
            except Exception as e:
                print(f" Erreur réseau : {e}")
                time.sleep(5)

        # On va donc récuperer tout les liens des différentes pages
        tout_les_liens_prod = []
        
        for p in range(1, last_page + 1):
            url_actuelle = f"{base_url}?ls=50&pg={p}"
            
            succes_navig = False
            for essai_nav in range(3):
                try:
                    time.sleep(random.uniform(3.0, 5.0))
                    
                    resp = requests.get(url_actuelle, headers=headers, timeout=10)
                    
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        count_page = 0
                        for a in soup.select('.fx-product-list-entry a.product__content'):
                            url_prod = a.get('href')
                            if url_prod:
 #on verifie que les url on pas changer (que les url ne sont pas complet)
                                if not url_prod.startswith("http"):
                                    # On enlève le slash du début s'il y est, pour coller proprement
                                    url_prod = url_prod.lstrip("/")
                                    url_prod = url_commun + url_prod
                                    
                                if url_prod not in tout_les_liens_prod : 
                                    tout_les_liens_prod.append(url_prod)
                                    count_page += 1
                        succes_navig = True
                        break # Page OK on continue
                        
                    elif resp.status_code == 429:
                        print("Erreur 429 on c'est fait ban quelque temps donc pause")
                        time.sleep(60)
                        
                except Exception as e:
                    print(f"Erreur réseau page {p}: {e}")
            
            if not succes_navig:
                print(f"Impossible de lire la page {p}, on continue...")

        total_liens = len(tout_les_liens_prod)
        print(f"{total_liens} produits trouvé")

        if total_liens == 0:
            with open(os.path.join(root, "scrapping_fait.txt"), "w") as f: f.write("VIDE")
            continue
#dans notre document témoins on  va dire que le dossier est vide. cela nous servira
#pour la partie veririfications des potentielles erreurs.

        # téléchargement des pages html des produit
        reussites = 0
        
        #On verifie si le produit n'existe pas dans notre base de donnée.        
        for i, link in enumerate(tout_les_liens_prod):
            
            nom_fichier = f"item_{i+1}.html"
            chemin_fichier = os.path.join(root, nom_fichier)
            
            if os.path.exists(chemin_fichier):
                reussites += 1
                continue
#/!\ le numéros du produit ( 1, 2, 3 ....) est attribuer en fonction de la place
# du liens dans la liste donc le liens 1 c'est celui a la place 0 (i+1)
            # On a pas déja le produit
            for essai in range(3):
                try:
                    wait_time = random.uniform(3.0, 5.0)
                    time.sleep(wait_time)
                    req_prod = requests.get(link, headers=headers, timeout=10)
                    
                    if req_prod.status_code == 200:
                        with open(chemin_fichier, "w", encoding="utf-8") as f:
                            f.write(req_prod.text)
                        reussites += 1
                        compteur_telechargement += 1
                        
                        # Log discret tous les 5 produits
                        if i % 5 == 0:
                            print(f"{i+1}/{total_liens} ok")
                        break # Succès, on passe au produit suivant
                        
                    elif req_prod.status_code == 429:
                        print("Erreur 429 on c'est fait ban quelque temps donc pause")
                        time.sleep(60)
                        # Pas de break, on réessaie le même produit après la pause
                    else:
                        print(f"Erreur HTTP {req_prod.status_code}")
                        break # Erreur fatale (404 etc), on lâche l'affaire pour ce produit
                        
                except Exception as e:
                    print(f"Bug réseau produit : {e}")
                    time.sleep(5)

        # On mets une validation (pour permettre une verification)
        # On valide même s'il manque des produit mets on le mentionne on pourra donc 
        # les rajouter lors de la veriffication et de la correction des potentiels problème
        with open(os.path.join(root, "scrapping_fait.txt"), "w", encoding="utf-8") as f:
            f.write(f"OK - {reussites}/{total_liens} produits")
            
        print(f" On a récupérer ({reussites}/{total_liens})")

print(f"On a fini !!!!! Il y a {compteur_telechargement} fichiers téléchargés.")

