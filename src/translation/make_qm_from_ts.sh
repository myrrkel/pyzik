#Pour ajouter une langue dans le projet Qt, dans le fichier .pro
#ajouter le nom du nouveau fichier de traduction:    
#		TRANSLATIONS += pyzik_en.ts pyzik_es.ts pyzik_fr.ts

# Needed: sudo apt-get install qttools5-dev-tools

cd ..
/usr/lib/x86_64-linux-gnu/qt5/bin/lrelease ./qt/*.ts
/usr/lib/x86_64-linux-gnu/qt5/bin/lrelease ./translation/*.ts
mv ./qt/*.qm ./translation/



