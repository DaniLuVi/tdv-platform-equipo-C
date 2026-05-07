import arcade
import os

# --- Configuración ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700 
SCREEN_TITLE = "Duelo de Plataformas - Misión Cooperativa"

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
        self.victoria = False

    def setup(self):
        """ Configuración inicial y reinicio """
        self.victoria = False
        
        # IMPORTANTE: Asegúrate de que este archivo esté en la misma carpeta que el .py
        map_name = os.path.join(self.script_path, "sin nombre.tmx")

        # Configuración de capas
        layer_options = {
            "Capa de patrones 1": {"use_spatial_hash": True},
            "Capa de patrones 2": {"use_spatial_hash": True},
            "Capa de patrones 4": {"use_spatial_hash": True},
            "Capa de patrones 5": {"use_spatial_hash": True},
            "Capa de patrones 6": {"use_spatial_hash": True},
            "Capa de patrones 7": {"use_spatial_hash": True},
        }

        try:
            # 1. Calculamos la escala automática para que quepa en la pantalla
            mapa_temp = arcade.load_tilemap(map_name)
            alto_real_mapa = mapa_temp.height * mapa_temp.tile_height
            escala_auto = SCREEN_HEIGHT / alto_real_mapa
            
            # 2. Cargamos el mapa con esa escala
            tile_map = arcade.load_tilemap(map_name, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
            print("Mapa cargado con éxito.")
        except Exception as e:
            print(f"Error cargando el archivo TMX: {e}")
            self.scene = None
            return

        # --- JUGADOR 1 (Chica) ---
        self.player_sprite = arcade.Sprite("chica.png", 0.1)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 150
        self.scene.add_sprite("Player1", self.player_sprite)

        # --- JUGADOR 2 (Chico) ---
        self.player_sprite2 = arcade.Sprite("chico.png", 0.1)
        self.player_sprite2.center_x = 200
        self.player_sprite2.center_y = 150
        self.scene.add_sprite("Player2", self.player_sprite2)

        # Motores de física
        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, gravity_constant=GRAVITY, walls=muros)
        self.physics_engine2 = arcade.PhysicsEnginePlatformer(self.player_sprite2, gravity_constant=GRAVITY, walls=muros)

    def on_draw(self):
        self.clear()
        if self.scene:
            self.scene.draw()
        else:
            arcade.draw_text("ERROR: No se encontró el archivo .tmx", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 
                             arcade.color.RED, 20, anchor_x="center")

        if self.victoria:
            arcade.draw_text("¡VICTORIA COOPERATIVA!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 
                             arcade.color.GOLD, 40, anchor_x="center", bold=True)
            arcade.draw_text("Presiona 'R' para reiniciar", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, 
                             arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        # Si hubo un error en setup o ya ganamos, no actualizamos
        if self.victoria or self.physics_engine is None or self.physics_engine2 is None:
            return

        self.physics_engine.update()
        self.physics_engine2.update()

        # 1. Lógica de Muerte
        capas_muerte_j1 = ["Capa de patrones 2", "Capa de patrones 5"]
        capas_muerte_j2 = ["Capa de patrones 2", "Capa de patrones 4"]

        for j, capas in [(self.player_sprite, capas_muerte_j1), (self.player_sprite2, capas_muerte_j2)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(j, self.scene[nombre]):
                        self.setup()
                        return
                except (KeyError, TypeError):
                    pass

        # 2. Lógica de Victoria
        try:
            en_puerta1 = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Capa de patrones 6"])
            en_puerta2 = arcade.check_for_collision_with_list(self.player_sprite2, self.scene["Capa de patrones 7"])
            if en_puerta1 and en_puerta2:
                self.victoria = True
        except (KeyError, TypeError):
            pass

    def on_key_press(self, key, modifiers):
        if self.victoria:
            if key == arcade.key.R: self.setup()
            return

        if self.physics_engine and self.physics_engine2:
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