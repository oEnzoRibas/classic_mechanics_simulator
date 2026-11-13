# Confere se as velocidades digitadas são números finitos.

from math import isfinite

# Distância em km e quantidade de quadros da animação.

DISTANCIA_INICIAL = 60.0

FPS = 60

QUADROS_POR_EXECUCAO = 1200  # A simulação dura aprox. 20 seg na tela.

# Enunciado que aparece no flashcard.

PROBLEMA_ORIGINAL = (

    'Dois trens, ambos se movendo a uma velocidade de 30 km/h, trafegam '

    'em sentidos opostos na mesma linha férrea retilínea. Um pássaro parte '

    'da extremidade dianteira de um dos trens, quando estão separados por '

    '60 km, voando a 60 km/h, e se dirige em linha reta para o outro trem. '

    'Quando chegar ao outro trem, o pássaro faz meia-volta e se dirige para '

    'o primeiro trem, e assim por diante. Qual é a distância que o pássaro '

    'percorre até os trens colidirem?'

)

# Passos da resolução, usando os valores do problema original.

PASSOS_ORIGINAIS = [

    ('1. Organize os dados',

     'Separação inicial: <b>60 km</b>. Velocidades dos trens: '

     '<b>30 km/h</b> cada. Velocidade do pássaro: <b>60 km/h</b>.'),

    ('2. Some as velocidades dos trens',

     'Os trens se aproximam em sentidos opostos. A distância entre eles '

     'diminui a <b>30 + 30 = 60 km/h</b>.'),

    ('3. Calcule o tempo até o encontro',

     '<b>t = distância inicial / velocidade de aproximação</b><br>'

     't = 60 km / 60 km/h = <b>1 hora = 60 minutos</b>.'),

    ('4. Calcule a distância percorrida pelo pássaro',

     'O pássaro voa durante a mesma 1 hora, mantendo sua rapidez, '

     'mesmo quando muda de sentido.<br>'

     '<b>d = velocidade × tempo = 60 km/h × 1 h = 60 km.</b>'),

    ('5. Entenda o resultado',

     'Não é necessário somar todas as idas e voltas: basta conhecer o '

     'tempo total de voo. O pássaro termina na posição <b>30 km</b>, '

     'mas a distância total que percorreu é <b>60 km</b>.'),

]

# Guarda os dados e faz as contas do movimento dos trens e do pássaro.

class SimulacaoTrens:

    # Começa com as velocidades do problema original, em km/h.

    def __init__(self, velocidade_a=30, velocidade_b=30, velocidade_passaro=60):

        self.configurar(velocidade_a, velocidade_b, velocidade_passaro)

    # Confere as velocidades escolhidas antes de começar outra simulação.

    def configurar(self, velocidade_a, velocidade_b, velocidade_passaro):

        valores = [float(v) for v in (velocidade_a, velocidade_b, velocidade_passaro)]

        if not all(isfinite(v) for v in valores):

            raise ValueError('Digite três velocidades numéricas finitas.')

        a, b, p = valores

        if a < 0 or b < 0 or a + b <= 0:

            raise ValueError('Os trens precisam ter velocidades não negativas; ao menos um deve se mover.')

        if p <= max(a, b):

            raise ValueError('Para ir e voltar entre os trens, o pássaro deve ser mais rápido que ambos.')

        # Soma as velocidades dos trens e calcula o tempo até colidirem, em minutos.

        tempo_final = (DISTANCIA_INICIAL * 60) / (a + b)

        if not isfinite(tempo_final) or tempo_final <= 0:

            raise ValueError('Escolha velocidades de ordem de grandeza menor.')

        # Salva os valores e converte as velocidades de km/h para km/min.

        self.velocidade_a, self.velocidade_b, self.velocidade_passaro = valores

        self.v_a, self.v_b, self.v_p = a / 60, -b / 60, p / 60

        self.tempo_final = tempo_final

        self.passo = tempo_final / QUADROS_POR_EXECUCAO

        self.reiniciar()

    # Zera o tempo e coloca o pássaro de volta no trem A, com tudo parado.

    def reiniciar(self):

        self.tempo = 0.0

        self.x_passaro = 0.0

        self.sentido = 1

        self.rodando = False

    # Posição do trem A em cada instante.

    @property

    def x_a(self):

        return self.v_a * self.tempo

    # O trem B parte dos 60 km e anda no sentido contrário.

    @property

    def x_b(self):

        return DISTANCIA_INICIAL + self.v_b * self.tempo

    # Confere se os trens já se encontraram.

    @property

    def finalizada(self):

        return self.tempo >= self.tempo_final

    # Alterna entre começar e pausar a simulação.

    def iniciar_parar(self):

        if not self.finalizada:

            self.rodando = not self.rodando

    # Atualiza o movimento e guarda os pontos do pássaro para o gráfico.

    def avancar(self):

        if not self.rodando or self.finalizada:

            return []

        # Limita o passo para a animação não passar do instante da colisão.

        fim = min(self.tempo_final, self.tempo + self.passo)

        if self.tempo_final - fim < self.passo * 1e-8:

            fim = self.tempo_final

        instante = self.tempo

        pontos = []

        # Calcula cada ida e volta que acontece dentro desse passo.

        while instante < fim:

            a = self.v_a * instante

            b = DISTANCIA_INICIAL + self.v_b * instante

            # Infinitas voltas perto da colisão, por isso o limite de 1e-8 km.

            if b - a < 1e-8:

                self.x_passaro = self.v_a * fim

                break

            # Tempo que falta para o pássaro chegar ao trem de cada lado.

            if self.sentido > 0:

                ate_encontro = max(0.0, (b - self.x_passaro) / (self.v_p - self.v_b))

            else:

                ate_encontro = max(0.0, (self.x_passaro - a) / (self.v_p + self.v_a))

            # Move só até o encontro, para o pássaro não atravessar o trem.

            restante = fim - instante

            trecho = min(restante, ate_encontro)

            self.x_passaro += self.sentido * self.v_p * trecho

            instante += trecho

            if ate_encontro <= restante:

                # Guarda a posição do encontro e inverte o sentido do pássaro.

                self.x_passaro = (DISTANCIA_INICIAL + self.v_b * instante

                                  if self.sentido > 0 else self.v_a * instante)

                pontos.append((instante, self.x_passaro))

                self.sentido = -self.sentido

        # Para a simulação quando os trens colidem.

        self.tempo = fim

        if self.finalizada:

            self.x_passaro = self.x_a

            self.rodando = False

        # Acrescenta a posição do pássaro no fim do passo.

        pontos.append((self.tempo, self.x_passaro))

        return pontos

# Mostra os números com vírgula e a quantidade escolhida de casas decimais.

def formatar_numero(valor, casas=2):

    return ('{:.' + str(casas) + 'f}').format(valor).replace('.', ',')

# Converte os minutos da simulação para horas, minutos e segundos.

def formatar_relogio(minutos):

    segundos = int(round(minutos * 60))

    horas, segundos = divmod(segundos, 3600)

    minutos, segundos = divmod(segundos, 60)

    return '{:02d}:{:02d}:{:02d}'.format(horas, minutos, segundos)

# Monta o flashcard para abrir uma etapa da resolução por clique.

def html_flashcard():

    html = (

        '<details style="white-space:normal;max-width:1200px;margin:12px 0;'

        'padding:14px 18px;border:1px solid #cbd5e1;border-radius:12px;'

        'background:#f8fafc;color:#172033;font-family:Arial,sans-serif;line-height:1.5;">'

        '<summary style="cursor:pointer;font-weight:bold;">'

        'Flashcard — clique para abrir o problema original</summary>'

        '<p>' + PROBLEMA_ORIGINAL + '</p>'

        '<p style="color:#526078;font-size:13px;">'

        'Esta resolução usa os valores originais, mesmo que você altere as velocidades da simulação. '

        'Clique nas etapas para revelar a solução.</p>'

    )

    # Cada etapa fica dentro da anterior para aparecer na ordem.

    for titulo, explicacao in PASSOS_ORIGINAIS:

        html += (

            '<details style="margin:10px 0 0;padding:10px 14px;'

            'border-left:3px solid #2563eb;background:white;border-radius:6px;">'

            '<summary style="cursor:pointer;font-weight:bold;">'

            + titulo + '</summary><p>' + explicacao + '</p>'

        )

    # Fecha as etapas e termina o cartão.

    html += '</details>' * (len(PASSOS_ORIGINAIS) + 1)

    return html

# Cria a tela, os botões e o gráfico no navegador.

def main():

    import vpython as vp

    # Configuração da tela preta e da câmera.

    modelo = SimulacaoTrens()

    # Tela independente para os controles: ela continua visível nos três modos.
    ui_canvas = vp.canvas(
        title='<b>Trens e pássaro — movimento em 3D</b><br>',
        width=1200, height=1, align='none', background=vp.color.white)

    # A cena mantém exatamente o tamanho e o alinhamento originais.
    scene = vp.canvas(
        title='', width=560, height=350, align='left', background=vp.color.black)

    scene.autoscale = False

    scene.userspin = False

    scene.userpan = False

    scene.center = vp.vector(30, 3, 0)

    scene.range = 22

    scene.fov = 0.01

    # Estacas do trilho

    for x in range(-3, 64, 2):

        vp.cylinder(canvas=scene, pos=vp.vector(x, -0.6, -4.5),

                    axis=vp.vector(0, 0, 9), radius=0.3,

                    color=vp.vector(0.65, 0.45, 0.25))

    for z in [-3, 3]:

        vp.box(canvas=scene, pos=vp.vector(30, 0, z),

               size=vp.vector(68, 0.4, 0.35), color=vp.color.gray(0.8))

    # Criação dos trens e do pássaro. Usa o centro dos objetos.

    trem_a = vp.box(canvas=scene, pos=vp.vector(0, 2.7, 0),

                    size=vp.vector(2, 3, 4), color=vp.color.yellow)

    trem_b = vp.box(canvas=scene, pos=vp.vector(60, 2.7, 0),

                    size=vp.vector(2, 3, 4), color=vp.color.green)

    passaro = vp.sphere(canvas=scene, pos=vp.vector(0, 8, 0),

                        radius=1.6, color=vp.color.blue)

    # O gráfico é removido e recriado quando necessário. As curvas não
    # selecionadas não são criadas, evitando que reapareçam durante a simulação.
    grafico = None
    curva_a = curva_b = curva_p = None
    curvas = []
    dados_curvas = [
        [[0, 0]],
        [[0, DISTANCIA_INICIAL]],
        [[0, 0]],
    ]
    curvas_visiveis = [True, True, True]

    def atualizar_curvas():
        nonlocal curva_a, curva_b, curva_p, curvas

        for curva in (curva_a, curva_b, curva_p):
            if curva is not None:
                curva.delete()

        curva_a = vp.gcurve(graph=grafico, color=vp.color.yellow,
                            label='Trem A', width=2, data=dados_curvas[0]) \
            if curvas_visiveis[0] else None
        curva_b = vp.gcurve(graph=grafico, color=vp.color.green,
                            label='Trem B', width=2, data=dados_curvas[1]) \
            if curvas_visiveis[1] else None
        curva_p = vp.gcurve(graph=grafico, color=vp.color.blue,
                            label='Pássaro', width=2, data=dados_curvas[2]) \
            if curvas_visiveis[2] else None

        curvas = [curva for curva in (curva_a, curva_b, curva_p)
                  if curva is not None]

    def criar_grafico():
        nonlocal grafico
        if grafico is not None:
            return

        grafico = vp.graph(title='', xtitle='Tempo (minutos)', ytitle='Posição (km)',
                           width=640, height=350, align='right', xmin=0,
                           xmax=modelo.tempo_final, ymin=0, ymax=60,
                           background=vp.color.white, foreground=vp.color.black)
        atualizar_curvas()

    def esconder_grafico():
        nonlocal grafico, curva_a, curva_b, curva_p, curvas
        if grafico is not None:
            grafico.delete()
            grafico = None
            curva_a = curva_b = curva_p = None
            curvas = []

    criar_grafico()

    # Os controles ficam em uma tela independente para nunca sumirem.
    ancora = ui_canvas.title_anchor

    # Escreve um texto na parte de cima da página.

    def texto(conteudo):

        return vp.wtext(pos=ancora, text=conteudo)

    # Atualiza o relógio, as velocidades e as distâncias na tela.

    def atualizar_painel():

        estado = ('Finalizada' if modelo.finalizada else

                  'Em execução' if modelo.rodando else 'Pausada')

        direcao = '→' if modelo.sentido > 0 else '←'

        valores = [

            ('Tempo simulado', formatar_relogio(modelo.tempo), '#172033'),

            ('Trem A', formatar_numero(modelo.velocidade_a, 1) + ' km/h →', '#b91c1c'),

            ('Trem B', formatar_numero(modelo.velocidade_b, 1) + ' km/h ←', '#15803d'),

            ('Pássaro', formatar_numero(modelo.velocidade_passaro, 1) + ' km/h ' + direcao, '#1d4ed8'),

            ('Entre os trens', formatar_numero(max(0, modelo.x_b - modelo.x_a)) + ' km', '#172033'),

            ('Pássaro ↔ trem A', formatar_numero(abs(modelo.x_passaro - modelo.x_a)) + ' km', '#172033'),

            ('Pássaro ↔ trem B', formatar_numero(abs(modelo.x_b - modelo.x_passaro)) + ' km', '#172033'),

        ]

        # Organiza os valores em pequenas caixas no painel.

        html = '<div style="white-space:normal;font-family:Arial,sans-serif;margin:10px 0;">'

        html += '<div style="margin-bottom:8px;"><b>' + estado + '</b>'

        html += ' · Velocidades do modelo · Relógio em horas:minutos:segundos</div>'

        html += '<div style="display:flex;flex-wrap:wrap;gap:8px;">'

        for rotulo, valor, cor in valores:

            html += ('<div style="background:#f1f5f9;border:1px solid #dbe3ee;'

                     'border-radius:8px;padding:9px 12px;min-width:115px;">'

                     '<span style="font-size:12px;color:#526078;">' + rotulo + '</span><br>'

                     '<b style="font-size:17px;color:' + cor + ';">' + valor + '</b></div>')

        painel.text = html + '</div></div>'

        # Muda o texto do botão e desativa quando os trens se encontram.

        botao_start.text = 'Finalizada' if modelo.finalizada else ('Parar' if modelo.rodando else 'Iniciar')

        botao_start.disabled = modelo.finalizada

    # Coloca os objetos nas posições calculadas pela simulação.

    def atualizar_objetos():

        trem_a.pos.x = modelo.x_a

        trem_b.pos.x = modelo.x_b

        passaro.pos.x = modelo.x_passaro

    # Apaga as curvas antigas e ajusta o eixo do tempo às velocidades escolhidas.

    def zerar_grafico():
        dados_curvas[0] = [[0, 0]]
        dados_curvas[1] = [[0, DISTANCIA_INICIAL]]
        dados_curvas[2] = [[0, 0]]

        if grafico is not None:
            grafico.xmax = modelo.tempo_final
            atualizar_curvas()

        atualizar_objetos()
        atualizar_painel()

    # Botão para começar ou pausar, atualizando o painel junto.

    def iniciar_parar(evento):

        modelo.iniciar_parar()

        atualizar_painel()

    # Botão para voltar ao começo e limpar o gráfico.

    def reiniciar(evento):

        modelo.reiniciar()

        zerar_grafico()

    # Troca a posição da câmera entre a visão de cima e a de lado.

    def mudar_visao(evento):

        if evento.selected == 'Visão de cima':

            scene.center = vp.vector(30, 0, 0)

            scene.up = vp.vector(0, 0, -1)

            scene.forward = vp.vector(0, -1, 0)

        else:

            scene.center = vp.vector(30, 3, 0)

            scene.up = vp.vector(0, 1, 0)

            scene.forward = vp.vector(0, 0, -1)

    # Cada combinação diz quais curvas ficam visíveis no gráfico.

    def selecionar_curvas(evento):
        combinacoes = [
            (True, True, True), (True, False, False), (False, True, False),
            (True, True, False), (True, False, True), (False, True, True),
            (False, False, True),
        ]
        curvas_visiveis[:] = combinacoes[evento.index]
        if grafico is not None:
            atualizar_curvas()

    # Mostra os avisos abaixo dos campos; erros aparecem em vermelho.

    def avisar(mensagem, erro=False):

        cor = '#b91c1c' if erro else '#526078'

        aviso.text = '<span style="color:' + cor + ';">' + mensagem + '</span>'

    # Lembra de aplicar as velocidades depois de editar os campos.

    def editar_velocidade(evento):

        avisar('Valores editados. Clique em Aplicar velocidades para reiniciar com eles.')

    # Lê as três velocidades e começa outra simulação com os novos valores.

    def aplicar_velocidades(evento):

        try:

            # Aceita tanto ponto quanto vírgula nos números digitados.

            velocidades = [float(campo.text.strip().replace(',', '.')) for campo in campos]

            modelo.configurar(*velocidades)

        # Se algum valor estiver errado, mostra o aviso e não aplica a mudança.

        except (ValueError, OverflowError) as erro:

            mensagem = str(erro)

            if 'could not convert' in mensagem:

                mensagem = 'Digite um número em cada campo. Exemplo: 30 ou 30,5.'

            avisar(mensagem, erro=True)

            return

        zerar_grafico()

        avisar('Velocidades aplicadas. Clique em Iniciar para executar a nova simulação.')

    # Volta para 30 km/h em cada trem e 60 km/h no pássaro.

    def usar_originais(evento):

        for campo, valor in zip(campos, [30, 30, 60]):

            campo.text = str(valor)

        aplicar_velocidades(evento)

    # Fecha as etapas para o usuário tentar resolver o problema de novo.

    def recomecar_flashcard(evento):
        flashcard.text = html_flashcard()

    # Alterna apenas a exibição. Nenhuma dimensão ou posição é alterada.
    def mostrar_so_visual(evento):
        scene.visible = True
        esconder_grafico()

    def mostrar_visual_e_grafico(evento):
        scene.visible = True
        criar_grafico()

    # Painel ao vivo e botões de iniciar e reiniciar.

    painel = texto('')

    botao_start = vp.button(pos=ancora, text='Iniciar', bind=iniciar_parar)
    texto('     ')
    vp.button(pos=ancora, text='Reiniciar', bind=reiniciar)

    texto('     Exibição: ')
    vp.button(pos=ancora, text='Só visual', bind=mostrar_so_visual)
    texto(' ')
    vp.button(pos=ancora, text='Visual + gráfico', bind=mostrar_visual_e_grafico)
    texto('<br>')

    # Menus para escolher a câmera e as curvas do gráfico.

    texto('  Câmera: ')

    visao = vp.menu(pos=ancora, choices=['Visão de lado', 'Visão de cima'], bind=mudar_visao)

    texto('  Curvas: ')

    vp.menu(pos=ancora, choices=['Trens e pássaro', 'Só trem A', 'Só trem B',

                                'Trem A e B', 'Trem A e pássaro',

                                'Trem B e pássaro', 'Só pássaro'], bind=selecionar_curvas)

    # Campos para digitar a velocidade de cada trem e do pássaro.

    texto('<br><br><b>Escolha as velocidades (km/h):</b>  Trem A: ')

    campo_a = vp.winput(pos=ancora, text='30', type='string', width=65, bind=editar_velocidade)

    texto('  Trem B: ')

    campo_b = vp.winput(pos=ancora, text='30', type='string', width=65, bind=editar_velocidade)

    texto('  Pássaro: ')

    campo_p = vp.winput(pos=ancora, text='60', type='string', width=65, bind=editar_velocidade)

    campos = [campo_a, campo_b, campo_p]

    texto('  ')

    # Botões para aplicar as velocidades ou voltar aos valores do enunciado.

    vp.button(pos=ancora, text='Aplicar velocidades', bind=aplicar_velocidades)

    texto('  ')

    vp.button(pos=ancora, text='Valores originais', bind=usar_originais)

    texto('<br>')

    # Avisos sobre as velocidades e o tempo acelerado da animação.

    aviso = texto('Escolha as velocidades e clique em Aplicar. A aplicação reinicia a simulação pausada.')

    texto('<br><span style="color:#64748b;font-size:12px;">'

          'O pássaro deve ser mais rápido que os dois trens. '

          'Animação acelerada: cerca de 20 s por execução; relógio e gráfico usam o tempo simulado.'

          '</span>')

    # Flashcard com o enunciado, a resolução e o botão para recomeçar.

    flashcard = texto(html_flashcard())

    vp.button(pos=ancora, text='Recomeçar flashcard', bind=recomecar_flashcard)

    texto('<br><br>')

    # Deixa a câmera de lado e os objetos nas posições iniciais.

    mudar_visao(visao)

    zerar_grafico()

    # Loop da animação. Os botões continuam funcionando durante a pausa.

    while True:

        vp.rate(FPS)

        if not modelo.rodando:

            continue

        # Calcula o próximo passo e move os objetos na tela.

        pontos = modelo.avancar()

        atualizar_objetos()

        # Guarda todo o histórico mesmo quando o gráfico está oculto.
        dados_curvas[0].append([modelo.tempo, modelo.x_a])
        dados_curvas[1].append([modelo.tempo, modelo.x_b])
        if grafico is not None:
            if curva_a is not None:
                curva_a.plot(modelo.tempo, modelo.x_a)
            if curva_b is not None:
                curva_b.plot(modelo.tempo, modelo.x_b)

        for instante, posicao in pontos:
            dados_curvas[2].append([instante, posicao])
            if grafico is not None and curva_p is not None:
                curva_p.plot(instante, posicao)
        # Mostra os novos valores no painel a cada quadro.

        atualizar_painel()

# Inicia o programa quando este arquivo é executado.

if __name__ == '__main__':

    main()
