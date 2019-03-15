; pyzik.nsi
;
; It remember the directory, 
; has uninstall support and (optionally) installs start menu shortcuts.
;
; It will install Pyzik into a directory that the user selects,

;--------------------------------

; The name of the installer
Name "Pyzik Installer"
Icon "src/img/logo_64.ico"


; The file to write
OutFile "dist\pyzik-0.3.win32_installer.exe"

; The default installation directory
InstallDir $PROGRAMFILES\pyzik

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\pyzik" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "Pyzik 0.3"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
 File /r "dist\pyzik\*"
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\pyzik "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pyzik" "DisplayName" "Pyzik"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pyzik" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pyzik" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pyzik" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\Pyzik"
  CreateShortcut "$SMPROGRAMS\Pyzik\Pyzik.lnk" "$INSTDIR\pyzik.exe" "" "$INSTDIR\img\logo_64.ico" 0
  CreateShortcut "$SMPROGRAMS\Pyzik\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0

  
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Pyzik"
  DeleteRegKey HKLM SOFTWARE\Pyzik

  ; Remove files and uninstaller
  Delete $INSTDIR\pyzik*
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\Pyzik\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\Pyzik"
  RMDir "$INSTDIR"

SectionEnd
