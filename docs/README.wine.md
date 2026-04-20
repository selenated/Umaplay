# Running Umaplay on Linux

This guide explains how to run Umaplay on Linux, either natively or using Wine for the Windows version of Umamusume: Pretty Derby.

## Prerequisites

- Linux distribution (Ubuntu, Fedora, Arch, etc.)
- Miniconda or Anaconda
- Git
- Wine 8.0+ (if running Windows version of the game)

## Quick Start: Native Linux Testing

### 1. Install Miniconda (if not already installed)

```bash
# Download and install Miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh

# Initialize conda for your shell
~/miniconda3/bin/conda init bash
# Then restart your terminal or run:
source ~/.bashrc
```

### 2. Clone and Set Up Umaplay

```bash
cd ~
git clone https://github.com/Magody/Umaplay.git
cd Umaplay

# Create conda environment
conda create -n env_uma python=3.10

# Activate environment
conda activate env_uma

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Linux System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get install xdotool python3-tk python3-dev

# Fedora
sudo dnf install xdotool python3-tkinter python3-devel

# Arch
sudo pacman -S xdotool tk
```

### 4. Run Test Script

```bash
# Verify everything works
./test_linux_venv.sh
```

## Running with Wine (Windows Game Version)

If you want to run the Windows version of Umamusume through Wine:

### 1. Install Wine

**Ubuntu/Debian:**
```bash
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -cs)/winehq-$(lsb_release -cs).sources
sudo apt update
sudo apt install --install-recommends winehq-stable
```

**Fedora:**
```bash
sudo dnf config-manager --add-repo https://dl.winehq.org/wine-builds/fedora/$(rpm -E %fedora)/winehq.repo
sudo dnf install winehq-stable
```

**Arch Linux:**
```bash
sudo pacman -S wine winetricks
```

### 2. Install Winetricks and Required Components

```bash
# Install winetricks if not already installed
sudo apt install winetricks  # Ubuntu/Debian
# or
sudo dnf install winetricks  # Fedora
# or
yay -S winetricks           # Arch

# Install required Windows components
winetricks corefonts
winetricks vcrun2019
winetricks d3dx9
```

### 3. Set Up Wine Prefix (Optional but Recommended)

Create a dedicated Wine prefix for Umamusume:

```bash
export WINEPREFIX="$HOME/.wine-umamusume"
export WINEARCH=win64
wineboot -u
```

Add these to your `~/.bashrc` or `~/.zshrc` to make them permanent:
```bash
echo 'export WINEPREFIX="$HOME/.wine-umamusume"' >> ~/.bashrc
echo 'export WINEARCH=win64' >> ~/.bashrc
source ~/.bashrc
```

### 4. Install Python in Wine

Download Python 3.10 Windows installer:
```bash
cd ~/Downloads
wget https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
wine python-3.10.11-amd64.exe
```

During installation:
- Check "Add Python to PATH"
- Choose "Install for all users"
- Complete the installation

### 5. Install Umamusume via Steam in Wine

If you're using Steam:

```bash
# Install Steam in Wine
winetricks steam

# Launch Steam
wine ~/.wine/drive_c/Program\ Files\ \(x86\)/Steam/Steam.exe

# Log in and install Umamusume: Pretty Derby
```

### 6. Clone and Set Up Umaplay

```bash
cd ~
git clone https://github.com/Magody/Umaplay.git
cd Umaplay
git checkout wine-support  # Use the Wine support branch
```

### 7. Install Python Dependencies in Wine

```bash
# Use Wine's Python to install dependencies
wine python -m pip install --upgrade pip
wine python -m pip install -r requirements.txt
```

**Note:** If you encounter issues with some packages, try:
```bash
wine python -m pip install --no-cache-dir -r requirements.txt
```

## Running Umaplay

### Launch Script

Create a launch script `run_umaplay_wine.sh`:

```bash
#!/bin/bash
export WINEPREFIX="$HOME/.wine-umamusume"
export WINEARCH=win64

cd ~/Umaplay
wine python main.py
```

Make it executable:
```bash
chmod +x run_umaplay_wine.sh
```

### Running the Bot

1. **Start Umamusume** (via Steam in Wine or your preferred method)
2. **Run Umaplay:**
   ```bash
   ./run_umaplay_wine.sh
   ```
3. **Access Web UI:** Open browser to `http://127.0.0.1:8000/`
4. **Configure settings** in the Web UI
5. **Press F2** to start/stop the bot

## Configuration Tips

### Window Title Detection

Under Wine, window titles might differ. To find your window title:

```bash
wine reg query 'HKEY_CURRENT_USER\Software\Wine' /s
# or use xwininfo on Linux
xwininfo -tree -root | grep -i uma
```

Update the window title in the Web UI accordingly.

### Performance Optimization

For better performance under Wine:

1. **Use DXVK** (DirectX to Vulkan translation):
   ```bash
   winetricks dxvk
   ```

2. **Enable Esync/Fsync:**
   ```bash
   export WINEESYNC=1
   # or for newer kernels
   export WINEFSYNC=1
   ```

3. **Disable Wine debugging:**
   ```bash
   export WINEDEBUG=-all
   ```

Add these to your launch script for permanent effect.

## Troubleshooting

### Native Linux Issues

**Issue: "No keyboard library available"**
- Expected on Linux without Wine
- Hotkey manager will use pynput instead

**Issue: Import errors**
- Run: `./test_linux_venv.sh` to verify setup
- Ensure all dependencies installed: `pip install -r requirements.txt`

**Issue: Window not detected**
- Verify xdotool is installed: `which xdotool`
- Test window detection: `xdotool search --name "uma"`

### Wine-Specific Issues

### Issue: Hotkeys (F2, F7, F8, F9) Not Working

Umaplay automatically detects Wine and switches to `pynput` for hotkey management. If hotkeys still don't work:

1. Ensure `pynput` is installed:
   ```bash
   wine python -m pip install pynput
   ```

2. Check Wine logs for errors:
   ```bash
   export WINEDEBUG=+all
   wine python main.py
   ```

### Issue: Window Not Found

1. Verify the window title matches exactly
2. Try using `pygetwindow` to list windows:
   ```bash
   wine python -c "import pygetwindow as gw; print([w.title for w in gw.getAllWindows()])"
   ```

### Issue: OCR Not Working Properly

PaddleOCR might have issues under Wine. Try:

```bash
wine python -m pip uninstall -y paddlepaddle paddleocr
wine python -m pip install paddlepaddle paddleocr --no-cache-dir
```

### Issue: Import Errors

If you get import errors for Windows-specific modules:

```bash
wine python -m pip install pywin32-ctypes
```

## Native Linux Alternative

If Wine causes too many issues, consider running Umamusume in a Windows VM and using Umaplay's **client-only mode** from your Linux host. See `README.md` for details on client-server setup.

## Known Limitations

- Some Windows-specific features may not work perfectly under Wine
- Performance may be slightly lower than native Windows
- Hotkey polling (`is_pressed`) has limited support with pynput backend
- Some anti-cheat systems may detect Wine (though Umamusume generally works fine)

## Getting Help

- **Discord:** https://discord.gg/JtJfuADDYz
- **GitHub Issues:** https://github.com/Magody/Umaplay/issues
- **Wine AppDB:** Check Wine compatibility reports for Umamusume

## Contributing

Found a Wine-specific issue or improvement? Please report it on GitHub with:
- Your Linux distribution and version
- Wine version (`wine --version`)
- Python version in Wine (`wine python --version`)
- Full error logs

---

**Last Updated:** January 2026  
**Wine Version Tested:** 9.0  
**Status:** Experimental - feedback welcome!
