### general info
port
> /dev/tty.usbserial-0166DBCA

### firmware commands
flashing
```
esptool.py --port /dev/tty.usbserial-0166DBCA --chip esp32 write_flash -z 0x1000 ./downloads/esp32-20210623-v1.16.bin
```

### Picocom
```
picocom -b 115200 /dev/tty.usbserial-0166DBCA
```

to exit
> C-a
>
> C-x

### one-liners
```
f = open('boot.py'); print(f.read()); f.close();
```

```
import network; wlan = network.WLAN(network.STA_IF); wlan.ifconfig();
```

