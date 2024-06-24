# twc3simulator (Tesla Wall Box 3 Simulator)

This program simulates the API output of a Tesla Wallbox 3.

It basically just fakes the output while using information from a Tasmota device to fill the current.

![](media/api.png)

I use this as a workaround to get evcc working with the mobile charger, as evcc requires a proper charger. The twc3 template is special because it lets evcc use Tesla's own api to start/stop and adjust the current level. 


## requirements

- Tasmota outlet to grep the current from. - Something like 


## Installation

via docker:

    docker run --name twc3simulator_v2 -p 80:80 -e SHELLY_IP=10.10.10.10 thekey82/twc3simulator_v2

where TASMOTA_IP ist the ip of the tasmota device where the current information should come from.

or as part of your evcc so you could access it via port 80 without exposint this port at all just with the name of the container 

    services:
    twc3sim:
      container_name: twc3simv2
      image: thekey82/twc3simulator_v2
      environment:
        - "SHELLY_IP=192.168.178.205"
      restart: unless-stopped
      
full example in the example folder


for tweaking:

first clone it to the machine you want to run it

    git clone https://github.com/thekey82/twc3simulator_v2.git


## set the correct ip of your tasmota device

    cd twc3simulator_v2
    
for this edit the script and set the proper ip address

    vim app/main.py

or set the IP as Envirnment var.
    
## run it

to run it native you have to first install the requirements with pip or your package manager

native:

    pip3 install -r requirements.txt
    sudo uvicorn app.main:app --reload --host 0.0.0.0 --port 80

   
## validate

if it's running properly you should get something back when looking at

http://<ip>/api/1/vitals
