import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Nivel Final"
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 12
PLAYER_MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.EERIE_BLACK)

        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.scene = None

        self.player_sprite = None
        self.player_sprite2 = None

        self.physics_engine = None
        self.physics_engine2 = None

        self.victoria = False
        self.palanca_activada = False

    def setup(self):
        self.victoria = False
        self.palanca_activada = False

        map_name = os.path.join(self.script_path, "nivel_final.tmx")

        layer_options = {
            "Capa de patrones 1": {"use_spatial_hash": True},
            "veneno": {"use_spatial_hash": True},
            "lava": {"use_spatial_hash": True},
            "agua": {"use_spatial_hash": True},
            "puertachica": {"use_spatial_hash": True},
            "puertachico": {"use_spatial_hash": True},
            "boton1": {"use_spatial_hash": True},
            "boton2": {"use_spatial_hash": True},
            "palanca": {"use_spatial_hash": True},
            "palancaactiva": {"use_spatial_hash": True},
            "muro1": {"use_spatial_hash": True},
            "muro2": {"use_spatial_hash": True},
            "muro3": {"use_spatial_hash": True},
        }

        # Cargar mapa con escala automática
        mapa_temp = arcade.load_tilemap(map_name)
        alto_real_mapa = mapa_temp.height * mapa_temp.tile_height
        escala_auto = SCREEN_HEIGHT / alto_real_mapa

        tile_map = arcade.load_tilemap(map_name, scaling=escala_auto, layer_options=layer_options)
        self.scene = arcade.Scene.from_tilemap(tile_map)

        # Guardar posiciones originales de muros
        for nombre in ["muro1", "muro2", "muro3"]:
            if nombre in self.scene:
                for muro in self.scene[nombre]:
                    muro.original_x = muro.center_x
                    muro.original_y = muro.center_y

        # Jugador 1
        self.player_sprite = arcade.Sprite("chica.png", 0.07)
        self.player_sprite.center_x = 150
        self.player_sprite.center_y = 750
        self.scene.add_sprite("Player1", self.player_sprite)

        # Jugador 2
        self.player_sprite2 = arcade.Sprite("chico.png", 0.07)
        self.player_sprite2.center_x = 190
        self.player_sprite2.center_y = 750
        self.scene.add_sprite("Player2", self.player_sprite2)

        # Crear lista de muros físicos
        muros = arcade.SpriteList()

        for nombre in ["Capa de patrones 1", "muro1", "muro2", "muro3"]:
            if nombre in self.scene:
                for sprite in self.scene[nombre]:
                    muros.append(sprite)

        # Motores de física
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=muros
        )
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2, gravity_constant=GRAVITY, walls=muros
        )

    def on_draw(self):
        self.clear()
        if self.scene:
            self.scene.draw()

        if self.victoria:
            arcade.draw_text("¡VICTORIA!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                             arcade.color.GOLD, 40, anchor_x="center", bold=True)
            arcade.draw_text("Presiona 'R' para reiniciar", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50,
                             arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        if self.victoria:
            return

        self.physics_engine.update()
        self.physics_engine2.update()

        # MUERTE
        capas_muerte_j1 = ["agua", "veneno"]
        capas_muerte_j2 = ["lava", "veneno"]

        for jugador, capas in [(self.player_sprite, capas_muerte_j1),
                               (self.player_sprite2, capas_muerte_j2)]:
            for nombre in capas:
                if nombre in self.scene:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.setup()
                        return

        # VICTORIA
        try:
            en_puerta1 = arcade.check_for_collision_with_list(self.player_sprite, self.scene["puertachica"])
            en_puerta2 = arcade.check_for_collision_with_list(self.player_sprite2, self.scene["puertachico"])
            if len(en_puerta1) and len(en_puerta2):
                self.victoria = True
        except:
            pass

        # BOTÓN 1 
        try:
            tocando_boton1 = (
                arcade.check_for_collision_with_list(self.player_sprite, self.scene["boton1"]) or
                arcade.check_for_collision_with_list(self.player_sprite2, self.scene["boton1"])
            )
        except:
            tocando_boton1 = False

        if "muro1" in self.scene:
            for muro in self.scene["muro1"]:
                if tocando_boton1:
                    muro.center_x = -10000
                    muro.center_y = -10000
                else:
                    muro.center_x = muro.original_x
                    muro.center_y = muro.original_y

        # BOTÓN 2 
        try:
            tocando_boton2 = (
                arcade.check_for_collision_with_list(self.player_sprite, self.scene["boton2"]) or
                arcade.check_for_collision_with_list(self.player_sprite2, self.scene["boton2"])
            )
        except:
            tocando_boton2 = False

        if "muro2" in self.scene:
            for muro in self.scene["muro2"]:
                if tocando_boton2:
                    muro.center_x = -10000
                    muro.center_y = -10000
                else:
                    muro.center_x = muro.original_x
                    muro.center_y = muro.original_y

        # PALANCA
        try:
            if not self.palanca_activada:
                tocando_palanca = (
                    arcade.check_for_collision_with_list(self.player_sprite, self.scene["palanca"]) or
                    arcade.check_for_collision_with_list(self.player_sprite2, self.scene["palanca"])
                )
            else:
                tocando_palanca = False
        except:
            tocando_palanca = False

        if tocando_palanca:
            self.palanca_activada = True

        if self.palanca_activada:
            if "palancaactiva" in self.scene:
                self.scene["palancaactiva"].visible = True

            if "palanca" in self.scene:
                self.scene["palanca"].visible = False

            if "muro3" in self.scene:
                for muro in self.scene["muro3"]:
                    muro.center_x = -10000
                    muro.center_y = -10000

    def on_key_press(self, key, modifiers):
        if self.victoria and key == arcade.key.R:
            self.setup()
            return

        # Jugador 1
        if key == arcade.key.UP and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # Jugador 2
        if key == arcade.key.W and self.physics_engine2.can_jump():
            self.player_sprite2.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.A:
            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0
        if key in (arcade.key.A, arcade.key.D):
            self.player_sprite2.change_x = 0


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
