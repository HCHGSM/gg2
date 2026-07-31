; Inno Setup script for Smart POS & ERP
; Build with: iscc installer\SmartPOS_ERP.iss   (Inno Setup 6.x, on Windows)
; Prerequisite: dist\SmartPOS_ERP.exe must already exist (run build.py / PyInstaller first).
;
; !! Update AppPublisher, AppPublisherURL, and AppVersion below to real values
; !! before shipping - see FINAL_AUDIT_REPORT.md "Decisions Required" section.

#define MyAppName "Smart POS & ERP"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://example.com"
#define MyAppExeName "ERP.exe"

[Setup]
AppId={{8F2C6C6E-9C1A-4C9E-9B7B-4E1F6A2B0A11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Users without admin rights can still install to their own profile if needed:
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist_installer
OutputBaseFilename=SmartPOS_ERP_Setup_{#MyAppVersion}
SetupIconFile=..\assets\icons\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Add any additional loose files here if the build ever stops being one-file, e.g.:
; Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
; Ensure the app's data/log directory exists and is writable post-install,
; matching pos_erp/database/db.py's default DB_PATH (<app>/data/pos_erp.db).
Name: "{app}\data"; Permissions: users-modify
