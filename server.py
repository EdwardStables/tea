from threading import Thread, Lock
import pandas as pd
from time import sleep
from jinja2 import Template
from os import path
#from gpiozero import Button
from datetime import datetime

FILE_LOCK = Lock()


#def gpio_loop(tea_path: str, pin: int):
#    button = Button(2) 
#    button.when_pressed = button_pressed(button, tea_path)
#
#def button_pressed(button, tea_path):
#    hist = load_hist(tea_path)
#    today_index = hist.index
#    with FILE_LOCK, open(tea_path, 'w') as f:
        

def html_loop(tea_path: str, repeat_time: int):
    while True:
        sleep(repeat_time)
        generate_html(tea_path)

def generate_html(tea_path: str):
    print("Generating html...")
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

if __name__ == "__main__":
    tea_path = path.expanduser("~/Documents/repos/tea")
    generate_html(tea_path)
    html_thread = Thread(target=html_loop, args = (tea_path, 10))
    html_thread.start()
    #gpio_loop(tea_path, 7)
