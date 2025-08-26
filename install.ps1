# Volume Control MCP Server - Windows Installation Script
# Run this script in PowerShell to automatically install and set up the volume control MCP server

param(
    [switch]$Dev,
    [switch]$Help
)

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Magenta = "`e[35m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param($Message, $Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Show-Help {
    Write-ColorOutput "🔊 Volume Control MCP Server - Installation Script" $Cyan
    Write-ColorOutput ""
    Write-ColorOutput "USAGE:" $Yellow
    Write-ColorOutput "  .\install.ps1                 # Standard installation"
    Write-ColorOutput "  .\install.ps1 -Dev            # Development installation (with dev dependencies)"
    Write-ColorOutput "  .\install.ps1 -Help           # Show this help message"
    Write-ColorOutput ""
    Write-ColorOutput "WHAT THIS SCRIPT DOES:" $Yellow
    Write-ColorOutput "  1. Checks Python version (requires 3.10+)"
    Write-ColorOutput "  2. Installs UV package manager if not present"
    Write-ColorOutput "  3. Installs project dependencies"
    Write-ColorOutput "  4. Sets up console commands"
    Write-ColorOutput "  5. Runs a quick test to verify installation"
    Write-ColorOutput ""
    Write-ColorOutput "AFTER INSTALLATION:" $Yellow
    Write-ColorOutput "  • Run server: volumecontrol-mcp-server"
    Write-ColorOutput "  • Run client: volumecontrol-mcp-client"
    Write-ColorOutput "  • Or use: python volumecontrol_server.py"
    exit 0
}

if ($Help) {
    Show-Help
}

Write-ColorOutput "🚀 Volume Control MCP Server Installation" $Cyan
Write-ColorOutput "=========================================" $Cyan
Write-ColorOutput ""

# Check if running on Windows
if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne "Win32NT") {
    Write-ColorOutput "❌ This script is designed for Windows. Use install.sh for Linux/WSL." $Red
    exit 1
}

# Check Python installation
Write-ColorOutput "🐍 Checking Python installation..." $Blue
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    
    # Extract version number
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-ColorOutput "❌ Python 3.10+ required. Found: $pythonVersion" $Red
            Write-ColorOutput "   Please install Python 3.10+ from https://python.org" $Yellow
            exit 1
        }
        
        Write-ColorOutput "✅ Found $pythonVersion" $Green
    } else {
        Write-ColorOutput "⚠️  Could not parse Python version: $pythonVersion" $Yellow
    }
} catch {
    Write-ColorOutput "❌ Python is not installed or not in PATH" $Red
    Write-ColorOutput "   Please install Python 3.10+ from https://python.org" $Yellow
    exit 1
}

# Check UV installation
Write-ColorOutput "📦 Checking UV package manager..." $Blue
try {
    $uvVersion = uv --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✅ Found UV: $uvVersion" $Green
    } else {
        throw "UV not found"
    }
} catch {
    Write-ColorOutput "⚠️  UV not found, installing..." $Yellow
    try {
        pip install uv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install UV"
        }
        Write-ColorOutput "✅ UV installed successfully" $Green
    } catch {
        Write-ColorOutput "❌ Failed to install UV package manager" $Red
        Write-ColorOutput "   Please install manually: pip install uv" $Yellow
        exit 1
    }
}

# Check if we're in the right directory
if (!(Test-Path "pyproject.toml")) {
    Write-ColorOutput "❌ pyproject.toml not found. Please run this script from the project root directory." $Red
    exit 1
}

if (!(Test-Path "volumecontrol_server.py")) {
    Write-ColorOutput "❌ volumecontrol_server.py not found. Please run this script from the project root directory." $Red
    exit 1
}

# Install dependencies
Write-ColorOutput "🔧 Installing dependencies..." $Blue
try {
    if ($Dev) {
        Write-ColorOutput "   Installing with development dependencies..." $Yellow
        uv sync --extra dev
    } else {
        uv sync
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "UV sync failed"
    }
    Write-ColorOutput "✅ Dependencies installed successfully" $Green
} catch {
    Write-ColorOutput "❌ Failed to install dependencies" $Red
    Write-ColorOutput "   Trying alternative installation method..." $Yellow
    
    try {
        if ($Dev) {
            pip install -e ".[dev]"
        } else {
            pip install -e .
        }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Pip install failed"
        }
        Write-ColorOutput "✅ Dependencies installed with pip" $Green
    } catch {
        Write-ColorOutput "❌ Failed to install dependencies with both UV and pip" $Red
        exit 1
    }
}

# Verify installation
Write-ColorOutput "🧪 Verifying installation..." $Blue

# Check if console scripts are available
try {
    $serverCheck = Get-Command volumecontrol-mcp-server -ErrorAction Stop
    Write-ColorOutput "✅ Console script 'volumecontrol-mcp-server' available" $Green
} catch {
    Write-ColorOutput "⚠️  Console script not found, but you can use: python volumecontrol_server.py" $Yellow
}

try {
    $clientCheck = Get-Command volumecontrol-mcp-client -ErrorAction Stop
    Write-ColorOutput "✅ Console script 'volumecontrol-mcp-client' available" $Green
} catch {
    Write-ColorOutput "⚠️  Console script not found, but you can use: python volumecontrol_client.py" $Yellow
}

# Quick functionality test
Write-ColorOutput "🎯 Running quick functionality test..." $Blue
try {
    $testOutput = python -c "
import sys
sys.path.insert(0, '.')
try:
    from volumecontrol_server import VolumeController
    controller = VolumeController()
    result = controller.get_volume()
    if result.get('status') == 'success':
        print('✅ Volume control functionality verified')
    else:
        print('⚠️ Volume control test completed with warnings')
except Exception as e:
    print(f'⚠️ Volume control test failed: {e}')
    print('   This might be normal if audio drivers are not available')
" 2>&1

    Write-ColorOutput $testOutput $Green
} catch {
    Write-ColorOutput "⚠️  Functionality test failed, but installation should still work" $Yellow
}

# Installation complete
Write-ColorOutput ""
Write-ColorOutput "🎉 Installation Complete!" $Green
Write-ColorOutput "========================" $Green
Write-ColorOutput ""
Write-ColorOutput "NEXT STEPS:" $Cyan
Write-ColorOutput ""
Write-ColorOutput "1. Start the MCP server:" $Yellow
Write-ColorOutput "   volumecontrol-mcp-server" $White
Write-ColorOutput "   # OR: python volumecontrol_server.py" $Magenta
Write-ColorOutput ""
Write-ColorOutput "2. Test with the client:" $Yellow  
Write-ColorOutput "   volumecontrol-mcp-client" $White
Write-ColorOutput "   # OR: python volumecontrol_client.py" $Magenta
Write-ColorOutput ""
Write-ColorOutput "3. Use with MCP clients:" $Yellow
Write-ColorOutput "   Configure your MCP client to use: volumecontrol-mcp-server" $White
Write-ColorOutput ""
Write-ColorOutput "📚 For more information, see README.md" $Cyan
Write-ColorOutput "🐛 Issues? Check the troubleshooting section in README.md" $Cyan
Write-ColorOutput ""
Write-ColorOutput "Happy volume controlling! 🔊" $Magenta
