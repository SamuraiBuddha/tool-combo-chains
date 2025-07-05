;===========================================
; Hybrid Memory Cognitive Stack Installer
; NSIS Script for Windows Installer
;===========================================

!define APPNAME "Hybrid Memory Cognitive Stack"
!define COMPANYNAME "Ehrig BIM & IT Consultation Inc"
!define DESCRIPTION "AI Cognitive Amplification System - 100x Productivity"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/SamuraiBuddha/tool-combo-chains"
!define UPDATEURL "https://github.com/SamuraiBuddha/tool-combo-chains/releases"
!define ABOUTURL "https://github.com/SamuraiBuddha/tool-combo-chains"
!define INSTALLSIZE 50000

; Request administrator privileges
RequestExecutionLevel admin

; Include Modern UI
!include "MUI2.nsh"

; General
Name "${APPNAME}"
OutFile "HybridMemory_Setup.exe"
Unicode True
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" ""

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "hybrid_memory_icon.ico"
!define MUI_UNICON "hybrid_memory_icon.ico"

; Welcome Page
!insertmacro MUI_PAGE_WELCOME

; License Page (optional)
; !insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

; Directory Page
!insertmacro MUI_PAGE_DIRECTORY

; Installation Page
!insertmacro MUI_PAGE_INSTFILES

; Finish Page
!define MUI_FINISHPAGE_RUN "$INSTDIR\start_hybrid_memory.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Start Hybrid Memory System"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${APPNAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${COMPANYNAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© 2025 ${COMPANYNAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${DESCRIPTION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.0"

; Installation Section
Section "!${APPNAME}" SecDummy

    SetOutPath "$INSTDIR"
    
    ; Create installation directory
    CreateDirectory "$INSTDIR"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\data"
    
    ; Copy files
    File "start_hybrid_memory.bat"
    File "hybrid_memory_icon.ico"
    File "..\*.md"
    File "..\*.yml"
    File "..\*.bat"
    File "..\*.py"
    File /r "..\tool_combo_chains"
    File /r "..\docker"
    File /r "..\scripts"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\start_hybrid_memory.bat" "" "$INSTDIR\hybrid_memory_icon.ico"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" ""
    
    ; Desktop shortcut
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\start_hybrid_memory.bat" "" "$INSTDIR\hybrid_memory_icon.ico"
    
    ; Store installation folder
    WriteRegStr HKCU "Software\${APPNAME}" "" $INSTDIR
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registry information for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\hybrid_memory_icon.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

SectionEnd

; Check Dependencies Function
Function CheckDependencies
    ; Check Docker
    nsExec::ExecToStack 'docker --version'
    Pop $0
    Pop $1
    StrCmp $0 "0" docker_ok
        MessageBox MB_OK|MB_ICONSTOP "Docker is required but not found! Please install Docker Desktop first.$\nDownload from: https://www.docker.com/products/docker-desktop"
        Abort
    docker_ok:
    
    ; Check Python
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    StrCmp $0 "0" python_ok
        MessageBox MB_OK|MB_ICONSTOP "Python is required but not found! Please install Python 3.8+ first.$\nDownload from: https://www.python.org/downloads/"
        Abort
    python_ok:
    
    ; Check Git (optional but recommended)
    nsExec::ExecToStack 'git --version'
    Pop $0
    Pop $1
    StrCmp $0 "0" git_ok
        MessageBox MB_YESNO|MB_ICONQUESTION "Git is recommended for updates. Continue without Git?" IDYES git_ok
        ExecShell "open" "https://git-scm.com/downloads"
        Abort
    git_ok:
FunctionEnd

; Installation Function
Function .onInit
    Call CheckDependencies
FunctionEnd

; Uninstaller Section
Section "Uninstall"

    ; Stop any running services
    nsExec::ExecToLog 'docker-compose -f "$INSTDIR\docker-compose.yml" down'
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remove files
    RMDir /r "$INSTDIR\tool_combo_chains"
    RMDir /r "$INSTDIR\docker" 
    RMDir /r "$INSTDIR\scripts"
    RMDir /r "$INSTDIR\logs"
    Delete "$INSTDIR\*.*"
    RMDir "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCU "Software\${APPNAME}"

SectionEnd

; Function to run after installation
Function .onInstSuccess
    MessageBox MB_YESNO "Installation complete! Would you like to start Hybrid Memory now?" IDNO finish
    ExecShell "open" "$INSTDIR\start_hybrid_memory.bat"
    finish:
FunctionEnd
