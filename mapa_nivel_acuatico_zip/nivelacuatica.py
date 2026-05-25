import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Nivel Acuático – Arcade"

class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.BLACK)

        # SpriteLists
        self.player_list = arcade.SpriteList()

        self.agua_solido_list = None
        self.veneno_list = None
        self.fondo_list = None
        self.plataformas_moviles = None
        self.agua_estela = None
        self.fuego_galaxi = None
        self.puerta_chico = None
        self.puerta_chica = None

        self.tile_map = None
        self.player_sprite = None
        self.physics_engine = None

    def setup(self):
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        map_name = os.path.join(BASE_PATH, "nivel_acuatico.tmx")

        layer_options = {
            "capa_agua_solido": {"use_spatial_hash": True},
            "capa_veneno": {"use_spatial_hash": True},
            "capa_plataforma_movil": {"use_spatial_hash": True},
        }

        self.tile_map = arcade.load_tilemap(map_name, scaling=0.4, layer_options=layer_options)

        self.fondo_list = self.tile_map.sprite_lists.get("capa_fondo")
        self.agua_estela = self.tile_map.sprite_lists.get("capa_agua_estela")
        self.agua_solido_list = self.tile_map.sprite_lists.get("capa_agua_solido")
        self.plataformas_moviles = self.tile_map.sprite_lists.get("capa_plataforma_movil")
        self.veneno_list = self.tile_map.sprite_lists.get("capa_veneno")
        self.fuego_galaxi = self.tile_map.sprite_lists.get("capa_fuego_galaxi")
        self.puerta_chico = self.tile_map.sprite_lists.get("puerta_chico_acuatico")
        self.puerta_chica = self.tile_map.sprite_lists.get("puerta_chica_acuatico")

        # Crear jugador
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            0.5
        )
        self.player_sprite.center_x = 150
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.agua_solido_list,
            gravity_constant=0.8
        )

    def on_draw(self):
        self.clear()

        if self.fondo_list:
            self.fondo_list.draw()

        if self.agua_estela:
            self.agua_estela.draw()

        if self.agua_solido_list:
            self.agua_solido_list.draw()

        if self.plataformas_moviles:
            self.plataformas_moviles.draw()

        if self.veneno_list:
            self.veneno_list.draw()

        if self.fuego_galaxi:
            self.fuego_galaxi.draw()

        if self.puerta_chico:
            self.puerta_chico.draw()

        if self.puerta_chica:
            self.puerta_chica.draw()

        # Jugador
        self.player_list.draw()

    def on_update(self, delta_time):
        self.physics_engine.update()

        if arcade.check_for_collision_with_list(self.player_sprite, self.veneno_list):
            print("Has muerto por veneno")
            self.setup()

        if arcade.check_for_collision_with_list(self.player_sprite, self.fuego_galaxi):
            print("Has muerto por fuego")
            self.setup()

        if arcade.check_for_collision_with_list(self.player_sprite, self.puerta_chico):
            print("Puerta chico → siguiente nivel")

        if arcade.check_for_collision_with_list(self.player_sprite, self.puerta_chica):
            print("Puerta chica → siguiente nivel")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 15
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -5
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 5

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0


if __name__ == "__main__":
    game = MyGame()
    game.setup()
    arcade.run()
