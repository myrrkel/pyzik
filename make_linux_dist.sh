pyinstaller -y pyzik.spec
cp /usr/lib/x86_64-linux-gnu/libvlc.so.5.6.0 dist/pyzik
cp /usr/lib/x86_64-linux-gnu/libvlccore.so.9.0.0 dist/pyzik
cp /usr/lib/x86_64-linux-gnu/libvlc.so.5 dist/pyzik
cp /usr/lib/x86_64-linux-gnu/libvlccore.so.9 dist/pyzik
tar -zcvf dist/pyzik-0.3.2.linux-x86_64.tar.gz dist/pyzik
