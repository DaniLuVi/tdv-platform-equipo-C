import arcade
import arcade.gui
import math

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

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
                if siguiente in ESTADOS_NIVELES:
                    if ESTADOS_NIVELES[siguiente] == "bloqueado":
                        ESTADOS_NIVELES[siguiente] = "no_conseguido"
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
        ESTADOS_NIVELES[nivel] = "conseguido"


class Nivel(arcade.View):
    """
    Vista del nivel.
    """
    def __init__(self, numero_nivel):
        super().__init__()
        self.numero_nivel = numero_nivel

    def on_show_view(self): 
        arcade.set_background_color(arcade.color.GRAY)

class Nivel1(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=1)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Pulsa 'V' para Ganar o 'D' para Perder", 640, 360, arcade.color.WHITE, 20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.V:
            self.window.show_view(NivelConseguido(self.numero_nivel))
        elif key == arcade.key.D:
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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Mapa de niveles")
    mapa = Mapa()
    window.show_view(mapa)
    arcade.run()