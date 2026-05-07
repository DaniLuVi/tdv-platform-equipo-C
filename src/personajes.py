import arcade
from abc import ABC, abstractmethod

# ------------------ CONSTANTES ------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Fireboy & Watergirl (Base)"

PLAYER_SPEED = 5
GRAVITY = 1
JUMP_SPEED = 20

RIGHT_FACING = 0
LEFT_FACING = 1

# Tipos de zonas
LAVA = 0
AGUA = 1
VERDE = 2

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

# ------------------ JUEGO ------------------
class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.fireboy = None
        self.watergirl = None

        self.lista_peligros = []
        self.walls = None

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

# ------------------ MAIN ------------------
def main():
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()