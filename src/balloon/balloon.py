from vpython import *
import numpy as np

trail_config = {
    "make_trail": True,
    "trail_type": "points",
    "trail_color": color.red,
    "trail_radius": .1
}

scene = canvas(
    align="left",
    width=600,
    height=600,
    background=vector(0.53, 0.81, 0.98),
    title="Gas Balloon"
)

scene.center = vec(0, 4, 0)
scene.range = 10

ground = box(
    pos=vec(0, -30.5, 0), 
    size=vec(30, 0.2, 30), 
    texture=textures.granite
    )

balloon = sphere(
    pos=vec(3, 0, 3), 
    size=vec(2, 2, 2),
    color=color.green
)

celular = box(
    pos=vec(0, 0, 3), 
    size=vec(2, 2, 2),
    color=color.red
)

t = 0
dt = 0.01

g_pos = graph(
    align="right",
    title="Ball Movement",
    xtitle="Time (s)",
    ytitle="Position",
    width=600,
    height=250,
    xmin=0,
    xmax=15,
    ymin=-10,
    ymax=20
)

g_pos_rel = graph(
    align="right",
    title="Relative Movement",
    xtitle="Time (s)",
    ytitle="Position",
    width=600,
    height=250,
    xmin=0,
    xmax=10,
    ymin=0,
    ymax=20
)

# g_vel = graph(
#     align="right",
#     title="Ball Movement",
#     xtitle="Time (s)",
#     ytitle="Position",
#     width=600,
#     height=250,
#     xmin=0,
#     xmax=10,
#     ymin=0,
#     ymax=20
# )

balloon_graph = gcurve(graph=g_pos, color=color.green)
celular_graph = gcurve(graph=g_pos, color=color.red)
cell_balloon = gcurve(graph=g_pos_rel, color= color.orange)

v0 = 4
v = v0
g = np.float64(-1)

while True:
    rate(60)

    if celular.pos.y <= -10:
        continue
    celular.pos.y = v0 * t + 0.5*g*t**2
    v = v + g * dt

    balloon.pos.y = v0*t



    celular_graph.plot(t, v)
    balloon_graph.plot(t, v0)
    cell_balloon.plot(t, v0-v)



    # if t > 10:
    #     g_pos.xmin = t - 10
    #     g_pos_rel.xmin = t - 10
    #     g_pos.xmax = t
    #     g_pos_rel.xmax = t

    t += dt