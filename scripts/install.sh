#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Required versions
REQUIRED_AZ_VERSION="2.65.0"

# Installation tracking
declare -A TO_INSTALL
declare -A TO_UPDATE
INSTALL_COUNT=0
UPDATE_COUNT=0

# Utility functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_progress() {
    echo -e "${BLUE}⏳ $1${NC}"
}

# Version comparison function
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Check Azure CLI
check_az() {
    print_progress "Checking Azure CLI (az)..."
    
    if command -v az &> /dev/null; then
        local current_version=$(az version --output json 2>/dev/null | grep -oP '"azure-cli": "\K[0-9]+\.[0-9]+\.[0-9]+' || echo "0.0.0")
        print_info "Found az version: $current_version"
        
        version_compare $current_version $REQUIRED_AZ_VERSION
        local result=$?
        
        if [[ $result -eq 2 ]]; then
            print_warning "az version $current_version is below required version $REQUIRED_AZ_VERSION"
            TO_UPDATE["az"]="$current_version -> $REQUIRED_AZ_VERSION+"
            ((UPDATE_COUNT++))
        else
            print_success "Azure CLI is up to date (>= $REQUIRED_AZ_VERSION)"
        fi
    else
        print_warning "Azure CLI (az) is not installed"
        TO_INSTALL["az"]=$REQUIRED_AZ_VERSION
        ((INSTALL_COUNT++))
    fi
}

# Check Azure Developer CLI
check_azd() {
    print_progress "Checking Azure Developer CLI (azd)..."
    
    if command -v azd &> /dev/null; then
        local current_version=$(azd version 2>&1 | grep -oP 'azd version \K[0-9]+\.[0-9]+\.[0-9]+' || echo "0.0.0")
        print_info "Found azd version: $current_version"
        
        version_compare $current_version $REQUIRED_AZD_VERSION
        local result=$?
        
        if [[ $result -eq 2 ]]; then
            print_warning "azd version $current_version is below required version $REQUIRED_AZD_VERSION"
            TO_UPDATE["azd"]="$current_version -> $REQUIRED_AZD_VERSION+"
            ((UPDATE_COUNT++))
        else
            print_success "azd is up to date (>= $REQUIRED_AZD_VERSION)"
        fi
    else
        print_warning "Azure Developer CLI (azd) is not installed"
        TO_INSTALL["azd"]=$REQUIRED_AZD_VERSION
        ((INSTALL_COUNT++))
    fi
}

# Check Azure Functions Core Tools
check_func() {
    print_progress "Checking Azure Functions Core Tools..."
    
    if command -v func &> /dev/null; then
        local current_version=$(func --version 2>&1 | grep -oP '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "0.0.0")
        print_info "Found func version: $current_version"
        
        version_compare $current_version $REQUIRED_FUNC_VERSION
        local result=$?
        
        if [[ $result -eq 2 ]]; then
            print_warning "func version $current_version is below required version $REQUIRED_FUNC_VERSION"
            TO_UPDATE["func"]="$current_version -> $REQUIRED_FUNC_VERSION+"
            ((UPDATE_COUNT++))
        else
            print_success "Azure Functions Core Tools is up to date (>= $REQUIRED_FUNC_VERSION)"
        fi
    else
        print_warning "Azure Functions Core Tools is not installed"
        TO_INSTALL["func"]=$REQUIRED_FUNC_VERSION
        ((INSTALL_COUNT++))
    fi
}

# Check Visual Studio Code
check_vscode() {
    print_progress "Checking Visual Studio Code..."
    
    if command -v code &> /dev/null; then
        local current_version=$(code --version 2>&1 | head -1 || echo "unknown")
        print_success "Visual Studio Code is installed (version: $current_version)"
    else
        print_warning "Visual Studio Code is not installed"
        TO_INSTALL["vscode"]="latest"
        ((INSTALL_COUNT++))
    fi
}

# Check VS Code Azure Functions extension
check_vscode_extension() {
    print_progress "Checking VS Code Azure Functions extension..."
    
    if command -v code &> /dev/null; then
        if code --list-extensions 2>&1 | grep -q "ms-azuretools.vscode-azurefunctions"; then
            print_success "Azure Functions extension is installed"
        else
            print_warning "Azure Functions extension is not installed"
            TO_INSTALL["vscode-extension"]="ms-azuretools.vscode-azurefunctions"
            ((INSTALL_COUNT++))
        fi
    else
        print_info "Skipping extension check (VS Code not installed)"
    fi
}

# Check uv
check_uv() {
    print_progress "Checking uv..."
    
    if command -v uv &> /dev/null; then
        local current_version=$(uv --version 2>&1 | grep -oP 'uv \K[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
        print_success "uv is installed (version: $current_version)"
    else
        print_warning "uv is not installed"
        TO_INSTALL["uv"]="latest"
        ((INSTALL_COUNT++))
    fi
}

# Install Azure CLI
install_az() {
    print_progress "Installing Azure CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install azure-cli && print_success "az installed successfully" || print_error "Failed to install az"
        else
            print_error "Homebrew is required to install Azure CLI on macOS"
            print_info "Please install from: https://learn.microsoft.com/cli/azure/install-azure-cli"
            return 1
        fi
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash && print_success "az installed successfully" || print_error "Failed to install az"
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Fedora
        sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
        sudo sh -c 'echo -e "[azure-cli]\nname=Azure CLI\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'
        sudo yum install -y azure-cli && print_success "az installed successfully" || print_error "Failed to install az"
    else
        print_error "Unsupported Linux distribution"
        print_info "Please install from: https://learn.microsoft.com/cli/azure/install-azure-cli"
        return 1
    fi
}

# Update Azure CLI
update_az() {
    print_progress "Updating Azure CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        brew upgrade azure-cli && print_success "az updated successfully" || print_error "Failed to update az"
    elif [[ -f /etc/debian_version ]]; then
        sudo apt-get update
        sudo apt-get install --only-upgrade -y azure-cli && print_success "az updated successfully" || print_error "Failed to update az"
    elif [[ -f /etc/redhat-release ]]; then
        sudo yum update -y azure-cli && print_success "az updated successfully" || print_error "Failed to update az"
    fi
}

# Install Azure Developer CLI
install_azd() {
    print_progress "Installing Azure Developer CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install azure-dev && print_success "azd installed successfully" || print_error "Failed to install azd"
        else
            curl -fsSL https://aka.ms/install-azd.sh | bash && print_success "azd installed successfully" || print_error "Failed to install azd"
        fi
    else
        # Linux
        curl -fsSL https://aka.ms/install-azd.sh | bash && print_success "azd installed successfully" || print_error "Failed to install azd"
    fi
}

# Update Azure Developer CLI
update_azd() {
    print_progress "Updating Azure Developer CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        brew upgrade azure-dev && print_success "azd updated successfully" || print_error "Failed to update azd"
    else
        curl -fsSL https://aka.ms/install-azd.sh | bash && print_success "azd updated successfully" || print_error "Failed to update azd"
    fi
}

# Install Azure Functions Core Tools
install_func() {
    print_progress "Installing Azure Functions Core Tools..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew tap azure/functions
            brew install azure-functions-core-tools@4 && print_success "func installed successfully" || print_error "Failed to install func"
        else
            print_error "Homebrew is required to install Azure Functions Core Tools on macOS"
            return 1
        fi
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
        sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
        sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
        sudo apt-get update
        sudo apt-get install azure-functions-core-tools-4 && print_success "func installed successfully" || print_error "Failed to install func"
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Fedora
        sudo sh -c 'echo -e "[azure-cli]\nname=Azure CLI\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'
        sudo yum install azure-functions-core-tools-4 && print_success "func installed successfully" || print_error "Failed to install func"
    else
        print_error "Unsupported Linux distribution"
        return 1
    fi
}

# Update Azure Functions Core Tools
update_func() {
    print_progress "Updating Azure Functions Core Tools..."
    
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        brew upgrade azure-functions-core-tools@4 && print_success "func updated successfully" || print_error "Failed to update func"
    elif [[ -f /etc/debian_version ]]; then
        sudo apt-get update
        sudo apt-get install --only-upgrade azure-functions-core-tools-4 && print_success "func updated successfully" || print_error "Failed to update func"
    elif [[ -f /etc/redhat-release ]]; then
        sudo yum update azure-functions-core-tools-4 && print_success "func updated successfully" || print_error "Failed to update func"
    fi
}

# Install Visual Studio Code
install_vscode() {
    print_progress "Installing Visual Studio Code..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install --cask visual-studio-code && print_success "VS Code installed successfully" || print_error "Failed to install VS Code"
        else
            print_error "Homebrew is required to install VS Code on macOS"
            print_info "Please install from: https://code.visualstudio.com/download"
            return 1
        fi
    elif [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
        sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
        rm -f packages.microsoft.gpg
        sudo apt-get update
        sudo apt-get install code && print_success "VS Code installed successfully" || print_error "Failed to install VS Code"
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Fedora
        sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
        sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
        sudo yum install code && print_success "VS Code installed successfully" || print_error "Failed to install VS Code"
    else
        print_error "Unsupported Linux distribution"
        print_info "Please install from: https://code.visualstudio.com/download"
        return 1
    fi
}

# Install VS Code extension
install_vscode_extension() {
    print_progress "Installing Azure Functions extension for VS Code..."
    
    if command -v code &> /dev/null; then
        code --install-extension ms-azuretools.vscode-azurefunctions && print_success "Extension installed successfully" || print_error "Failed to install extension"
    else
        print_error "VS Code is not installed"
        return 1
    fi
}

# Install uv
install_uv() {
    print_progress "Installing uv..."
    
    curl -LsSf https://astral.sh/uv/install.sh | sh && print_success "uv installed successfully" || print_error "Failed to install uv"
}

# Main installation function
perform_installation() {
    local total_actions=$((INSTALL_COUNT + UPDATE_COUNT))
    local current=0
    
    print_header "Starting Installation/Update Process"
    
    # Install new packages
    for package in "${!TO_INSTALL[@]}"; do
        ((current++))
        echo -e "\n${BLUE}[$current/$total_actions]${NC}"
        
        case $package in
            az)
                install_az
                ;;
            vscode)
                install_vscode
                ;;
            uv)
                install_uv
                ;;
        esac
    done
    
    # Update existing packages
    for package in "${!TO_UPDATE[@]}"; do
        ((current++))
        echo -e "\n${BLUE}[$current/$total_actions]${NC}"
        
        case $package in
            az)
                update_az
                ;;
        esac
    done
}

# Main script
main() {
    print_header "Prerequisites Check for MCP SDK Usage Kusto Server"
    
    # Check all prerequisites
    check_az
    check_vscode
    check_uv
    
    # Summary
    print_header "Check Summary"
    
    if [[ $INSTALL_COUNT -eq 0 && $UPDATE_COUNT -eq 0 ]]; then
        print_success "All prerequisites are installed and up to date!"
        exit 0
    fi
    
    # Show what needs to be installed
    if [[ $INSTALL_COUNT -gt 0 ]]; then
        echo -e "${YELLOW}Packages to install:${NC}"
        for package in "${!TO_INSTALL[@]}"; do
            echo -e "  - $package (>= ${TO_INSTALL[$package]})"
        done
        echo ""
    fi
    
    # Show what needs to be updated
    if [[ $UPDATE_COUNT -gt 0 ]]; then
        echo -e "${YELLOW}Packages to update:${NC}"
        for package in "${!TO_UPDATE[@]}"; do
            echo -e "  - $package (${TO_UPDATE[$package]})"
        done
        echo ""
    fi
    
    # Ask for confirmation
    read -p "$(echo -e ${BLUE}Do you want to proceed with installation/update? [y/N]: ${NC})" -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled by user"
        exit 0
    fi
    
    # Perform installation
    perform_installation
    
    # Final verification
    print_header "Final Verification"
    check_az
    check_vscode
    check_uv
    
    print_header "Installation Complete"
    print_success "All operations completed!"
    print_info "You may need to restart your terminal for some changes to take effect"
}

# Run main function
main
