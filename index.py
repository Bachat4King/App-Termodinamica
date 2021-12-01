from flask import *
from flask_socketio import *
import numpy as np
import matplotlib.pyplot as plt
from pyXSteam.XSteam import XSteam
import os

PEOPLE_FOLDER = os.path.join('static')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

socketio = SocketIO(app)


@socketio.on('message')
def handle_message(message):
    datos = message
    if datos['potencia'] == '':
        datos['potencia'] = 0

    steam_table = XSteam(XSteam.UNIT_SYSTEM_MKS)


    p1 = float(datos['presion'])

    s1 = steam_table.sL_p(p1)

    T1 = steam_table.t_ps(p1, s1)

    h1 = steam_table.hL_p(p1)

    p2 = float(datos['presion2'])

    s2 = s1

    v = 1 / steam_table.rhoL_p(p1)

    w_p = v * (p2 - p1) * 100

    h2 = h1 + w_p

    T2 = steam_table.t_ph(p2, h2)

    h2dash = steam_table.hL_p(p2)

    s2dash = steam_table.sL_p(p2)

    T2dash = steam_table.t_ph(p2, h2dash)

    h3dash = steam_table.hV_p(p2)

    s3dash = steam_table.sV_p(p2)

    T3dash = T2dash

    p3 = p2

    T3 = float(datos['temperatura'])

    h3 = steam_table.h_pt(p3, T3)

    s3 = steam_table.s_pt(p3, T3)

    p4 = p3 / float(datos['division'])

    s4 = s3

    T4 = steam_table.t_ps(p4, s4)

    h4 = steam_table.h_pt(p4, T4)

    p5 = p4

    T5 = T3

    h5 = steam_table.h_pt(p5, T5)

    s5 = steam_table.s_pt(p5, T5)

    p6 = p1

    s6 = s5

    T6 = steam_table.t_ps(p6, s6)

    x6 = steam_table.x_ps(p6, s6)

    h6 = steam_table.h_px(p6, x6)



    w_HPt = h3 - h4

    w_LPt = h5 - h6

    q_H = (h3 - h2) + (h5 - h4)

    q_L = h6 - h1

    eta_th = (w_HPt + w_LPt - w_p) / q_H * 100


    flujo_masico = round(float(datos['potencia'])*1000 / round(float(w_HPt + w_LPt - w_p), 2), 2)

    font = {'family': 'Times New Roman',
            'size': 22}

    plt.figure(figsize=(15, 10))
    plt.title('Diagrama TS - Ciclo de Rankine con recalentamiento  (Ideal)')
    plt.rc('font', **font)

    plt.ylabel('Temperatura (C)')
    plt.xlabel('Entropia (s)')
    plt.xlim(-2, 10)
    plt.ylim(0, 600)

    T = np.linspace(0, 373.945, 400)  # range of temperatures
    # saturated vapor and liquid entropy lines
    svap = [s for s in [steam_table.sL_t(t) for t in T]]
    sliq = [s for s in [steam_table.sV_t(t) for t in T]]

    plt.plot(svap, T, 'b-', linewidth=2.0)
    plt.plot(sliq, T, 'r-', linewidth=2.0)

    plt.plot([s1, s2, s2dash, s3dash, s3, s4, s5, s6, s1], [T1, T2, T2dash, T3dash, T3, T4, T5, T6, T1], 'black',
             linewidth=2.0)

    plt.text(s1 - .1, T1,
             f'(1)\nT = {round(float(T1), 2)} C\nP = {round(float(p1), 1)} bar \nh = {round(float(h1), 1)} kJ/kg\n s = {round(float(s1), 3)} kJ/kgK',
             ha='right', backgroundcolor='white')
    plt.text(1.6, 60,
             f'(2)\nT = {round(float(T2), 2)} C\nP = {round(float(p2), 1)} bar \nh = {round(float(h2), 1)} kJ/kg',
             ha='left', backgroundcolor='white')
    plt.text(s2dash - .15, T2dash,
             f"(2')\nT = {round(float(T2dash), 2)} C\nP = {round(float(p2), 1)} bar \nh = {round(float(h2dash), 1)} kJ/kg \ns = {round(float(s2dash), 3)} kJ/kgK",
             ha='right', backgroundcolor='white')
    plt.text(6.3, T3 - 50,
             f'(3)\nT = {round(float(T3), 2)} C\nh = {round(float(h3), 1)} kJ/kg \ns = {round(float(s3), 3)} kJ/kgK',
             ha='right')
    plt.text(s4 - .1, T4 - 120,
             f'(4)\nT = {round(float(T4), 2)} C\nP = {round(float(p4), 1)} bar\nh = {round(float(h4), 1)} kJ/kg \ns = {round(float(s4), 3)} kJ/kgK',
             ha='right', backgroundcolor='white')
    plt.text(s3dash - .1, T3dash - 80,
             f"(3')\nh = {round(float(h3dash), 1)} kJ/kg \ns = {round(float(s3dash), 3)} kJ/kgK",
             ha='right')
    plt.text(s5 + .2, T5 - 70,
             f'(5)\nT = {round(float(T5), 2)} C\nh = {round(float(h5), 1)} kJ/kg \ns = {round(float(s5), 3)} kJ/kgK',
             ha='left', backgroundcolor='white')
    plt.text(s6 + .1, T6,
             f'(6)\nT = {round(float(T6), 2)} C\nh = {round(float(h6), 1)} kJ/kg \ns = {round(float(s6), 3)} kJ/kgK \nx = {round(float(x6), 3)}',
             ha='left', backgroundcolor='white')

    plt.savefig('static/grafico.jpg')

    dic = {"eficiencia": round(eta_th, 2), "wp": round(w_p, 2), "w_HPt": round(w_HPt,2), "w_LPt": round(w_LPt, 2), "q_H": round(q_H, 2), "q_L": round(q_L, 2), "flujo_masico": round(flujo_masico, 2), "WTT": round(float(w_HPt + w_LPt - w_p), 2)}

    send(dic, broadcast=True)


@app.route('/')
def index():
    try:
        os.remove('static/grafico.jpg')
    except:
        print('No file to delete')
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'grafico.jpg')
    return render_template("index.html", user_image=full_filename)


@app.route('/about.html')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host='localhost', port=8000)