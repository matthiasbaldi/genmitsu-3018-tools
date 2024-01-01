> More details: https://maruba.ch/blog/cnc-genmitsu-3018-proverv2-usbip

## Installation

```bash
cd ~
git clone https://github.com/matthiasbaldi/genmitsu-3018-tools.git
cd genmitsu-3018-tools/usbip

# Install dependencies
sudo apt update
sudo apt upgrade
sudo apt install usbip

# Install service
sudo cp usbipd.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable usbipd.service
sudo systemctl start usbipd.service
```

**Tested with:**

-   Windows PC as client
-   Candle GRBL Controller
-   LightBurn Laser Software
