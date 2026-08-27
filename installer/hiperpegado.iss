; Instalador de Hiperpegado (Inno Setup 6)
; Compilar con: ISCC.exe installer\hiperpegado.iss   (o python build.py)

#define AppName      "Hiperpegado"
#define AppVersion   "1.0.0"
#define AppPublisher "Hiperpegado"
#define AppExe       "Hiperpegado.exe"

[Setup]
AppId={{9C4F1A2E-6B7D-4E58-9A31-0F2D5C8E7B44}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename={#AppName}Setup-{#AppVersion}
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Por defecto instala para el usuario actual sin pedir elevacion; el asistente
; ofrece tambien la instalacion para todo el equipo, que si requiere UAC.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Cierra la instancia en ejecucion antes de reemplazar archivos, via el
; Administrador de reinicio de Windows.
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "startupicon"; Description: "Iniciar {#AppName} con Windows"; GroupDescription: "Opciones:"

[Files]
Source: "..\dist\Hiperpegado\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"

[Registry]
; Arranque automatico. Siempre en HKCU: el usuario que instala es el que la usa,
; y asi la opcion sigue siendo reversible desde la ventana de configuracion.
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "{#AppName}"; ValueData: """{app}\{#AppExe}"" --tray"; \
    Flags: uninsdeletevalue; Tasks: startupicon

[Run]
; Da de alta la opcion del menu contextual y deja la bandeja funcionando.
Filename: "{app}\{#AppExe}"; Parameters: "--register"; Flags: runhidden waituntilterminated
Filename: "{app}\{#AppExe}"; Parameters: "--tray"; Description: "Iniciar {#AppName} ahora"; \
    Flags: nowait postinstall skipifsilent

[UninstallRun]
; Retira la entrada del menu contextual antes de borrar el ejecutable.
Filename: "{app}\{#AppExe}"; Parameters: "--unregister"; RunOnceId: "QuitarMenuContextual"; \
    Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  // La bandeja mantiene el .exe bloqueado; cerrarla antes de desinstalar.
  if CurUninstallStep = usUninstall then
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#AppExe}', '',
         SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
