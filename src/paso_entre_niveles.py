import arcade
import arcade.gui
import math
from abc import ABC, abstractmethod

# --- CONFIGURACIÓN DINÁMICA ---
# Obtenemos el tamaño del monitor para que casi lo ocupe todo
# (Le restamos un poco de margen para que se vea la barra de tareas)
monitor = arcade.get_display_size()
SCREEN_WIDTH = int(monitor[0] * 0.9)
SCREEN_HEIGHT = int(monitor[1] * 0.8)

# Diccionario para almacenar el estado de cada nivel: no conseguido, conseguido o bloqueado
ESTADOS_NIVELES = {
    1: "no_conseguido",
    2: "bloqueado",
    3: "bloqueado",
    4: "bloqueado",
    5: "bloqueado",
    6: "bloqueado",
    7: "bloqueado",
    8: "bloqueado",
    9: "bloqueado",
    10: "bloqueado"
}

# ------------------ CONSTANTES ------------------

# Velocidad de movimiento, gravedad y salto en píxeles por frame
PLAYER_SPEED = 5
GRAVITY = 1
JUMP_SPEED = 20

# Se usan para determinar la dirección del personaje
RIGHT_FACING = 0
LEFT_FACING = 1

# Tipos de zonas
LAVA = 0
AGUA = 1
VERDE = 2

# --- VISTA: MENÚ PRINCIPAL ---
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        # Variables para controlar el mensaje de error de "Continuar Partida"
        self.mostrar_error = False
        self.tiempo_error = 0.0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_update(self, delta_time):
        # Si el error está activo, sumamos el tiempo para que desaparezca tras 3 segundos
        if self.mostrar_error:
            self.tiempo_error += delta_time
            if self.tiempo_error > 3.0:
                self.mostrar_error = False
                self.tiempo_error = 0.0

    def on_draw(self):
        self.clear()
        
        # Título centrado dinámicamente
        arcade.draw_text("MI VIDEOJUEGO", self.window.width / 2, self.window.height * 0.75,
                         arcade.color.WHITE, font_size=60, anchor_x="center")

        # --- BOTÓN 1: INICIAR PARTIDA ---
        # Calculamos la posición central
        cx, cy = self.window.width / 2, self.window.height / 2
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy - 25, cy + 25, arcade.color.ARMY_GREEN)
        arcade.draw_text("INICIAR PARTIDA", cx, cy,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- BOTÓN 2: CONTINUAR PARTIDA ---
        # Lo ponemos un poco más abajo del centro
        cy_continuar = cy - 80
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy_continuar - 25, cy_continuar + 25, arcade.color.YELLOW_GREEN)
        arcade.draw_text("CONTINUAR PARTIDA", cx, cy_continuar,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- BOTÓN 3: AJUSTES ---
        # Lo ponemos un poco más abajo del centro
        cy_ajustes = cy_continuar - 80
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy_ajustes - 25, cy_ajustes + 25, arcade.color.SLATE_GRAY)
        arcade.draw_text("AJUSTES", cx, cy_ajustes,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- MENSAJE DE ERROR DINAMICO ---
        if self.mostrar_error:
            arcade.draw_text("No hay ninguna partida empezada todavía.", cx, cy_ajustes - 80,
                             arcade.color.LIGHT_RED_OCHRE, font_size=16, anchor_x="center", bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2
        
        # Clic en Iniciar
        if cx - 150 < x < cx + 150 and cy - 25 < y < cy + 25:
            # Reseteamos el progreso usando la variable global
            global ESTADOS_NIVELES
            ESTADOS_NIVELES[1] = "no_conseguido"
            for i in range(2, 11):
                ESTADOS_NIVELES[i] = "bloqueado"
            
            # Limpiamos cualquier error previo y entramos al mapa
            self.mostrar_error = False
            mapa = Mapa()
            self.window.show_view(mapa)

        # Clic en Continuar
        cy_continuar = cy - 80
        if cx - 150 < x < cx + 150 and cy_continuar - 25 < y < cy_continuar + 25:
            hay_progreso = ESTADOS_NIVELES[1] == "conseguido"
            
            if hay_progreso:
                self.mostrar_error = False
                mapa = Mapa()
                self.window.show_view(mapa)
            else:
                # Si no hay progreso, activamos el mensaje
                self.mostrar_error = True
                self.tiempo_error = 0.0

        # Clic en Ajustes
        cy_ajustes = cy_continuar - 80
        if cx - 150 < x < cx + 150 and cy_ajustes - 25 < y < cy_ajustes + 25:
            settings_view = SettingsView()
            self.window.show_view(settings_view)

# --- VISTA: AJUSTES ---
class SettingsView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

    def on_draw(self):
        self.clear()
        cx, cy = self.window.width / 2, self.window.height / 2
        
        arcade.draw_text("AJUSTES DE SONIDO", cx, self.window.height * 0.7,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        
        # Muestra el volumen actual
        vol_porcentaje = int(self.window.volumen * 100)
        arcade.draw_text(f"VOLUMEN: {vol_porcentaje}%", cx, cy + 50,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

        # Botón Menos (-)
        arcade.draw_lrbt_rectangle_filled(cx - 120, cx - 40, cy - 20, cy + 20, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("-", cx - 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Más (+)
        arcade.draw_lrbt_rectangle_filled(cx + 40, cx + 120, cy - 20, cy + 20, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("+", cx + 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Volver
        arcade.draw_lrbt_rectangle_outline(cx - 60, cx + 60, 90, 130, arcade.color.WHITE, border_width=2)
        arcade.draw_text("VOLVER", cx, 110, arcade.color.WHITE, font_size=15, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2

        # Clic en MENOS (-)
        if cx - 120 < x < cx - 40 and cy - 20 < y < cy + 20:
            self.window.volumen = max(0.0, self.window.volumen - 0.1)

        # Clic en MÁS (+)
        elif cx + 40 < x < cx + 120 and cy - 20 < y < cy + 20:
            self.window.volumen = min(1.0, self.window.volumen + 0.1)

        # Clic en VOLVER
        elif cx - 60 < x < cx + 60 and 90 < y < 130:
            self.window.show_view(MenuView())

class VistaNivelEnMapa:
    """
    Vista del logo de cada nivel en el mapa, en el que cada nivel puede ser no conseguido, conseguido o bloqueado"""

    def __init__(self, nivel, x, y, conexiones):
        self.nivel = nivel  # Número o identificador del nivel
        self.x = x  # Coordenada x del logo del nivel
        self.y = y  # Coordenada y del logo del nivel
        self.conexiones = conexiones  # Conexiones con otros niveles (lista con los niveles)
        self.radio_logo = 20  # Radio para hacer click en el nivel

    def draw(self):
        # Se dibuja el logo del nivel dependiendo del estado del nivel´

        if ESTADOS_NIVELES[self.nivel] == "no_conseguido":
            color = arcade.color.GRAY
            color_borde = arcade.color.YELLOW
        elif ESTADOS_NIVELES[self.nivel] == "conseguido":
            color = arcade.color.GREEN
            color_borde = arcade.color.YELLOW
        elif ESTADOS_NIVELES[self.nivel] == "bloqueado":
            color = arcade.color.RED
            color_borde = arcade.color.LIGHT_BROWN

        arcade.draw_circle_filled(self.x, self.y, self.radio_logo, color)
        arcade.draw_circle_outline(self.x, self.y, self.radio_logo, color_borde, 3)
        arcade.draw_text(str(self.nivel), self.x, self.y, arcade.color.BLACK, 12, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            distancia = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
            if distancia <= self.radio_logo:
                if ESTADOS_NIVELES[self.nivel] != "bloqueado":
                    # Lógica para abrir el nivel correspondiente
                    nivel_pulsado = Nivel(self.nivel)  # Aquí se debería crear la instancia del nivel correspondiente
                    self.window.show_view(nivel_pulsado)

class Mapa(arcade.View):
    """
    Vista en la que se muestran los distintos niveles del juego.
    """
    def __init__(self):
        super().__init__()

        self.niveles = {
           1: VistaNivelEnMapa(nivel=1, x=200, y=500, conexiones=[2]),
           2: VistaNivelEnMapa(nivel=2, x=400, y=500, conexiones=[1, 3]),
           3: VistaNivelEnMapa(nivel=3, x=600, y=500, conexiones=[2, 4]),
           4: VistaNivelEnMapa(nivel=4, x=800, y=500, conexiones=[3]),
           5: VistaNivelEnMapa(nivel=5, x=200, y=300, conexiones=[6, 7]),
           6: VistaNivelEnMapa(nivel=6, x=400, y=300, conexiones=[5]),
           7: VistaNivelEnMapa(nivel=7, x=600, y=300, conexiones=[5]),
           8: VistaNivelEnMapa(nivel=8, x=800, y=300, conexiones=[9]),
           9: VistaNivelEnMapa(nivel=9, x=1000, y=300, conexiones=[10]),
           10: VistaNivelEnMapa(nivel=10, x=1200, y=300, conexiones=[]),
        }

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BROWN_NOSE)

    def on_draw(self):
        self.clear()
        
        # Dibujar las conexiones entre los niveles
        for nivel in self.niveles.values():
            for conexion in nivel.conexiones:
                if conexion in self.niveles:
                    destino = self.niveles[conexion]

                    if ESTADOS_NIVELES[nivel.nivel] != "bloqueado" and ESTADOS_NIVELES[destino.nivel] != "bloqueado":
                        color_conexion = arcade.color.GOLD
                    else:
                        color_conexion = arcade.color.DARK_BROWN

                    arcade.draw_line(nivel.x, nivel.y, destino.x, destino.y, color_conexion, 3)

        # Dibujar los niveles
        for nivel in self.niveles.values():
            nivel.draw()

        arcade.draw_text("Presiona ESC para volver al menú", self.window.width / 2, 100,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for nivel in self.niveles.values():
                distancia = math.dist((x, y), (nivel.x, nivel.y))

                if distancia <= nivel.radio_logo:
                    if ESTADOS_NIVELES[nivel.nivel] != "bloqueado":
                        print(f"¡Cargando el nivel {nivel.nivel}!")
                        if nivel.nivel in CLASES_NIVELES: 
                            self.window.show_view(CLASES_NIVELES[nivel.nivel]())
                
                    else:
                        print(f"El nivel {nivel.nivel} aún está bloqueado.")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

class VistaFinNivel(arcade.View):
    def __init__(self, nivel, mensaje, color):
        super().__init__()
        self.nivel = nivel
        self.mensaje = mensaje
        self.color = color

        self.manager = arcade.gui.UIManager()

    def on_show_view(self): 
        self.manager.enable()
        arcade.set_background_color(arcade.color.BLACK)

        # Creamos una caja vertical para organizar los botones
        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        # --- BOTÓN PRINCIPAL (Siguiente o Reiniciar) ---
        texto_boton_1 = "Siguiente nivel" if self.color == arcade.color.GREEN else "Reiniciar nivel"
        boton_accion = arcade.gui.UIFlatButton(text=texto_boton_1, width=250)
        self.h_box.add(boton_accion)

        # --- BOTÓN VOLVER AL MAPA ---
        boton_mapa = arcade.gui.UIFlatButton(text="Volver al mapa", width=250)
        self.h_box.add(boton_mapa)

        # Asignar funciones a los clics
        @boton_accion.event("on_click")
        def on_click_accion(event):
            if self.color == arcade.color.GREEN:
                # Lógica: Desbloquear siguiente y abrirlo
                siguiente = self.nivel + 1
                if siguiente in CLASES_NIVELES:
                    self.window.show_view(CLASES_NIVELES[siguiente]())
                else:
                    # Si no hay más niveles, volvemos al mapa
                    self.window.show_view(Mapa())
            else:
                # Reiniciar el mismo nivel
                self.window.show_view(CLASES_NIVELES[self.nivel]())

        @boton_mapa.event("on_click")
        def on_click_mapa(event):
            self.window.show_view(Mapa())

        # Centrar la caja en la pantalla
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(
            child=self.h_box,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-100  # Ajuste vertical para que quede un poco más abajo del centro
        )
        self.manager.add(anchor)
    
    def on_hide_view(self):
        # Es vital deshabilitar el manager al cambiar de vista
        self.manager.disable()

    def on_draw(self):
        self.clear()

        # Mensaje de victoria
        arcade.draw_text(
            self.mensaje, self.window.width / 2, self.window.height / 2 + 50, self.color, font_size=40, anchor_x="center")
        
        self.manager.draw()

class NivelPerdido(VistaFinNivel):
    """
    Vista que se muestra al perder un nivel, con un mensaje de derrota y posibilidad de reiniciar el nivel o ir al mapa.
    """
    def __init__(self, nivel):
        super().__init__(nivel, "No ha conseguido superar el nivel", arcade.color.RED)

class NivelConseguido(VistaFinNivel):
    """
    Vista que se muestra al conseguir un nivel, con un mensaje de victoria y posibilidad de pasar al siguiente nivel o ir al mapa.
    """
    def __init__(self, nivel):
        super().__init__(nivel, "¡Nivel conseguido!", arcade.color.GREEN)
        # Al conseguir el nivel, actualizamos su estado a conseguido
        ESTADOS_NIVELES[nivel] = "conseguido"
        # Si el siguiente nivel está bloqueado,  lo desbloqueamos
        siguiente = nivel + 1
        if siguiente in ESTADOS_NIVELES and ESTADOS_NIVELES[siguiente] == "bloqueado":
            ESTADOS_NIVELES[siguiente] = "no_conseguido"

# ------------------ CLASE ABSTRACTA ------------------
class Personaje(arcade.Sprite, ABC):

    def __init__(self, color, scale=1):
        super().__init__()

        self.color = color
        self.scale = scale
        self.width = 40
        self.height = 60

        self.center_x = 0
        self.center_y = 0

        self.change_x = 0
        self.change_y = 0

        self.physics_engine = None

    def update(self):
        self.center_x += self.change_x

    def saltar(self):
        if self.physics_engine and self.physics_engine.can_jump():
            self.change_y = JUMP_SPEED

    @abstractmethod
    def es_seguro(self, tipo):
        pass

    def comprobar_colision(self, objeto):
        if not self.es_seguro(objeto.tipo):
            self.morir()

    def morir(self):
        print(f"{self.__class__.__name__} ha muerto")
        self.center_x = 100
        self.center_y = 200

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            self.center_x,
            self.center_y,
            self.width,
            self.height,
            self.color
        )

# ------------------ PERSONAJES ------------------
class Fireboy(Personaje):
    def es_seguro(self, tipo):
        return tipo == LAVA


class Watergirl(Personaje):
    def es_seguro(self, tipo):
        return tipo == AGUA
    
# ------------------ ZONAS ------------------
class ZonaPeligrosa(arcade.Sprite):
    def __init__(self, tipo, x, y, width, height):
        super().__init__()
        self.tipo = tipo
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height

    def draw(self):
        if self.tipo == LAVA:
            color = arcade.color.RED
        elif self.tipo == AGUA:
            color = arcade.color.BLUE
        else:
            color = arcade.color.GREEN

        arcade.draw_lbwh_rectangle_filled(
            self.center_x, self.center_y, self.width, self.height, color
        )



class Nivel(arcade.View):
    """
    Vista del nivel.
    """
    def __init__(self, numero_nivel):
        super().__init__()
        self.numero_nivel = numero_nivel

        self.fireboy = None
        self.watergirl = None

        self.lista_peligros = []
        self.walls = None

    def on_show_view(self): 
        arcade.set_background_color(arcade.color.GRAY)
        self.setup()

    # ---------------- CONTROLES ----------------
    def on_key_press(self, key, modifiers):
        # Fireboy (flechas)
        if key == arcade.key.LEFT:
            self.fireboy.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.fireboy.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.fireboy.saltar()

        # Watergirl (WASD)
        if key == arcade.key.A:
            self.watergirl.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.watergirl.change_x = PLAYER_SPEED
        elif key == arcade.key.W:
            self.watergirl.saltar()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.fireboy.change_x = 0

        if key in [arcade.key.A, arcade.key.D]:
            self.watergirl.change_x = 0

class Nivel1(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=1)

    def setup(self):
        # Suelo
        self.walls = arcade.SpriteList()
        suelo = arcade.SpriteSolidColor(800, 40, arcade.color.GRAY)
        suelo.center_x = 400
        suelo.center_y = 20
        self.walls.append(suelo)

        # Personajes
        self.fireboy = Fireboy(arcade.color.ORANGE)
        self.fireboy.center_x = 100
        self.fireboy.center_y = 200

        self.watergirl = Watergirl(arcade.color.CYAN)
        self.watergirl.center_x = 200
        self.watergirl.center_y = 200

        # Física
        self.fireboy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.fireboy, self.walls, GRAVITY
        )

        self.watergirl.physics_engine = arcade.PhysicsEnginePlatformer(
            self.watergirl, self.walls, GRAVITY
        )

        # Zonas peligrosas
        self.lista_peligros = [
            ZonaPeligrosa(LAVA, 300, 60, 100, 40),
            ZonaPeligrosa(AGUA, 500, 60, 100, 40),
            ZonaPeligrosa(VERDE, 650, 60, 100, 40),
        ]

    def on_draw(self):
        self.clear()

        self.walls.draw()

        for zona in self.lista_peligros:
            zona.draw()

        self.fireboy.draw()
        self.watergirl.draw()

        arcade.draw_text("Pulsa 'V' para Ganar o 'L' para Perder", 640, 360, arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        # Física
        self.fireboy.physics_engine.update()
        self.watergirl.physics_engine.update()

        # Colisiones
        for zona in self.lista_peligros:
            if arcade.check_for_collision(self.fireboy, zona):
                self.fireboy.comprobar_colision(zona)

            if arcade.check_for_collision(self.watergirl, zona):
                self.watergirl.comprobar_colision(zona)
    
    def on_key_press(self, key, modifiers):
        super().on_key_press(key, modifiers)
        if key == arcade.key.V:
            self.window.show_view(NivelConseguido(self.numero_nivel))
        elif key == arcade.key.L:
            self.window.show_view(NivelPerdido(self.numero_nivel))

class Nivel2(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=2)

class Nivel3(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=3)

class Nivel4(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=4)

class Nivel5(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=5)

class Nivel6(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=6)

class Nivel7(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=7)

class Nivel8(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=8)

class Nivel9(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=9)

class Nivel10(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=10)

CLASES_NIVELES = {
    1: Nivel1,
    2: Nivel2,
    3: Nivel3,
    4: Nivel4,
    5: Nivel5,
    6: Nivel6,
    7: Nivel7,
    8: Nivel8,
    9: Nivel9,
    10: Nivel10,
}

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Juego", resizable=True)
    window.volumen = 0.5
    menu = MenuView()
    window.show_view(menu)
    arcade.run()