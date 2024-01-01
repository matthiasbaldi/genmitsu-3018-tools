> More details: https://maruba.ch/blog/cnc-genmitsu-3018-proverv2-usbip

Create file: `sudo vim /lib/systemd/system/usbipd.service`

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable usbipd
sudo systemctl start usbipd
```

**Tested with:**

-   Windows PC as client
-   Candle GRBL Controller
-   LightBurn Laser Software
