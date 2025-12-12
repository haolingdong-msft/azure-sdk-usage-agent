# Installation script for Azure SDK Usage Agent prerequisites
# Supports Windows with PowerShell 5.1+

# Set UTF-8 encoding for console output
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Required versions
$REQUIRED_AZ_VERSION = "2.65.0"

# Installation tracking
$script:ToInstall = @{}
$script:ToUpdate = @{}
$script:InstallCount = 0
$script:UpdateCount = 0

# Utility functions
function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Progress-Custom {
    param([string]$Message)
    Write-Host "[...] $Message" -ForegroundColor Blue
}

# Version comparison function
function Compare-Version {
    param(
        [string]$Version1,
        [string]$Version2
    )
    
    try {
        $v1 = [version]$Version1
        $v2 = [version]$Version2
        
        if ($v1 -eq $v2) { return 0 }
        if ($v1 -gt $v2) { return 1 }
        return -1
    }
    catch {
        Write-Warning-Custom "Could not compare versions: $Version1 vs $Version2"
        return 0
    }
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Azure CLI
function Test-AzureCLI {
    Write-Progress-Custom "Checking Azure CLI (az)..."
    
    $azCommand = Get-Command az -ErrorAction SilentlyContinue
    if ($azCommand) {
        try {
            $versionOutput = az version --output json 2>&1 | Out-String
            if ($versionOutput -match '"azure-cli": "([0-9]+\.[0-9]+\.[0-9]+)') {
                $currentVersion = $matches[1]
                Write-Info "Found az version: $currentVersion"
                
                $comparison = Compare-Version $currentVersion $REQUIRED_AZ_VERSION
                if ($comparison -lt 0) {
                    Write-Warning-Custom "az version $currentVersion is below required version $REQUIRED_AZ_VERSION"
                    $script:ToUpdate["az"] = "$currentVersion -> $REQUIRED_AZ_VERSION+"
                    $script:UpdateCount++
                }
                else {
                    Write-Success "Azure CLI is up to date (>= $REQUIRED_AZ_VERSION)"
                }
            }
            else {
                Write-Warning-Custom "Could not determine az version"
                $script:ToUpdate["az"] = "unknown -> $REQUIRED_AZ_VERSION+"
                $script:UpdateCount++
            }
        }
        catch {
            Write-Warning-Custom "Error checking az version: $_"
        }
    }
    else {
        Write-Warning-Custom "Azure CLI (az) is not installed"
        $script:ToInstall["az"] = $REQUIRED_AZ_VERSION
        $script:InstallCount++
    }
}

# Check Azure Developer CLI
function Test-AzureDeveloperCLI {
    Write-Progress-Custom "Checking Azure Developer CLI (azd)..."
    
    $azdCommand = Get-Command azd -ErrorAction SilentlyContinue
    if ($azdCommand) {
        try {
            $versionOutput = azd version 2>&1 | Out-String
            if ($versionOutput -match 'azd version (\d+\.\d+\.\d+)') {
                $currentVersion = $matches[1]
                Write-Info "Found azd version: $currentVersion"
                
                $comparison = Compare-Version $currentVersion $REQUIRED_AZD_VERSION
                if ($comparison -lt 0) {
                    Write-Warning-Custom "azd version $currentVersion is below required version $REQUIRED_AZD_VERSION"
                    $script:ToUpdate["azd"] = "$currentVersion -> $REQUIRED_AZD_VERSION+"
                    $script:UpdateCount++
                }
                else {
                    Write-Success "azd is up to date (>= $REQUIRED_AZD_VERSION)"
                }
            }
            else {
                Write-Warning-Custom "Could not determine azd version"
                $script:ToUpdate["azd"] = "unknown -> $REQUIRED_AZD_VERSION+"
                $script:UpdateCount++
            }
        }
        catch {
            Write-Warning-Custom "Error checking azd version: $_"
        }
    }
    else {
        Write-Warning-Custom "Azure Developer CLI (azd) is not installed"
        $script:ToInstall["azd"] = $REQUIRED_AZD_VERSION
        $script:InstallCount++
    }
}

# Check Azure Functions Core Tools
function Test-AzureFunctionsCoreTools {
    Write-Progress-Custom "Checking Azure Functions Core Tools..."
    
    $funcCommand = Get-Command func -ErrorAction SilentlyContinue
    if ($funcCommand) {
        try {
            $versionOutput = func --version 2>&1 | Out-String
            if ($versionOutput -match '(\d+\.\d+\.\d+)') {
                $currentVersion = $matches[1]
                Write-Info "Found func version: $currentVersion"
                
                $comparison = Compare-Version $currentVersion $REQUIRED_FUNC_VERSION
                if ($comparison -lt 0) {
                    Write-Warning-Custom "func version $currentVersion is below required version $REQUIRED_FUNC_VERSION"
                    $script:ToUpdate["func"] = "$currentVersion -> $REQUIRED_FUNC_VERSION+"
                    $script:UpdateCount++
                }
                else {
                    Write-Success "Azure Functions Core Tools is up to date (>= $REQUIRED_FUNC_VERSION)"
                }
            }
            else {
                Write-Warning-Custom "Could not determine func version"
            }
        }
        catch {
            Write-Warning-Custom "Error checking func version: $_"
        }
    }
    else {
        Write-Warning-Custom "Azure Functions Core Tools is not installed"
        $script:ToInstall["func"] = $REQUIRED_FUNC_VERSION
        $script:InstallCount++
    }
}

# Check Visual Studio Code
function Test-VSCode {
    Write-Progress-Custom "Checking Visual Studio Code..."
    
    $codeCommand = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCommand) {
        try {
            $versionOutput = code --version 2>&1 | Out-String
            $version = ($versionOutput -split "`n")[0].Trim()
            Write-Success "Visual Studio Code is installed (version: $version)"
        }
        catch {
            Write-Success "Visual Studio Code is installed"
        }
    }
    else {
        Write-Warning-Custom "Visual Studio Code is not installed"
        $script:ToInstall["vscode"] = "latest"
        $script:InstallCount++
    }
}

# Check VS Code Azure Functions extension
function Test-VSCodeExtension {
    Write-Progress-Custom "Checking VS Code Azure Functions extension..."
    
    $codeCommand = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCommand) {
        try {
            $extensions = code --list-extensions 2>&1 | Out-String
            if ($extensions -match "ms-azuretools.vscode-azurefunctions") {
                Write-Success "Azure Functions extension is installed"
            }
            else {
                Write-Warning-Custom "Azure Functions extension is not installed"
                $script:ToInstall["vscode-extension"] = "ms-azuretools.vscode-azurefunctions"
                $script:InstallCount++
            }
        }
        catch {
            Write-Warning-Custom "Could not check VS Code extensions: $_"
        }
    }
    else {
        Write-Info "Skipping extension check (VS Code not installed)"
    }
}

# Check uv
function Test-UV {
    Write-Progress-Custom "Checking uv..."
    
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) {
        try {
            $versionOutput = uv --version 2>&1 | Out-String
            if ($versionOutput -match 'uv (\d+\.\d+\.\d+)') {
                $version = $matches[1]
                Write-Success "uv is installed (version: $version)"
            }
            else {
                Write-Success "uv is installed"
            }
        }
        catch {
            Write-Success "uv is installed"
        }
    }
    else {
        Write-Warning-Custom "uv is not installed"
        $script:ToInstall["uv"] = "latest"
        $script:InstallCount++
    }
}

# Install Azure CLI
function Install-AzureCLI {
    Write-Progress-Custom "Installing Azure CLI..."
    
    try {
        # Check if winget is available
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget install Microsoft.AzureCLI --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "az installed successfully"
                return
            }
        }
        
        # Fallback to MSI installer
        Write-Info "Downloading Azure CLI installer..."
        $msiUrl = "https://aka.ms/installazurecliwindows"
        $msiPath = "$env:TEMP\AzureCLI.msi"
        Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath
        
        Write-Info "Installing Azure CLI (this may take a few minutes)..."
        Start-Process msiexec.exe -ArgumentList "/i", $msiPath, "/quiet", "/norestart" -Wait
        Remove-Item $msiPath -ErrorAction SilentlyContinue
        
        Write-Success "az installed successfully"
        Write-Warning-Custom "Please restart your terminal to use 'az' command"
    }
    catch {
        Write-Error-Custom "Failed to install az: $_"
        Write-Info "Please install manually from: https://learn.microsoft.com/cli/azure/install-azure-cli"
    }
}

# Update Azure CLI
function Update-AzureCLI {
    Write-Progress-Custom "Updating Azure CLI..."
    
    try {
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget upgrade Microsoft.AzureCLI --accept-source-agreements --accept-package-agreements
            Write-Success "az updated successfully"
        }
        else {
            Write-Warning-Custom "winget not available, using az upgrade"
            az upgrade --yes
            Write-Success "az updated successfully"
        }
    }
    catch {
        Write-Error-Custom "Failed to update az: $_"
    }
}

# Install Azure Developer CLI
function Install-AzureDeveloperCLI {
    Write-Progress-Custom "Installing Azure Developer CLI..."
    
    try {
        # Check if winget is available
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget install microsoft.azd --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "azd installed successfully"
                return
            }
        }
        
        # Fallback to PowerShell script installation
        $installScript = Invoke-WebRequest -Uri "https://aka.ms/install-azd.ps1" -UseBasicParsing
        Invoke-Expression ($installScript.Content)
        Write-Success "azd installed successfully"
    }
    catch {
        Write-Error-Custom "Failed to install azd: $_"
    }
}

# Update Azure Developer CLI
function Update-AzureDeveloperCLI {
    Write-Progress-Custom "Updating Azure Developer CLI..."
    
    try {
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget upgrade microsoft.azd --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "azd updated successfully"
                return
            }
        }
        
        # Fallback to reinstall
        Install-AzureDeveloperCLI
    }
    catch {
        Write-Error-Custom "Failed to update azd: $_"
    }
}

# Install Azure Functions Core Tools
function Install-AzureFunctionsCoreTools {
    Write-Progress-Custom "Installing Azure Functions Core Tools..."
    
    try {
        # Check if Chocolatey is available
        $chocoCommand = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoCommand) {
            choco install azure-functions-core-tools-4 -y
            if ($LASTEXITCODE -eq 0) {
                Write-Success "func installed successfully"
                return
            }
        }
        
        # Check if winget is available
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget install Microsoft.Azure.FunctionsCoreTools --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "func installed successfully"
                return
            }
        }
        
        # Manual installation via npm
        $npmCommand = Get-Command npm -ErrorAction SilentlyContinue
        if ($npmCommand) {
            npm install -g azure-functions-core-tools@4
            if ($LASTEXITCODE -eq 0) {
                Write-Success "func installed successfully via npm"
                return
            }
        }
        
        Write-Warning-Custom "Could not install Azure Functions Core Tools automatically"
        Write-Info "Please install manually from: https://learn.microsoft.com/azure/azure-functions/functions-run-local"
    }
    catch {
        Write-Error-Custom "Failed to install func: $_"
    }
}

# Update Azure Functions Core Tools
function Update-AzureFunctionsCoreTools {
    Write-Progress-Custom "Updating Azure Functions Core Tools..."
    
    try {
        $chocoCommand = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoCommand) {
            choco upgrade azure-functions-core-tools-4 -y
            if ($LASTEXITCODE -eq 0) {
                Write-Success "func updated successfully"
                return
            }
        }
        
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget upgrade Microsoft.Azure.FunctionsCoreTools --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "func updated successfully"
                return
            }
        }
        
        # Fallback to reinstall
        Install-AzureFunctionsCoreTools
    }
    catch {
        Write-Error-Custom "Failed to update func: $_"
    }
}

# Install Visual Studio Code
function Install-VSCode {
    Write-Progress-Custom "Installing Visual Studio Code..."
    
    try {
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget install Microsoft.VisualStudioCode --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "VS Code installed successfully"
                Write-Info "You may need to restart your terminal to use the 'code' command"
                return
            }
        }
        
        $chocoCommand = Get-Command choco -ErrorAction SilentlyContinue
        if ($chocoCommand) {
            choco install vscode -y
            if ($LASTEXITCODE -eq 0) {
                Write-Success "VS Code installed successfully"
                return
            }
        }
        
        Write-Warning-Custom "Could not install VS Code automatically"
        Write-Info "Please install manually from: https://code.visualstudio.com/download"
    }
    catch {
        Write-Error-Custom "Failed to install VS Code: $_"
    }
}

# Install VS Code extension
function Install-VSCodeExtension {
    Write-Progress-Custom "Installing Azure Functions extension for VS Code..."
    
    $codeCommand = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCommand) {
        try {
            code --install-extension ms-azuretools.vscode-azurefunctions
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Extension installed successfully"
            }
            else {
                Write-Error-Custom "Failed to install extension"
            }
        }
        catch {
            Write-Error-Custom "Failed to install extension: $_"
        }
    }
    else {
        Write-Error-Custom "VS Code is not installed"
    }
}

# Install uv
function Install-UV {
    Write-Progress-Custom "Installing uv..."
    
    try {
        # Try winget first
        $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
        if ($wingetCommand) {
            winget install --id astral-sh.uv --accept-source-agreements --accept-package-agreements
            if ($LASTEXITCODE -eq 0) {
                Write-Success "uv installed successfully"
                return
            }
        }
        
        # Fallback to PowerShell installation script
        irm https://astral.sh/uv/install.ps1 | iex
        Write-Success "uv installed successfully"
    }
    catch {
        Write-Error-Custom "Failed to install uv: $_"
    }
}

# Main installation function
function Start-Installation {
    $totalActions = $script:InstallCount + $script:UpdateCount
    $current = 0
    
    Write-Header "Starting Installation/Update Process"
    
    # Install new packages
    foreach ($package in $script:ToInstall.Keys) {
        $current++
        Write-Host "`n[$current/$totalActions]" -ForegroundColor Blue
        
        switch ($package) {
            "az" { Install-AzureCLI }
            "vscode" { Install-VSCode }
            "uv" { Install-UV }
        }
    }
    
    # Update existing packages
    foreach ($package in $script:ToUpdate.Keys) {
        $current++
        Write-Host "`n[$current/$totalActions]" -ForegroundColor Blue
        
        switch ($package) {
            "az" { Update-AzureCLI }
        }
    }
}

# Main script
function Main {
    Write-Header "Prerequisites Check for MCP SDK Usage Kusto Server"
    
    # Check if running as Administrator
    if (-not (Test-Administrator)) {
        Write-Warning-Custom "This script may require Administrator privileges for some installations"
        Write-Info "Consider running PowerShell as Administrator for best results"
        Write-Host ""
    }
    
    # Check all prerequisites
    Test-AzureCLI
    Test-VSCode
    Test-UV
    
    # Summary
    Write-Header "Check Summary"
    
    if ($script:InstallCount -eq 0 -and $script:UpdateCount -eq 0) {
        Write-Success "All prerequisites are installed and up to date!"
        return
    }
    
    # Show what needs to be installed
    if ($script:InstallCount -gt 0) {
        Write-Host "Packages to install:" -ForegroundColor Yellow
        foreach ($package in $script:ToInstall.Keys) {
            Write-Host "  - $package (>= $($script:ToInstall[$package]))"
        }
        Write-Host ""
    }
    
    # Show what needs to be updated
    if ($script:UpdateCount -gt 0) {
        Write-Host "Packages to update:" -ForegroundColor Yellow
        foreach ($package in $script:ToUpdate.Keys) {
            Write-Host "  - $package ($($script:ToUpdate[$package]))"
        }
        Write-Host ""
    }
    
    # Ask for confirmation
    $response = Read-Host "Do you want to proceed with installation/update? [y/N]"
    
    if ($response -notmatch '^[Yy]$') {
        Write-Info "Installation cancelled by user"
        return
    }
    
    # Perform installation
    Start-Installation
    
    # Final verification
    Write-Header "Final Verification"
    Test-AzureCLI
    Test-VSCode
    Test-UV
    
    Write-Header "Installation Complete"
    Write-Success "All operations completed!"
    Write-Info "You may need to restart your terminal/PowerShell for some changes to take effect"
    Write-Info "If 'code' command is not found after VS Code installation, restart your terminal"
}

# Run main function
Main
