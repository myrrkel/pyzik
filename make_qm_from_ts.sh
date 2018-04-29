#Pour ajouter une langue dans le projet Qt, dans le fichier .pro
#ajouter le nom du nouveau fichier de traduction:    
#		TRANSLATIONS += pyzik_en.ts pyzik_es.ts pyzik_fr.ts


lrelease ./qt/*.ts
lrelease ./*.ts
cp ./qt/*.qm ./



