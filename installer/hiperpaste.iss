; Instalador de Hiperpaste (Inno Setup 6)
; Compilar con: ISCC.exe installer\hiperpaste.iss   (o python build.py)

#define AppName      "Hiperpaste"
; La version la genera build.py a partir de hiperpaste/__init__.py.
#include "version.iss"
#define AppPublisher "Hiperpaste"
#define AppExe       "Hiperpaste.exe"

[Setup]
AppId={{5E1F432E-60F4-4F73-BCAE-4ACC917F97F6}
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
Source: "..\dist\Hiperpaste\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

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
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  // Al actualizar, el Administrador de reinicio no logra cerrar la bandeja
  // (pystray no atiende su peticion de cierre) y la instalacion se aborta.
  // Se cierra aqui, antes de que intente sustituir el ejecutable.
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#AppExe}', '',
       SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := '';
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  // La bandeja mantiene el .exe bloqueado; cerrarla antes de desinstalar.
  if CurUninstallStep = usUninstall then
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM {#AppExe}', '',
         SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
