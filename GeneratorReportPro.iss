[Setup]
AppName=GeneratorReportPro
AppVersion=1.0
DefaultDirName={autopf}\GeneratorReportPro
DefaultGroupName=GeneratorReportPro
OutputBaseFilename=GeneratorReportPro_Setup

[Files]

Source: "dist\GeneratorReportPro\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]

Name: "{commondesktop}\GeneratorReportPro"; Filename: "{app}\GeneratorReportPro.exe"

[Run]

Filename: "{app}\GeneratorReportPro.exe"; Description: "Запустить GeneratorReportPro"; Flags: nowait postinstall skipifsilent