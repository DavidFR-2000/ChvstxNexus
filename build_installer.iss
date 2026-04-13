[Setup]
AppName=Chvstx Nexus
AppVersion=4.0.1
AppPublisher=DavidFR-2000
AppPublisherURL=https://github.com/DavidFR-2000/ChvstxNexux
DefaultDirName={localappdata}\Programs\ChvstxNexus
DefaultGroupName=Chvstx Nexus
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=ChvstxNexus_v4.0.1_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
InfoBeforeFile=dist\tutorial.txt
WizardImageFile=dist\wizard_banner.bmp
WizardSmallImageFile=dist\wizard_small.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ChvstxNexus\ChvstxNexus.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ChvstxNexus\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Chvstx Nexus"; Filename: "{app}\ChvstxNexus.exe"
Name: "{autodesktop}\Chvstx Nexus"; Filename: "{app}\ChvstxNexus.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ChvstxNexus.exe"; Description: "{cm:LaunchProgram,Chvstx Nexus}"; Flags: nowait postinstall skipifsilent
