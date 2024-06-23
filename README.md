# Dynmap Snapshotter V2
This tool allows you to capture full, large snapshots of your Minecraft Dynmap from the command line or using a graphical user interface



## Features 
- Automatic uploads of snapshot to discord server
- Set new background color with hex code
- Resize the output image 


## Installation
I reccommend using Python 3.10, but any version might work. If you encounter issues on different versions of python then please create a virtual environment using a version of Python 3.10.

In order to install, clone the repo using Git, enter repo directory and install requirements with pip.
```
git clone https://github.com/verosment/dynmap-snapshotter-v2.git
```
```
cd dynmap-snapshotter-v2
```
```
pip install -r requirements.txt
```

## Usage
### **Taking a snapshot**
Capture a snapshot from the commandline
1. Run the script using `python main.py`

2. Fill in required parameters:
- Tiles Directory: Point to where your Dynmap tiles are saved in your server files.
  Example: `{server-directory}/plugins/dynmap/web/tiles`
- World: Select the desired Minecraft world
- Map: Choose the map type (t = orthographic terrain, flat = top down, ct = caves rendered orthographically)

---

## Command line Usage
### **Taking a snapshot**
Capture a snapshot from the commandline
1. Download dynmap-snapshotter


2. Run the script<br/>
    EITHER in interactive mode<br/>
    `python snapshotter.py --interactive`
    
    OR set required arguments yourself<br/>
    `python snapshotter.py --folder plugins/dynmap/web/tiles --world world --map flat`


3. Enjoy your snapshot <br/>
	Find your snapshot in the `snapshots` folder where `dynmap-snapshotter.py` was saved

### **Daily snapshots with crontab**
Use crontab to setup daily snapshots 
1. Open the crontab editor<br/>
    `crontab -e`

2. Create a new entry<br/>
	This will create a snapshot of world:flat every day at 00:00<br/>
	```
    0 0 * * * python /home/user/snapshotter.py --folder /srv/minecraft/plugins/dynmap/web/tiles --world the_nether --map flat
    ```
    remeber to set your own arguments and flags

### **Posting to discord**
Enable posting to discord via a webhook

1. Enable webhook integration in channel settings

2. Copy your webhook url

3. Add arguments when running the script<br/>
    
    `python dynmap-snapshotter.py ... --discord-webhook-url [webhook url]`
    
    you may also set the `--discord-message` argument to provide a custom message
    
### **All arguments**
This is the help message for the script
```
> python dynmap-snapshotter.py --help

usage: dynmap-snapshotter.py [-h] [--folder FOLDER] [--world WORLD] [--map MAP] [--interactive] [--scale SCALE] [--fixed-tile-size FIXED_TILE_SIZE]
                           [--color-hex COLOR_HEX] [--discord-message DISCORD_MESSAGE] [--discord-webhook-url DISCORD_WEBHOOK_URL]

optional arguments:
  -h, --help            show this help message and exit
  --folder FOLDER       specify the absolute path for folder where dynmap tiles are stored. this is usually [server folder]/plugins/dynmap/web/tiles.
  --world WORLD         world to take snapshot of
  --map MAP             map to take snapshot of
  --interactive         helps user decide arguments trough prompts
  --scale SCALE         resize the snapshot with a decimal point number
  --fixed-tile-size FIXED_TILE_SIZE
                        resize the snapshot with setting a new tile size
  --color-hex COLOR_HEX
                        hex value of color to apply to background.
  --discord-message DISCORD_MESSAGE
                        message to go along with discord post snapshot
  --discord-webhook-url DISCORD_WEBHOOK_URL
                        discord webhook url to post snapshot to.

```


## Credit
[Kasperjha](https://github.com/kasperjha) for creating and writing the original code repository

---

Thanks to https://github.com/GuyInGrey for helping me understand the dynmap api :)

Project inspired by https://github.com/xtotdam/dynmap-assemble
