from vpython import *

# 1. Configuração da Cena 3D
scene = canvas(title="<b>Simulador Cinemático: Movimento Relativo e Inércia</b>", width=700, height=500, align="left", background=color.cyan)
scene.center = vector(0, 10, 0)
scene.range = 100 

# 2. Configuração do Gráfico Único de Posição
g_posicao = graph(
    title="Posição no Solo (x x t)", 
    xtitle="Tempo t (s)", 
    ytitle="Posição x (m)", 
    width=400, 
    height=300, 
    align="right", 
    xmin=0, xmax=15, 
    ymin=-200, ymax=250
)

# Duas curvas no MESMO gráfico
curva_x_trem = gcurve(graph=g_posicao, color=color.blue, width=3, label="Trem")
curva_x_pessoa = gcurve(graph=g_posicao, color=color.red, width=3, label="Pessoa")

# 3. Objetos do Cenário (Fixo no Solo)
chao = box(pos=vector(0, -2, 0), size=vector(500, 2, 20), color=vector(0.3, 0.7, 0.3))
trilho = box(pos=vector(0, -0.9, 0), size=vector(500, 0.2, 4), color=color.gray(0.5))

postes = []
for x in range(-200, 201, 30):
    postes.append(box(pos=vector(x, 5, -10), size=vector(0.5, 14, 0.5), color=color.orange))

# 4. Entidades Móveis
trem = box(pos=vector(-80, 2, 0), size=vector(140, 6, 8), color=color.blue, opacity=0.8)
pessoa = sphere(pos=vector(-80, 6, 0), radius=1.5, color=color.red)

# Vetores de Velocidade
seta_vtrem = arrow(pos=trem.pos, axis=vector(0,0,0), color=color.black, shaftwidth=0.6, headwidth=1.5)
seta_vpessoa = arrow(pos=pessoa.pos, axis=vector(0,0,0), color=color.red, shaftwidth=0.6, headwidth=1.5)

# 5. Variáveis de Física e Estado
rodando = False
dt = 0.02
t = 0
v_trem = 20 
v_pessoa_relativa = -10 
x_inicial = -80

caiu = False
v_inercia_chao = 0

# 6. Interface de Usuário (UI)
scene.append_to_caption('\n<b>Painel de Controle</b>\n\n')

def altera_vpessoa(s):
    global v_pessoa_relativa
    v_pessoa_relativa = s.value
    texto_vp.text = f" {v_pessoa_relativa} m/s"

scene.append_to_caption('Velocidade da Pessoa (Contra o trem): ')
sl_vp = slider(min=-50, max=0, value=-10, step=1, length=250, bind=altera_vpessoa)
texto_vp = wtext(text=" -10 m/s")
scene.append_to_caption('\n\n')

modo_referencial = "Observador no Solo (Externo)"
def altera_referencial(m):
    global modo_referencial
    modo_referencial = m.selected
    
scene.append_to_caption('<b>Referencial de Observação: </b>')
menu(choices=["Observador no Solo (Externo)", "Observador no Trem (Interno)"], bind=altera_referencial)
scene.append_to_caption('\n\n')

def play_pause(b):
    global rodando
    rodando = not rodando
    b.text = "<b>⏸ Pausar</b>" if rodando else "<b>▶ Iniciar</b>"

def resetar(b):
    global rodando, caiu, v_inercia_chao, t
    rodando = False
    caiu = False
    v_inercia_chao = 0
    t = 0
    curva_x_trem.data = []   # Limpa a curva do trem
    curva_x_pessoa.data = [] # Limpa a curva da pessoa
    btn_play.text = "<b>▶ Iniciar</b>"
    trem.pos.x = x_inicial
    pessoa.pos.x = x_inicial
    pessoa.pos.y = 6

btn_play = button(text="<b>▶ Iniciar</b>", bind=play_pause, color=color.white, background=color.blue)
scene.append_to_caption('  ')
button(text="<b>⟲ Resetar</b>", bind=resetar, color=color.black, background=color.orange)

label_ref = label(pos=vector(0, 38, 0), text="", box=False, color=color.black, height=18, font="sans")

# 7. Loop Principal
while True:
    rate(60)
    
    # Velocidade absoluta da pessoa enquanto está no trem
    v_pessoa_solo = v_trem + v_pessoa_relativa 
    
    if rodando:
        t += dt
        trem.pos.x += v_trem * dt
        
        # Verifica se a pessoa ainda está sobre o teto do trem (comprimento 140 m => +/- 70 m)
        if abs(pessoa.pos.x - trem.pos.x) <= 70 and not caiu:
            pessoa.pos.x += v_pessoa_solo * dt
            pessoa.pos.y = 6 
        else:
            # Lógica de Queda
            if not caiu:
                caiu = True
                v_inercia_chao = v_pessoa_solo 
                pessoa.pos.y = -0.5 
            
            pessoa.pos.x += v_inercia_chao * dt

        # === PLOTAGEM DAS DUAS POSIÇÕES NO MESMO GRÁFICO ===
        curva_x_trem.plot(t, trem.pos.x)
        curva_x_pessoa.plot(t, pessoa.pos.x)
        
        # Loop do cenário
        if trem.pos.x > 250:
            trem.pos.x = x_inicial
            pessoa.pos.x = x_inicial
            pessoa.pos.y = 6
            caiu = False
            t = 0
            curva_x_trem.data = []
            curva_x_pessoa.data = []

    # 8. Câmera e Vetores
    if modo_referencial == "Observador no Solo (Externo)":
        scene.center = vector(0, 10, 0)
        scene.range = 100 
        label_ref.pos = vector(0, 38, 0) 
        
        seta_vtrem.pos = trem.pos + vector(0, 4, 0)
        seta_vtrem.axis = vector(v_trem * 0.4, 0, 0)
        seta_vtrem.visible = True
        
        seta_vpessoa.pos = pessoa.pos + vector(0, 2.5, 0)
        
        if caiu:
            seta_vpessoa.axis = vector(v_inercia_chao * 0.4, 0, 0)
            status_pessoa = f"Caiu! Velocidade residual (inércia): {round(v_inercia_chao, 1)} m/s"
        else:
            seta_vpessoa.axis = vector(v_pessoa_solo * 0.4, 0, 0)
            status_pessoa = f"Velocidade da Pessoa no Solo (V.trem + V.relativa): {v_pessoa_solo} m/s"
            
        label_ref.text = f"REFERENCIAL: SOLO\nVelocidade do Trem: {v_trem} m/s\n{status_pessoa}"
        
    elif modo_referencial == "Observador no Trem (Interno)":
        scene.center = trem.pos + vector(0, 10, 0)
        scene.range = 70 
        label_ref.pos = trem.pos + vector(0, 30, 0)
        
        seta_vtrem.visible = False 
        
        seta_vpessoa.pos = pessoa.pos + vector(0, 2.5, 0)
        
        if caiu:
            v_relativa_chao = v_inercia_chao - v_trem
            seta_vpessoa.axis = vector(v_relativa_chao * 0.4, 0, 0)
            status_pessoa = f"Caiu do trem! Velocidade relativa vista pelo trem: {round(v_relativa_chao, 1)} m/s"
        else:
            seta_vpessoa.axis = vector(v_pessoa_relativa * 0.4, 0, 0)
            status_pessoa = f"Velocidade da Pessoa (V.relativa): {v_pessoa_relativa} m/s"
            
        label_ref.text = f"REFERENCIAL: TREM\nVelocidade do Trem: 0 m/s (Em repouso relativo)\n{status_pessoa}"