import arcade
import os
import random

# --- Configuración ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "playa - cuidado con los cocos"

# Valores de física
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 12
PLAYER_MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Ruta del script actual
        self.script_path = os.path.dirname(os.path.abspath(__file__))

        self.scene = None
        self.player_sprite = None
        self.player_sprite2 = None
        self.physics_engine = None
        self.physics_engine2 = None

        self.objetos_que_caen = None
        self.tiempo_spawn = 0

        self.victoria = False

    def setup(self):
        self.victoria = False
        arcade.set_background_color(arcade.color.SKY_BLUE)

        map_name = os.path.join(self.script_path, "nivel2real.tmx")
        print("SETUP LLAMADO")
        print("TMX que está cargando Arcade:", map_name)

        layer_options = {
            "Capa de patrones 1": {"use_spatial_hash": True},
            "Capa de patrones 7": {"use_spatial_hash": True},
            "Capa de patrones 5": {"use_spatial_hash": True},
            "agua": {"use_spatial_hash": True},
            "Capa de patrones 3": {"use_spatial_hash": False},
            "Capa de patrones 2": {"use_spatial_hash": False},
            "Capa de patrones 4": {"use_spatial_hash": False},
        }

        # Cargamos el mapa sin capturar la excepción para ver cualquier error real
        mapa_temp = arcade.load_tilemap(map_name)
        alto_real_mapa = mapa_temp.height * mapa_temp.tile_height
        escala_auto = SCREEN_HEIGHT / alto_real_mapa

        tile_map = arcade.load_tilemap(
            map_name,
            scaling=escala_auto,
            layer_options=layer_options
        )
        self.scene = arcade.Scene.from_tilemap(tile_map)
        print("Mapa cargado con éxito.")

        # --- CALCULAR TAMAÑO REAL DEL MAPA ---
        alto_mapa = tile_map.height * tile_map.tile_height * tile_map.scaling
        ancho_mapa = tile_map.width * tile_map.tile_width * tile_map.scaling

        # --- JUGADOR 1 (Chica) ESQUINA SUPERIOR IZQUIERDA ---
        self.player_sprite = arcade.Sprite("chica.png", 0.08)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = alto_mapa - 50
        self.scene.add_sprite("Player1", self.player_sprite)

        # --- JUGADOR 2 (Chico) ESQUINA INFERIOR DERECHA ---
        self.player_sprite2 = arcade.Sprite("chico.png", 0.08)
        self.player_sprite2.center_x = ancho_mapa - 50
        self.player_sprite2.center_y = 50
        self.scene.add_sprite("Player2", self.player_sprite2)

        # --- Objetos que caen ---
        self.objetos_que_caen = arcade.SpriteList()
        self.scene.add_sprite_list("ObjetosCaen", self.objetos_que_caen)
        self.tiempo_spawn = 0

        # Motores de física
        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            gravity_constant=GRAVITY,
            walls=muros
        )
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2,
            gravity_constant=GRAVITY,
            walls=muros
        )

    def crear_objeto_que_cae(self):
        """Crea un coco que cae desde arriba"""
        ruta = os.path.join(
            self.script_path,
            "WhatsApp_Image_2026-05-07_at_00.13.20-removebg-preview.png"
        )

        sprite = arcade.Sprite(ruta, 0.15)

        # Posición inicial aleatoria arriba
        sprite.center_x = random.randint(0, SCREEN_WIDTH)
        sprite.center_y = SCREEN_HEIGHT + 200

        # Velocidad hacia abajo
        sprite.change_y = -5

        self.objetos_que_caen.append(sprite)

    def on_draw(self):
        self.clear()

        if self.scene:
            self.scene.draw()

        # Dibujar los cocos encima de todo
        if self.objetos_que_caen:
            self.objetos_que_caen.draw()

        if self.victoria:
            arcade.draw_text(
                "¡VICTORIA!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.color.GOLD,
                40,
                anchor_x="center",
                bold=True
            )
            arcade.draw_text(
                "Presiona 'R' para reiniciar",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                arcade.color.WHITE,
                20,
                anchor_x="center"
            )

    def on_update(self, delta_time):
        if self.victoria:
            return

        self.physics_engine.update()
        self.physics_engine2.update()

        # --- MUERTE POR CAPAS ---
        capas_muerte_j1 = ["Capa de patrones 7", "agua"]
        capas_muerte_j2 = ["Capa de patrones 7", "Capa de patrones 5"]

        for jugador, capas in [
            (self.player_sprite, capas_muerte_j1),
            (self.player_sprite2, capas_muerte_j2)
        ]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(
                        jugador,
                        self.scene[nombre]
                    ):
                        self.setup()
                        return
                except KeyError:
                    pass

        # --- VICTORIA ---
        try:
            en_puerta1 = arcade.check_for_collision_with_list(
                self.player_sprite,
                self.scene["Capa de patrones 3"]
            )
            en_puerta2 = arcade.check_for_collision_with_list(
                self.player_sprite2,
                self.scene["Capa de patrones 2"]
            )
            if en_puerta1 and en_puerta2:
                self.victoria = True
        except KeyError:
            pass

        # --- OBJETOS QUE CAEN ---
        self.objetos_que_caen.update()

        # Generar cocos cada 1.5 segundos
        self.tiempo_spawn += delta_time
        if self.tiempo_spawn > 1.5:
            self.crear_objeto_que_cae()
            self.tiempo_spawn = 0

        # Colisión con jugadores
        for obj in self.objetos_que_caen:
            if (
                arcade.check_for_collision(obj, self.player_sprite)
                or arcade.check_for_collision(obj, self.player_sprite2)
            ):
                self.setup()
                return

        # Eliminar cocos fuera de pantalla
        for obj in self.objetos_que_caen:
            if obj.center_y < -100:
                obj.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        if self.victoria:
            if key == arcade.key.R:
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

