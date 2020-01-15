from threading import Thread, Lock
import pandas as pd
from time import time, sleep
from jinja2 import Template
from os import path
from datetime import datetime
import RPi.GPIO as gpio

FILE_LOCK = Lock()
TEA_PATH = path.expanduser("~/tea")
BOUNCE_WAIT_TIME = 0.3
WRITE_TIME = 0

def gpio_loop(tea_path: str, pin: int):
    gpio.setwarnings(False)
    gpio.setmode(gpio.BOARD)
    gpio.setup(7, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.add_event_detect(7, gpio.RISING, callback=button_pressed)

def button_pressed(button):
    global WRITE_TIME
    global BOUNCE_WAIT_TIME

    if time() - WRITE_TIME < BOUNCE_WAIT_TIME:
        return
    else:
        WRITE_TIME = time()

    dates, vals = load_hist(TEA_PATH)
    today = datetime.today().strftime('%y-%m-%d')

    try:
        index = dates.index(today)
        vals[index] += 1
        print(f"Today: {vals[index]}")
    except:
        dates.append(today)
        vals.append(1)

    save_hist(TEA_PATH, dates, vals)

def html_loop(tea_path: str, repeat_time: int):
    while True:
        sleep(repeat_time)
        generate_html(tea_path)

def generate_html(tea_path: str):
    template_path = path.join(tea_path, "template.html")
    html_path = path.join(tea_path, "tea_graph.html")

    dates, vals = load_hist(tea_path)

    with open(template_path) as f:
        template = f.read()
    
    tmp = Template(template)
    html = tmp.render(dates=dates, vals=vals) 

    with open(html_path, 'w') as f:
        f.write(html)
    

def load_hist(tea_path: str) -> (list, list):
    log_path = path.join(tea_path, "test.csv")
    if path.exists(log_path):
        with FILE_LOCK, open(log_path) as f:
            df = pd.read_csv(f)
            dates = df.dates.tolist()
            vals = df.vals.tolist()
    else:
        dates = []
        vals = []
    return dates, vals

def save_hist(tea_path, dates, vals):
    log_path = path.join(tea_path, "test.csv")
    df = pd.DataFrame(data={"dates":dates, "vals":vals})
    with FILE_LOCK, open(log_path, 'w') as f:
        csv = df.to_csv(index=False)
        f.write(csv)

if __name__ == "__main__":
    generate_html(TEA_PATH)
    html_thread = Thread(target=html_loop, args = (TEA_PATH, 1))
    html_thread.start()
    gpio_loop(TEA_PATH, 7)
    while True:
        pass

