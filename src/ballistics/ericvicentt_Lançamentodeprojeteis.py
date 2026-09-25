from vpython import *

# 1. Configuração da Cena 3D
scene = canvas(title="<b>Simulador Cinemático: Decomposição Vetorial (vx e vy)</b>", width=800, height=500,align="left", center=vector(40, 30, 0), background=color.gray(0.9))
scene.camera.pos = vector(40, 30, 110)

# 2. Configuração dos Gráficos
# Gráfico de Posiçãhttps://glowscript.org/#/user/ericvicentt/folder/MyPrograms/program/Lan%C3%A7amentodeprojeteiso: Escala LIVRE (auto-scaling) para melhor visualização da parábola
g_yt = graph(title="Posição Vertical (y x t)", xtitle="Tempo t (s)", ytitle="Altura y (m)", width=300, height=200, align="right", xmin=0, xmax=12, ymin=-5, ymax=70)
curva_yt = gcurve(graph=g_yt, color=color.blue, width=2)

# Gráficos de Velocidade: Escala FIXA para não distorcer a leitura da aceleração
g_vx = graph(title="Velocidade Horizontal (vx x t)", xtitle="Tempo t (s)", ytitle="vx (m/s)", width=300, height=200, align="right-top", xmin=0, xmax=12, ymin=-5, ymax=55)
curva_vx = gcurve(graph=g_vx, color=color.cyan, width=2)

g_vy = graph(title="Velocidade Vertical (vy x t)", xtitle="Tempo t (s)", ytitle="vy (m/s)", width=300, height=200, align="right", xmin=0, xmax=12, ymin=-75, ymax=55)
curva_vy = gcurve(graph=g_vy, color=color.orange, width=2)

# 3. Parâmetros Físicos
g_val = -10
g = vector(0, g_val, 0)
dt = 0.01

# 4. Objetos do Cenário
chao = box(pos=vector(40, -1, 0), size=vector(250, 2, 20), color=vector(0.2, 0.6, 0.2))
projetil = sphere(pos=vector(0, 0, 0), radius=1.5, color=color.purple, make_trail=True, trail_type="points", interval=10)

# Vetores DECOMPOSTOS
seta_vx = arrow(pos=projetil.pos, axis=vector(0,0,0), color=color.cyan, shaftwidth=0.9, headwidth=2.2)
seta_vy = arrow(pos=projetil.pos, axis=vector(0,0,0), color=color.orange, shaftwidth=0.9, headwidth=2.2)

# Réguas do cenário
eixo_x = arrow(pos=vector(0,0,0), axis=vector(180,0,0), color=color.black, shaftwidth=0.2)
eixo_y = arrow(pos=vector(0,0,0), axis=vector(0,150,0), color=color.black, shaftwidth=0.2)
label(pos=vector(185, 0, 0), text="x (m)", box=False, line=False, color=color.black)
label(pos=vector(0, 155, 0), text="y (m)", box=False, line=False, color=color.black)

for x_tick in range(20, 161, 20):
    box(pos=vector(x_tick, 0, 0), size=vector(0.2, 2, 2), color=color.black)
    label(pos=vector(x_tick, -3, 0), text=str(x_tick), box=False, line=False, color=color.black, height=10)

for y_tick in range(20, 141, 20):
    box(pos=vector(0, y_tick, 0), size=vector(2, 0.2, 2), color=color.black)
    label(pos=vector(-4, y_tick, 0), text=str(y_tick), box=False, line=False, color=color.black, height=10)

# 5. Variáveis de Controle
lancando = False
v = vector(0,0,0)
t = 0

# === INTERFACE DE USUÁRIO (UI) ===
scene.append_to_caption('\n<b>Parâmetros Iniciais</b>\n')

def atualiza_y0(s):
    texto_y0.text = f" {s.value} m"
    if not lancando:
        projetil.pos.y = s.value
        seta_vx.pos = projetil.pos
        seta_vy.pos = projetil.pos

scene.append_to_caption('Altura Inicial (y₀): ')
sl_y0 = slider(min=0, max=80, value=0, step=1, length=200, bind=atualiza_y0)
texto_y0 = wtext(text=" 0 m")
scene.append_to_caption('\n')

def atualiza_v0(s):
    texto_v0.text = f" {s.value} m/s"

scene.append_to_caption('Velocidade (v₀): ')
sl_v0 = slider(min=10, max=50, value=40, step=1, length=200, bind=atualiza_v0)
texto_v0 = wtext(text=" 40 m/s")
scene.append_to_caption('\n')

def atualiza_angulo(s):
    texto_angulo.text = f" {s.value} graus"

scene.append_to_caption('Ângulo (θ): ')
sl_angulo = slider(min=0, max=90, value=60, step=1, length=200, bind=atualiza_angulo)
texto_angulo = wtext(text=" 60 graus")
scene.append_to_caption('\n\n')

def disparar(b):
    global lancando, t, v
    if lancando: return
    
    projetil.pos = vector(0, sl_y0.value, 0)
    projetil.clear_trail()
    curva_yt.data = []
    curva_vx.data = []
    curva_vy.data = []
    t = 0
    
    v0_mag = sl_v0.value
    theta = radians(sl_angulo.value)
    
    v = vector(v0_mag * cos(theta), v0_mag * sin(theta), 0)
    lancando = True

button(text="<b>▶ Iniciar Lançamento</b>", bind=disparar, color=color.white, background=color.blue)
scene.append_to_caption('\n\n<i>Note: O gráfico de posição vertical ajusta sua escala automaticamente, enquanto os gráficos de velocidade possuem escalas travadas para visualização precisa da aceleração.</i>')

# 6. Loop de Física
while True:
    rate(100)
    
    if lancando:
        v = v + g * dt
        projetil.pos = projetil.pos + v * dt
        t = t + dt
        
        seta_vx.pos = projetil.pos
        seta_vx.axis = vector(v.x * 0.4, 0, 0)
        
        seta_vy.pos = projetil.pos
        seta_vy.axis = vector(0, v.y * 0.4, 0)
        
        curva_yt.plot(t, projetil.pos.y)
        curva_vx.plot(t, v.x)
        curva_vy.plot(t, v.y)
        
        if projetil.pos.y < 0:
            lancando = False
            projetil.pos.y = 0
            seta_vy.axis = vector(0,0,0)