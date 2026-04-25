import arcade
import os

# --- Configuración ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800 
SCREEN_TITLE = "Duelo de Plataformas - Misión Cooperativa"

# Valores de física
GRAVITY = 0.5
PLAYER_JUMP_SPEED = 12
PLAYER_MOVEMENT_SPEED = 5
MAP_SCALING = 0.4  # Ajusta el mapa de 1920px a la ventana de 800px

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
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
        map_name = os.path.join(self.script_path, "sin nombre.tmx")

        # Configuración de capas para el mapa
        layer_options = {
            "Capa de patrones 1": {"use_spatial_hash": True}, # Suelos/Paredes
            "Capa de patrones 2": {"use_spatial_hash": True}, # Veneno
            "Capa de patrones 4": {"use_spatial_hash": True}, # Lava
            "Capa de patrones 5": {"use_spatial_hash": True}, # Agua mortal
            "Capa de patrones 6": {"use_spatial_hash": True}, # Puerta J1
            "Capa de patrones 7": {"use_spatial_hash": True}, # Puerta J2
        }

        # Cargar mapa
        try:
            tile_map = arcade.load_tilemap(map_name, scaling=MAP_SCALING, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
        except Exception as e:
            print(f"Error cargando el archivo TMX: {e}")
            return

        # --- JUGADOR 1 (Flechas) ---
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", 0.3)
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 150
        self.scene.add_sprite("Player1", self.player_sprite)

        # --- JUGADOR 2 (WASD) ---
        self.player_sprite2 = arcade.Sprite(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png", 0.3)
        self.player_sprite2.center_x = 200
        self.player_sprite2.center_y = 150
        self.scene.add_sprite("Player2", self.player_sprite2)

        # Motores de física (Gravedad y Colisiones con Capa 1)
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

        # Mostrar mensaje de victoria
        if self.victoria:
            arcade.draw_text("¡VICTORIA COOPERATIVA!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 
                             arcade.color.GOLD, 40, anchor_x="center", bold=True)
            arcade.draw_text("Presiona 'R' para reiniciar", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50, 
                             arcade.color.WHITE, 20, anchor_x="center")

    def on_update(self, delta_time):
        if self.victoria:
            return

        self.physics_engine.update()
        self.physics_engine2.update()

        # 1. Lógica de Muerte (Capas 2y4)
        capas_peligro = ["Capa de patrones 2", "Capa de patrones 5"]
        for nombre_capa in capas_peligro:
            try:
                capa = self.scene[nombre_capa]
                if arcade.check_for_collision_with_list(self.player_sprite, capa):
                    self.setup()
            except KeyError:
                pass
        capas_peligro2 = ["Capa de patrones 2", "Capa de patrones 4"]
        for nombre_capa in capas_peligro2:
            try:
                capa = self.scene[nombre_capa]
                if arcade.check_for_collision_with_list(self.player_sprite2, capa):
                    self.setup()
            except KeyError:
                pass

        # 2. Lógica de Victoria (J1 en Capa 6 Y J2 en Capa 7)
        try:
            en_puerta1 = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Capa de patrones 6"])
            en_puerta2 = arcade.check_for_collision_with_list(self.player_sprite2, self.scene["Capa de patrones 7"])

            if en_puerta1 and en_puerta2:
                self.victoria = True
        except KeyError:
            pass

    def on_key_press(self, key, modifiers):
        if self.victoria:
            if key == arcade.key.R: self.setup()
            return

        # Controles Jugador 1
        if key == arcade.key.UP and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # Controles Jugador 2
        if key == arcade.key.W and self.physics_engine2.can_jump():
            self.player_sprite2.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.A:
            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        # Frenar J1
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0
        # Frenar J2
        if key in (arcade.key.A, arcade.key.D):
            self.player_sprite2.change_x = 0

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
