import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
ESCALA_MAPA = 0.35

class Galeria(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Historia")

        carpeta = os.path.dirname(__file__)

        self.mapas = [
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if f.endswith(".tmx")
        ]

        self.mapas.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        self.mapas = self.mapas[6:9]

        self.indice = 0

        self.camara = arcade.Camera2D()

        self.cargar_mapa()

    def cargar_mapa(self):
        tile_map = arcade.load_tilemap(self.mapas[self.indice])
        self.scene = arcade.Scene.from_tilemap(tile_map)

        ancho = tile_map.width * tile_map.tile_width
        alto = tile_map.height * tile_map.tile_height

        self.camara.position = (ancho / 2, alto / 2)


        self.camara.zoom = ESCALA_MAPA

    def on_draw(self):
        self.clear()
        self.camara.use()
        self.scene.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.indice = (self.indice + 1)
        self.cargar_mapa()

if __name__ == "__main__":
    Galeria()
    arcade.run()