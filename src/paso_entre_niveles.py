import arcade

class VistaNivelEnMapa(arcade.View):
    """
    Vista del logo de cada nivel en el mapa, en el que cada nivel puede ser no conseguido, conseguido o bloqueado"""

    def __init__(self, nivel, x, y, estado_nivel, conexiones):
        super().__init__()
        self.nivel = nivel  # Número o identificador del nivel
        self.x = x  # Coordenada x del logo del nivel
        self.y = y  # Coordenada y del logo del nivel
        self.estado_nivel = estado_nivel  # Estado del nivel: "no_conseguido", "conseguido" o "bloqueado"
        self.conexiones = conexiones  # Conexiones con otros niveles (lista con los niveles)
        self.radio_logo = 20  # Radio para hacer click en el nivel

    def on_draw(self):
        self.clear()
        # Se dibuja el logo del nivel dependiendo del estado del nivel´

        if self.estado_nivel == "no_conseguido":
            color = arcade.color.GRAY
            color_borde = arcade.color.YELLOW
        elif self.estado_nivel == "conseguido":
            color = arcade.color.GREEN
            color_borde = arcade.color.YELLOW
        elif self.estado_nivel == "bloqueado":
            color = arcade.color.RED
            color_borde = arcade.color.LIGHT_BROWN

        arcade.draw_circle_filled(self.x, self.y, self.radio_logo, color)
        arcade.draw_circle_outline(self.x, self.y, self.radio_logo, color_borde, 3)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            distancia = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
            if distancia <= self.radio_logo:
                if self.estado_nivel != "bloqueado":
                    # Lógica para abrir el nivel correspondiente
                    nivel_pulsado = Nivel(self.nivel)  # Aquí se debería crear la instancia del nivel correspondiente
                    self.window.show_view(nivel_pulsado)

class Mapa(arcade.View):
    """
    Vista en la que se muestran los distintos niveles del juego.
    """
    def __init__(self):
        super().__init__()
        self.window.background_color = arcade.color.WHITE

        self.niveles = {
           
        }

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Mapa de niveles - Click para ir al nivel",
            640,
            360,
            arcade.color.GREEN,
            font_size=30,
            anchor_x="center"
        )

class NivelPerdido(arcade.View):
    """
    Vista que se muestra al perder un nivel, con un mensaje de derrota y posibilidad de reiniciar el nivel o ir al mapa.
    """
    def __init__(self,):
        super().__init__()
        self.background_color = arcade.color.BLACK
        
        self.presionado = None  # Variable para almacenar el botón presionado
    
    def on_draw(self):
        self.clear()


    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.presionado == "reiniciar":
                # Lógica para reiniciar el nivel
                pass
            elif self.presionado == "mapa":
                mapa = Mapa()
                self.window.show_view(mapa)

class NivelConseguido(arcade.View):
    """
    Vista que se muestra al conseguir un nivel, con un mensaje de victoria y posibilidad de pasar al siguiente nivel o ir al mapa.
    """
    def __init__(self,):
        super().__init__()
        self.background_color = arcade.color.BLACK

        self.presionado = None  # Variable para almacenar el botón presionado
    
    def on_draw(self):
        self.clear()


    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.presionado == "siguiente":
                # Lógica para pasar al siguiente nivel
                pass
            elif self.presionado == "mapa":
                mapa = Mapa()
                self.window.show_view(mapa)

class Nivel(arcade.View):
    """
    Vista del nivel.
    """
    def __init__(self, numero_nivel):
        super().__init__()
        self.numero_nivel = numero_nivel
        self.background_color = arcade.color.GRAY

class Nivel1(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=1)

class Nivel2(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=2)

if __name__ == "__main__":
    window = arcade.Window(1280, 720, "Mapa de niveles")
    mapa = Mapa()
    window.show_view(mapa)
    arcade.run()