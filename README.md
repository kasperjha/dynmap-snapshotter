# dynmap-snapshotter
Use this script to assemble one large *snapshot* of your minecraft dynmap.



## Features 
- Automatic uploads of snapshot to discord server
- Set new background color with hex code
- Resize the output image 


## Usage
### **Taking a snapshot**
Capture a snapshot from the commandline
1. Download dynmap-snapshotter


2. Run the script<br/>
    EITHER in interactive mode<br/>
    `python dynmap-snapshotter.py --interactive`
    
    OR set required arguments yourself<br/>
    `python dynmap-snapshotter.py --folder plugins/dynmap/web/tiles --world world --map flat`


3. Enjoy your snapshot <br/>
	Find your snapshot in the `snapshots` folder where `dynmap-snapshotter.py` was saved


### **Daily snapshots with crontab**
Use crontab to setup daily snapshots 
1. Open the crontab editor<br/>
    `crontab -e`

2. Create a new entry<br/>
	This will create a snapshot of world:flat every day at 00:00<br/>
	```
    0 0 * * * python /home/user/dynmap-snapshotter.py --folder /srv/minecraft/plugins/dynmap/web/tiles --world the_nether --map flat
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

Thanks to https://github.com/GuyInGrey for helping me understand the dynmap api :)

Project inspired by https://github.com/xtotdam/dynmap-assemble