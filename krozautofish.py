import tkinter as tk
from tkinter import ttk
import pyautogui, time, random, json, threading, win32gui, win32con, keyboard
from PIL import Image, ImageTk

CONFIG_FILE="config.json"
running=False
target_hwnd=None

def load_config():
    try:
        with open(CONFIG_FILE,"r") as f:
            return json.load(f)
    except:
        return {"sens":16,"threshold":35,"sell_command":"/pesca sellall","stop_repeats":4,"hotkey":"f8"}

def save_config(data):
    with open(CONFIG_FILE,"w") as f:
        json.dump(data,f,indent=4)

cfg=load_config()

def list_windows():
    wins=[]
    def enum(h,_):
        if win32gui.IsWindowVisible(h):
            t=win32gui.GetWindowText(h)
            if t.strip():
                wins.append((hex(h),t))
    win32gui.EnumWindows(enum,None)
    return wins

def auto_refresh(event=None):
    menu["values"]=[f"{title} ({hwnd})" for hwnd,title in list_windows()]

def select_window(event=None):
    global target_hwnd
    sel=menu.get()
    if "(" in sel:
        target_hwnd=int(sel.split("(")[-1].replace(")",""),16)

def mc_click():
    if target_hwnd:
        win32gui.PostMessage(target_hwnd,win32con.WM_RBUTTONDOWN,win32con.MK_RBUTTON,0)
        win32gui.PostMessage(target_hwnd,win32con.WM_RBUTTONUP,0,0)

def mc_sell():
    if not target_hwnd:return
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYDOWN,0x54,0)
    win32gui.PostMessage(target_hwnd, win32con.WM_KEYUP,0x54,0)
    time.sleep(0.08)
    for c in entry_cmd.get():
        win32gui.PostMessage(target_hwnd,win32con.WM_CHAR,ord(c),0)
    win32gui.PostMessage(target_hwnd,win32con.WM_KEYDOWN,0x0D,0)
    win32gui.PostMessage(target_hwnd,win32con.WM_KEYUP,0x0D,0)
    log("SELL executed")

def bot():
    global running
    log("Starting in 5 seconds…")
    time.sleep(5)
    x,y=pyautogui.position()
    base=pyautogui.pixel(x,y)[0]
    sens=sens_var.get()
    th=th_var.get()
    stoplim=int(entry_stop.get())
    count=0
    hits=[]
    sell_timer=time.time()+random.randint(120,240)
    log("BOT RUNNING")
    while running:
        x,y=pyautogui.position()
        diff=abs(pyautogui.pixel(x,y)[0]-base)
        if time.time()>sell_timer:
            mc_sell()
            sell_timer=time.time()+random.randint(120,240)
        if diff>sens and diff>th:
            ts=time.time()
            hits.append(ts)
            hits=[t for t in hits if ts-t<=5]
            count+=1
            log(f"Fish {count} Δ{diff}")
            if stoplim>0 and len(hits)>=stoplim:
                log("Auto STOP triggered")
                running=False
                break
            time.sleep(0.2+random.random()*0.3)
            mc_click()
            time.sleep(0.9+random.random()*0.3)
            mc_click()
            time.sleep(1.3)
            base=pyautogui.pixel(x,y)[0]
        time.sleep(0.04)
    log("BOT STOPPED")

def toggle_hotkey():
    global running
    if running:
        running=False
        log("BOT OFF")
    else:
        running=True
        threading.Thread(target=bot,daemon=True).start()
        log("BOT ON")

def start_button():
    global running
    if running:
        running=False
        time.sleep(0.3)
    running=True
    save_config({"sens":sens_var.get(),"threshold":th_var.get(),"sell_command":entry_cmd.get(),"stop_repeats":entry_stop.get(),"hotkey":entry_key.get()})
    threading.Thread(target=bot,daemon=True).start()
    log("BOT STARTED/RESTARTED")

def stop():
    global running
    running=False
    log("BOT STOPPED")

app=tk.Tk()
app.resizable(True, True) 
app.minsize(500,750)      
app.title("KrozAutofisher")
app.geometry("500x750")
app.iconbitmap("logo.ico")
app.configure(bg="#0F1116")
header=tk.Frame(app,bg="#0F1116")
header.pack(pady=15)

img=Image.open("giorno.png").resize((45,45))
photo=ImageTk.PhotoImage(img)

tk.Label(header,image=photo,bg="#0F1116").pack(side="right",padx=10)
tk.Label(header,text="KROZAUTOFISHER",font=("Segoe UI",22,"bold"),foreground="#4CD3FF",background="#0F1116").pack(side="left")

ttk.Separator(app,orient="horizontal").pack(fill="x",pady=8)

ttk.Label(app,text="Select Target Window",foreground="white",background="#0F1116",font=("Segoe UI",11,"bold")).pack()
menu=ttk.Combobox(app,width=55)
menu.pack(pady=6)
menu.bind("<Button-1>", auto_refresh)
menu.bind("<<ComboboxSelected>>", select_window)

ttk.Separator(app,orient="horizontal").pack(fill="x",pady=10)

ttk.Label(app,text="Bite Sensitivity (recommended 10–18)",foreground="#4CD3FF",background="#0F1116",font=("Segoe UI",10,"bold")).pack(pady=4)
lbl_sens=tk.Label(app,text=f"Value: {cfg['sens']}",foreground="white",background="#0F1116",font=("Segoe UI",10))
lbl_sens.pack()
sens_var=tk.IntVar(value=cfg["sens"])
def update_sens(v): lbl_sens.config(text=f"Value: {v}")
tk.Scale(app,from_=1,to=50,orient="horizontal",variable=sens_var,length=350,bg="#0F1116",highlightthickness=0,troughcolor="#1A1F29",command=update_sens).pack(pady=3)

ttk.Label(app,text="Min Color Change to Trigger Bite (recommended 30-40)",foreground="#4CD3FF",background="#0F1116",font=("Segoe UI",10,"bold")).pack(pady=4)
lbl_th=tk.Label(app,text=f"Value: {cfg['threshold']}",foreground="white",background="#0F1116",font=("Segoe UI",10))
lbl_th.pack()
th_var=tk.IntVar(value=cfg["threshold"])
def update_th(v): lbl_th.config(text=f"Value: {v}")
tk.Scale(app,from_=1,to=100,orient="horizontal",variable=th_var,length=350,bg="#0F1116",highlightthickness=0,troughcolor="#1A1F29",command=update_th).pack(pady=3)

ttk.Separator(app,orient="horizontal").pack(fill="x",pady=14)

ttk.Label(app,text="AutoStop after X false positives (0 for disabled)",foreground="white",background="#0F1116",font=("Segoe UI",9,"bold")).pack(pady=3)
entry_stop=ttk.Entry(app,width=10); entry_stop.insert(0,cfg["stop_repeats"]); entry_stop.pack(pady=2)

ttk.Label(app,text="Sell Command",foreground="white",background="#0F1116",font=("Segoe UI",10,"bold")).pack(pady=4)
entry_cmd=ttk.Entry(app,width=30); entry_cmd.insert(0,cfg["sell_command"]); entry_cmd.pack()

ttk.Label(app,text="Hotkey Toggle (ON/OFF)",foreground="white",background="#0F1116",font=("Segoe UI",10,"bold")).pack(pady=6)
entry_key=ttk.Entry(app,width=10); entry_key.insert(0,cfg.get("hotkey","f8")); entry_key.pack()

ttk.Separator(app,orient="horizontal").pack(fill="x",pady=14)

ttk.Button(app,text="▶ START / RESTART (F8 DEFAULT)",command=start_button).pack(pady=10,ipadx=40,ipady=6)
ttk.Button(app,text="■ STOP",command=stop).pack(ipadx=50,ipady=6)

ttk.Separator(app,orient="horizontal").pack(fill="x",pady=12)

box=tk.Text(app,height=15,width=60,bg="#161A22",fg="#00F1FF",insertbackground="white")
box.pack(pady=10, fill="both", expand=True)


def log(t):
    box.insert("end",t+"\n"); box.see("end")

keyboard.add_hotkey(entry_key.get(), toggle_hotkey)
app.mainloop()
keyboard.wait()
