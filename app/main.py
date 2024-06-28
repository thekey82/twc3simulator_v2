from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()
wh = 0
wh_neu = False
session_energy_wh = 0.000
total = 0

shelly_ip = os.getenv('shelly_ip', '192.168.178.59')
# Define the data structure
class Vitals(BaseModel):
    contactor_closed: bool
    vehicle_connected: bool
    session_s: int
    grid_v: float
    grid_hz: float
    vehicle_current_a: float
    currentA_a: float
    currentB_a: float
    currentC_a: float
    currentN_a: float
    voltageA_v: float
    voltageB_v: float
    voltageC_v: float
    relay_coil_v: float
    pcba_temp_c: float
    handle_temp_c: float
    mcu_temp_c: float
    uptime_s: int
    input_thermopile_uv: int
    prox_v: float
    pilot_high_v: float
    pilot_low_v: float
    session_energy_wh: float
    config_status: int
    evse_state: int
    current_alerts: list

    
    
def get_shelly_current(shelly_ip):
    url = f"http://{shelly_ip}/rpc/Shelly.GetStatus"

    #{"ble":{},"cloud":{"connected":true},"input:0":{"id":0,"state":false},"mqtt":{"connected":false},"switch:0":{"id":0, "source":"HTTP_in", "output":false, "apower":0.0, "voltage":248.8, "current":0.000, "aenergy":{"total":7840.485,"by_minute":[0.000,0.000,0.000],"minute_ts":1719228000},"temperature":{"tC":57.9, "tF":136.2}},"sys":{"mac":"B0B21C102CC4","restart_required":false,"time":"13:20","unixtime":1719228008,"uptime":36301,"ram_size":261564,"ram_free":122896,"fs_size":458752,"fs_free":139264,"cfg_rev":11,"kvs_rev":0,"schedule_rev":1,"webhook_rev":0,"available_updates":{},"reset_reason":3},"wifi":{"sta_ip":"192.168.178.205","status":"got ip","ssid":"Garage","rssi":-37},"ws":{"connected":false}}
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["switch:0"]["current"]
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from Shelly device: {e}")

def get_shelly_total(shelly_ip):
    url = f"http://{shelly_ip}/rpc/Shelly.GetStatus"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["switch:0"]["aenergy"]["total"]
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from Shelly device: {e}")
        
    
def get_shelly_voltage(shelly_ip):
    url = f"http://{shelly_ip}/rpc/Shelly.GetStatus"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["switch:0"]["voltage"]
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from Shelly device: {e}")
def get_shelly_connected(shelly_ip):
    url = f"http://{shelly_ip}/rpc/Shelly.GetStatus"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["switch:0"]["output"] == True:
            power = True
        else:
            power = False
        return power
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from Shelly device: {e}")
@app.get("/api/1/vitals")
async def get_vitals():
    try:
        total = get_shelly_total(shelly_ip)
    except ValueError as e:
        return {"error": str(e)} 
    
    try:
        current = get_shelly_current(shelly_ip)
    if session_energy_wh == 0.000:
        wh = total 
    except ValueError as e:
        return {"error": str(e)}  
    if current <= 4.5:
        charging = False
        wh_neu = True
        session_energy_wh = 0.000
    else:
        charging = True
        session_energy_wh = total - wh
        print(total)
        print(wh)
    try:
        connected = get_shelly_connected(shelly_ip)
    except ValueError as e:
        return {"error": str(e)} 
    try:
        voltage = get_shelly_voltage(shelly_ip)
    except ValueError as e:
        return {"error": str(e)}    
        
    vitals = Vitals(
        contactor_closed=charging,
        vehicle_connected=connected,
        session_s=0,
        grid_v=voltage,
        grid_hz=49.828,
        vehicle_current_a=current,
        currentA_a=current,
        currentB_a=0.0,
        currentC_a=0.0,
        currentN_a=0.0,
        voltageA_v=voltage,
        voltageB_v=0.0,
        voltageC_v=0.0,
        relay_coil_v=11.9,
        pcba_temp_c=7.4,
        handle_temp_c=1.8,
        mcu_temp_c=15.2,
        uptime_s=26103,
        input_thermopile_uv=-176,
        prox_v=0.0,
        pilot_high_v=11.9,
        pilot_low_v=11.8,
        session_energy_wh=session_energy_wh,
        config_status=5,
        evse_state=1,
        current_alerts=[]
        # ... the other static stuf..contactor_closed=True,
    )
    return vitals
