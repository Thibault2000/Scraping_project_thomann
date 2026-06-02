"""
PROJET: Traitement et Analyse des données
Partie 2 Creation de la base de données
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt

#______________________________________________________________________________
###############################################################################
#configuartion
###############################################################################
Env_trav = *** 
os.chdir(Env_trav)


resultats = []
max_sous_cat = 0

#______________________________________________________________________________
###############################################################################
#Boucle pour extraire les données des HTML
###############################################################################

for root, dirs, files in os.walk(Env_trav):
    
    # On ne traite le dossier que s'il ont le fichier témoin scrapping fait
    if "scrapping_fait.txt" in files:
        
        # On récupère le nombre maximum de catégorie ( pour connaitre combien
        #de colone catégorie on fait au maximum)
        chemin_relatif = os.path.relpath(root, Env_trav)# vire l'environement
        #de trav du chemin donc des caté
        liste_categories = chemin_relatif.split(os.sep)# detecte les / et fait une 
        #liste avec pour avoir un enchainement
        
        if len(liste_categories) > max_sous_cat :
            max_sous_cat = len(liste_categories)# regarde la taille de cette liste
            #et garde la valeur la plus élever

        for file in files:
            if file.lower().startswith("item_") and file.lower().endswith(".html"):
                chemin_complet = os.path.join(root, file)# récupère les fichier produit
                with open(chemin_complet, "r", encoding="utf-8") as f:
                    html = f.read()

                info = {}

                #On récupère l'identifiant du produit 

                patern = r'"item_id":"(\d+)"'
                match = re.search(patern, html)
                if match:
                    info["ID"] = match.group(1)
                else:
                    info["ID"] = None
                    
                #On récupère la nom/ la référence du produit 
                patern = r'"item_name":"(.*?)"'
                match = re.search(patern, html)
                if match:
                    info["Nom"] = match.group(1)
                else:
                    info["Nom"] = None
                    
                #On récupère la marque
                patern = r'"item_brand":"(.*?)"'
                match = re.search(patern, html)
                if match:
                    info["Marque"] = match.group(1)
                else:
                    info["Marque"] = None

                #On récupère le prix
                patern = r'"price":([\d\.]+)'
                match = re.search(patern, html)
                prix_num = None
                if match:
                    prix_num = float(match.group(1))
                    info["Prix_EUR"] = prix_num
                else:
                    info["Prix_EUR"] = None

                #On determine si la livraison est gratuite ou non
                patern = r'(?:offert(?:s)?|gratuit(?:e)?)\s+dès\s+(\d+)\s?€'
                seuil_match = re.search(patern, html, re.IGNORECASE)#ignorecase permet
                #d'ignorer si on a des majuscule ou non
                seuil_reel = float(seuil_match.group(1))if seuil_match else 69.0
                
                if prix_num is not None:
                    info["Livraison_Gratuite"] = "Oui" if prix_num >= seuil_reel else "Non"
                else:
                    info["Livraison_Gratuite"] = None

                # On récupère la note du produit
                patern = r'itemprop="ratingValue">(.*?)</span>'
                match = re.search(patern, html)
                if match:
                    info["Note"] = match.group(1)
                else:
                    info["Note"] = None
                    
                # On récupère le nombre d'avis
                patern = r'itemprop="ratingCount">(.*?)</span>'
                match = re.search(patern, html)
                if match:
                    info["Nb_Avis"] = match.group(1)
                else:
                    info["Nb_Avis"] = 0

                #On récupère le poids du produit
                patern = r'Poids[:\s]+([\d,]+)\s?(kg)'
                match = re.search(patern, html)
                if match:
                    info["Poids_kg"] = float(match.group(1).replace(',', '.'))
                    # pour avoir que des . en virgule et évité tout problème avec le CSV
                else:
                    info["Poids_kg"] = None

                # On récupère la dimentions
                patern = r'[Dd]imensions.*?:[:\s]+(\d+[\d,]*)\s*x\s*(\d+[\d,]*)(?:\s*x\s*(\d+[\d,]*))?\s*([cmm]+)'
                match = re.search(patern, html)

                if match:
                #si on c'est ecrit de la "bonne" manière
                    #On récupère et on transforme en nombre 
                    v1 = float(match.group(1).replace(',', '.'))
                    v2 = float(match.group(2).replace(',', '.'))
                    # v3 est optionnel il n'existe pas pour certains objets
                    v3 = match.group(3)
                    if v3:
                        v3 = float(v3.replace(',', '.'))
    
                    unite = match.group(4).lower()
                    
                    # On convertie en cm pour plus d'uniformité
                    if unite == "mm":
                        v1 = v1 / 10
                        v2 = v2 / 10
                        if v3: v3 = v3 / 10
                    elif unite == "m":
                            v1 = v1 * 100
                            v2 = v2 * 100
                            if v3: v3 = v3 * 100
                        # Si c'est déjà en "cm", on ne touche à rien
                        
                    #On formate le texte final
                    if v3:
                        info["Dimensions"] = f"{v1} x {v2} x {v3} cm"
                    else:
                        info["Dimensions"] = f"{v1} x {v2} cm"

                else:
                #parfois la dimension est directement indiquer en longueur, 
                #largeur et hauteur
                    patern_L = r'[Ll]ongueur.*?:[:\s]+([\d,]+)\s?([cmm]+)'
                    patern_l = r'[Ll]argeur.*?:[:\s]+([\d,]+)\s?([cmm]+)'
                    patern_h = r'[Hh]auteur.*?:[:\s]+([\d,]+)\s?([cmm]+)'
                    
                    m_L = re.search(patern_L, html)
                    m_l = re.search(patern_l, html)
                    m_h = re.search(patern_h, html)
                    
                    dim_trouve = []
                    
                    # On convertie chaque dimension une par une
                    for m in [m_L, m_l, m_h]:
                        if m:
                            # On récupère la chaîne brute
                            val_brute = m.group(1).replace(',', '.')
                            try:
                                # On tente la conversion en nombre
                                v = float(val_brute)
                                unit = m.group(2).lower()
                                
                                # Conversion en cm
                                if unit == "mm": v = v / 10
                                if unit == "m": v = v * 100
                            
                                dim_trouve.append(str(v))
                            except ValueError:
                                # Si c'est un "." ou du texte, on ignore l'erreur et on continue
                                print(f" probleme de format sur une dimension dans : {file}")
                                continue
                    if dim_trouve:
                        info["Dimensions"] = " x ".join(dim_trouve) + " cm"
                    else:
                        # Si rien n'a été trouvé du tout
                        info["Dimensions"] = None
                    

                #On récupère si le produit est disponible
                patern = r'class="fx-availability.*?">(.*?)</span>'
                match = re.search(patern, html, re.DOTALL)
                if match:
                    info["Disponibilite"] = match.group(1).strip()
                else:
                    info["Disponibilite"] = None
                
                #On récupère depuis quand il est référencé
                patern = r'Référencé depuis.*?bold.*?>(.*?)</span>'
                match = re.search(patern, html, re.DOTALL)
                if match:
                    info["Reference_Depuis"] = match.group(1).strip()
                else:
                    info["Reference_Depuis"] = None
                    
                #On récupère le liens
                patern = r'<link rel="canonical" href="(.*?)"'
                match = re.search(patern, html)
                if match:
                    info["Lien"] = match.group(1)
                else:
                    info["Lien"] = None
                    
                
                # Sauvegarde temporaire de la hierarchie des catégorie car 
                #temps que on sais pas combien de catégorie max on a on peux pas 
                #faire un le bon nombre de colone il nous faut garder la hierarchie 
                #des catégorie
                info["_temp_hierarchie"] = liste_categories
                
                resultats.append(info)

# --- TRAITEMENT FINAL ET EXPORT ---
if len(resultats) > 0:
       
    # Transformation de la hiérarchie des catégorie en colonnes distinctes
    for item in resultats:
        h = item.pop("_temp_hierarchie")#on récupère les différentes catégorie
        #et on supprime la catégorie _temp
        for i in range(max_sous_cat):
            nom_colonne = f"Niveau_{i+1}"
            item[nom_colonne] = h[i] if i < len(h) else None

    df = pd.DataFrame(resultats)
    
    # Suppression des doublons basés sur l'ID car il est possible d'avoir des doublons
    df = df.drop_duplicates(subset=['ID'], keep='last')
    
    
    # Enregistrement de la base de donnée

    df.to_excel("base_donnees_thomann_finale.xlsx", index=False, engine='openpyxl')
    df.to_csv("base_donnees_thomann_finale.csv", index=False, sep=';', encoding='utf-8-sig')

   
else:
    print("Gros problème aucun fichier trouvé.")
    
    
    
#______________________________________________________________________________
###############################################################################
#Traitement et analyse de la base de données
###############################################################################
#Traitement de la Base de donnée

fichier_xlsx = "base_donnees_thomann_finale.xlsx"
fichier_csv = "base_donnees_thomann_finale.csv"

df = pd.read_excel(fichier_xlsx)

df = df.dropna(subset=['ID'])
df["ID"] = df["ID"].astype(int).astype(str)
# pour que on ai p<s des ID comme un nombre a virgule
df["Nb_Avis"] = pd.to_numeric(df["Nb_Avis"], errors='coerce').fillna(0).astype(int)
#transforme les valeurs manquantes du nombre d'avis en 0 car si ya pas de nombre d'avis c'est qu'il y a pas d'avis
df["Disponibilite"] = df["Disponibilite"].str.replace("Disponibilité immédiate", "Disponible immédiatement", regex=True, case=False)
# remplace la catégorie disponible immédiat par disponible immédiatement


ordre_colonnes = [
    "ID", "Nom", "Marque","Niveau_1", "Niveau_2", "Niveau_3","Prix_EUR",
    "Livraison_Gratuite","Note", "Nb_Avis","Poids_kg", "Dimensions",
    "Disponibilite", "Reference_Depuis","Lien"]

df = df[ordre_colonnes]

df.to_excel(fichier_xlsx, index=False)
df.to_csv(fichier_csv, index=False, sep=";", encoding='utf-8-sig')

#Différents graphique

plt.rcParams.update({"font.size": 18, "axes.titlesize": 22})

# Part de marché par marque en %
plt.figure(figsize=(12, 7))
top_10_pct = (df["Marque"].value_counts() / len(df) * 100).nlargest(10).sort_values()
top_10_pct.plot(kind="barh", color="#3498db", edgecolor="black")
plt.title("Graphique 1 : Part de marché par marque (% du catalogue)")
plt.xlabel("pourcentage (%)")
plt.tight_layout()
plt.savefig("graph_1_marques_pct.png")

# Stock 
df["Dispo_Groupe"] = "Autres / Indisponible"
df.loc[df["Disponibilite"].isin(["Disponible immédiatement", "Disponible rapidement (2 à 5 jours)"]), "Dispo_Groupe"] = "Stock immédiat"
df.loc[df["Disponibilite"].isin(["Disponible sous 1-2 semaines", "Disponible dans environ une semaine", "Disponible sous 2-3 semaines", "Provisoirement indisponible (1-2 semaines environ)"]), "Dispo_Groupe"] = "Court terme (1-3 sem.)"
df.loc[df["Disponibilite"].str.contains("3-4|4-5|5-7|6-8|7-9|8-10", na=False), "Dispo_Groupe"] = "Moyen terme (4-10 sem.)"
df.loc[df["Disponibilite"].str.contains("9-12|10-13|11-14|12-15|13-17|14-18|15-19|plusieurs mois", na=False), "Dispo_Groupe"] = "Long terme (+3 mois)"
df.loc[df["Disponibilite"].isin(["Pas encore disponible", "Précommandable maintenant","Sur demande"]), "Dispo_Groupe"] = "Précommande ou sur demande"

plt.figure(figsize=(10, 10))
colors = ["#2ecc71", "#95a5a6", "#f1c40f", "#e67e22", "#e74c3c"]
df["Dispo_Groupe"].value_counts().plot(kind="pie", autopct="%1.1f%%", startangle=140, colors=colors)
plt.title("Graphique 2 : Etat des stocks par catégorie")
plt.ylabel('')
plt.tight_layout()
plt.savefig("graph_2_dispo_pie.png")

# Satisfaction 
df["Satisfaction"] = "Pas d'avis"
df.loc[df["Note"] >= 4.5, "Satisfaction"] = "Très satisfait (4.5-5)"
df.loc[(df["Note"] >= 4.0) & (df["Note"] < 4.5), "Satisfaction"] = "Satisfait (4-4.4)"
df.loc[df["Note"] < 4.0, "Satisfaction"] = "Moyennement / Peu (<4)"

plt.figure(figsize=(10, 10))
df["Satisfaction"].value_counts().plot(kind="pie", autopct="%1.1f%%", startangle=140, colors=["#27ae60", "#bdc3c7", "#f1c40f", "#e74c3c"])
plt.title("Graphique 3 : Répartition de la satisfaction client")
plt.ylabel("")
plt.savefig("graphique_3_satisfaction_pie.png")

#Max et min du prix
print(f"Max : {df.loc[df['Prix_EUR'].idxmax(), ['Nom', 'Marque', 'Prix_EUR']].values}")
print(f"Min : {df.loc[df['Prix_EUR'].idxmin(), ['Nom', 'Marque', 'Prix_EUR']].values}")

