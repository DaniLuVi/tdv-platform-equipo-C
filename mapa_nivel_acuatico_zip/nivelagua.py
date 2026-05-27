import arcade
import os

# ---------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 774
SCREEN_TITLE = "Nivel Acuático – Arcade"

GRAVITY = 1.0
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 18

class Piraña(arcade.Sprite):
    def __init__(self, x, y, muros):
        super().__init__()

        self.textura_izq = arcade.load_texture(os.path.join("assets", "piraña.png"))
        self.textura_der = self.textura_izq.flip_left_right()
        
        self.texture = self.textura_der 
        self.scale = 0.15

        self.center_x = x
        self.center_y = y
        self.change_x = 5  # Velocidad de nado
        self.muros = muros

    def update(self, delta_time):
        # Movemos la piraña
        self.center_x += self.change_x
        
        # Comprobamos si se ha chocado con alguna pared
        if arcade.check_for_collision_with_list(self, self.muros):

            if len(self.muros) > 0:
                # Si choca, retrocedemos un paso
                self.center_x -= self.change_x
                # Y cambiamos la dirección
                self.change_x *= -1
    
            if self.change_x < 0:
                self.texture = self.textura_izq
            else:
                self.texture = self.textura_der

class MyGame(arcade.Window):

    def __init__(self):

        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            resizable=False
        )

        arcade.set_background_color(arcade.color.BLACK)

        # Ruta proyecto
        self.script_path = os.path.dirname(os.path.abspath(__file__))

        # Tilemap
        self.tile_map = None

        # Capas
        self.fondo_list = None
        self.agua_estela = None
        self.agua_solido_list = None
        self.plataformas_moviles = None
        self.veneno_list = None
        self.fuego_galaxi = None
        self.puerta_chico = None
        self.puerta_chica = None

        # Jugadores
        self.player_list = arcade.SpriteList()

        self.player_sprite = None
        self.player_sprite2 = None

        # Física
        self.physics_engine = None
        self.physics_engine2 = None

        # ---------------------------------------------------
        # PLATAFORMAS MÓVILES
        # ---------------------------------------------------

        # velocidad más lenta
        self.velocidad_plataformas = 2

        # límites
        self.altura_minima = 0
        self.altura_maxima = 0

        self.estado_plataformas = "esperando_arriba"

        # temporizador
        self.contador_pausa = 0

        # segundos de pausa
        self.tiempo_pausa = 2
        
        # ---------------------------------------------------
        # VICTORIA
        # ---------------------------------------------------

        self.victoria = False

    # ---------------------------------------------------
    # SETUP
    # ---------------------------------------------------

    def setup(self):

        map_name = os.path.join(
            self.script_path,
            "nivel_acuatico.tmx"
        )

        layer_options = {
            "capa_agua_solido": {"use_spatial_hash": True},
            "capa_veneno": {"use_spatial_hash": True},
            "capa_plataforma_movil": {"use_spatial_hash": True},
        }

        # ---------------------------------------------------
        # CARGAR MAPA TEMPORAL
        # ---------------------------------------------------

        mapa_temp = arcade.load_tilemap(map_name)

        ancho_real = mapa_temp.width * mapa_temp.tile_width
        alto_real = mapa_temp.height * mapa_temp.tile_height

        escala_x = SCREEN_WIDTH / ancho_real
        escala_y = SCREEN_HEIGHT / alto_real

        escala_auto = min(escala_x, escala_y)

        # ---------------------------------------------------
        # CARGAR TILEMAP DEFINITIVO
        # ---------------------------------------------------

        self.tile_map = arcade.load_tilemap(
            map_name,
            scaling=escala_auto,
            layer_options=layer_options
        )

        # ---------------------------------------------------
        # CAPAS
        # ---------------------------------------------------

        self.fondo_list = self.tile_map.sprite_lists.get("capa_fondo")

        self.agua_estela = self.tile_map.sprite_lists.get(
            "capa_agua_estela"
        )

        self.agua_solido_list = self.tile_map.sprite_lists.get(
            "capa_agua_solido"
        )

        self.plataformas_moviles = self.tile_map.sprite_lists.get(
            "capa_plataforma_movil"
        )

        self.veneno_list = self.tile_map.sprite_lists.get(
            "capa_veneno"
        )

        self.fuego_galaxi = self.tile_map.sprite_lists.get(
            "capa_fuego_galaxi"
        )

        self.puerta_chico = self.tile_map.sprite_lists.get(
            "puerta_chico_acuatico"
        )

        self.puerta_chica = self.tile_map.sprite_lists.get(
            "puerta_chica_acuatico"
        )

        # ---------------------------------------------------
        # TAMAÑO MAPA
        # ---------------------------------------------------

        ancho_mapa = (
            self.tile_map.width
            * self.tile_map.tile_width
            * self.tile_map.scaling
        )

        alto_mapa = (
            self.tile_map.height
            * self.tile_map.tile_height
            * self.tile_map.scaling
        )

        self.set_size(int(ancho_mapa), int(alto_mapa))

        # ---------------------------------------------------
        # LÍMITES PLATAFORMAS
        # ---------------------------------------------------

        if self.plataformas_moviles:

            # usamos bottom en vez de center_y
            self.altura_maxima = self.plataformas_moviles[0].bottom

            # cuánto bajan
            self.altura_minima = self.altura_maxima - 102

        # ---------------------------------------------------
        # JUGADORES
        # ---------------------------------------------------

        self.player_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("chica.png", 0.08)
        self.player_sprite.center_x = 80
        self.player_sprite.center_y = 100

        self.player_list.append(self.player_sprite)

        self.player_sprite2 = arcade.Sprite("chico.png", 0.08)
        self.player_sprite2.center_x = ancho_mapa - 80
        self.player_sprite2.center_y = 100

        self.player_list.append(self.player_sprite2)

        # ---------------------------------------------------
        # PAREDES
        # ---------------------------------------------------

        paredes = self.agua_solido_list

        # ---------------------------------------------------
        # ENEMIGOS
        # ---------------------------------------------------
        
        self.lista_enemigos = arcade.SpriteList()
        pirana1 = Piraña(x=450, y=250, muros=paredes)
        pirana2 = Piraña(x=300, y=250, muros=paredes)
        pirana3 = Piraña(x=400, y=500, muros=paredes)
        
        self.lista_enemigos.append(pirana1)
        self.lista_enemigos.append(pirana2)
        self.lista_enemigos.append(pirana3)

        # ---------------------------------------------------
        # FÍSICA
        # ---------------------------------------------------

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=paredes,
            platforms=self.plataformas_moviles,
            gravity_constant=GRAVITY
        )

        self.physics_engine2 = arcade.PhysicsEnginePlatformer(
            self.player_sprite2,
            walls=paredes,
            platforms=self.plataformas_moviles,
            gravity_constant=GRAVITY
        )

    # ---------------------------------------------------
    # DIBUJAR
    # ---------------------------------------------------

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

        self.player_list.draw()
        self.lista_enemigos.draw()

        # ---------------------------------------------------
        # MENSAJE VICTORIA
        # ---------------------------------------------------

        if self.victoria:

            arcade.draw_lrbt_rectangle_filled(
            SCREEN_WIDTH / 2 - 250,
            SCREEN_WIDTH / 2 + 250,
            SCREEN_HEIGHT / 2 - 110,
            SCREEN_HEIGHT / 2 + 110,
            (0, 0, 0, 180)
        )

            arcade.draw_text(
                "¡VICTORIA COOPERATIVA!",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 30,
                arcade.color.GOLD,
                32,
                anchor_x="center",
                bold=True
            )

            arcade.draw_text(
                "Pulsa R para reiniciar",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 60,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )

    # ---------------------------------------------------
    # UPDATE
    # ---------------------------------------------------

    def on_update(self, delta_time):
        
        if self.victoria:
            return

        # actualizar físicas
        self.physics_engine.update()
        self.physics_engine2.update()
        self.lista_enemigos.update()

        for pirana in self.lista_enemigos:
            if arcade.check_for_collision(pirana, self.player_sprite) or arcade.check_for_collision(pirana, self.player_sprite2):
                self.setup()  # Reiniciar el nivel
                return
        # ---------------------------------------------------
        # PLATAFORMAS CON PAUSAS
        # ---------------------------------------------------

        if self.plataformas_moviles:

            # -----------------------------
            # ESPERANDO ARRIBA
            # -----------------------------

            if self.estado_plataformas == "esperando_arriba":

                self.contador_pausa += delta_time

                if self.contador_pausa >= self.tiempo_pausa:

                    self.contador_pausa = 0
                    self.estado_plataformas = "bajando"

            # -----------------------------
            # BAJANDO
            # -----------------------------

            elif self.estado_plataformas == "bajando":

                for plataforma in self.plataformas_moviles:
                    plataforma.center_y -= self.velocidad_plataformas

                if (
                    self.plataformas_moviles[0].bottom
                    <= self.altura_minima
                ):

                    self.estado_plataformas = "esperando_abajo"

            # -----------------------------
            # ESPERANDO ABAJO
            # -----------------------------

            elif self.estado_plataformas == "esperando_abajo":

                self.contador_pausa += delta_time

                if self.contador_pausa >= self.tiempo_pausa:

                    self.contador_pausa = 0
                    self.estado_plataformas = "subiendo"

            # -----------------------------
            # SUBIENDO
            # -----------------------------

            elif self.estado_plataformas == "subiendo":

                for plataforma in self.plataformas_moviles:
                    plataforma.center_y += self.velocidad_plataformas

                if (
                    self.plataformas_moviles[0].bottom
                    >= self.altura_maxima
                ):

                    self.estado_plataformas = "esperando_arriba"

        # ---------------------------------------------------
        # MUERTE CHICA
        # ---------------------------------------------------

        if (
            self.agua_estela
            and arcade.check_for_collision_with_list(
                self.player_sprite,
                self.agua_estela
            )
        ):

            self.setup()
            return

        if (
            self.veneno_list
            and arcade.check_for_collision_with_list(
                self.player_sprite,
                self.veneno_list
            )
        ):

            self.setup()
            return

        # ---------------------------------------------------
        # MUERTE CHICO
        # ---------------------------------------------------

        if (
            self.fuego_galaxi
            and arcade.check_for_collision_with_list(
                self.player_sprite2,
                self.fuego_galaxi
            )
        ):

            self.setup()
            return

        if (
            self.veneno_list
            and arcade.check_for_collision_with_list(
                self.player_sprite2,
                self.veneno_list
            )
        ):

            self.setup()
            return

        # ---------------------------------------------------
        # PUERTAS
        # ---------------------------------------------------

        chica_ok = (
            arcade.check_for_collision_with_list(
                self.player_sprite,
                self.puerta_chica
            )
            if self.puerta_chica
            else False
        )

        chico_ok = (
            arcade.check_for_collision_with_list(
                self.player_sprite2,
                self.puerta_chico
            )
            if self.puerta_chico
            else False
        )

        if chica_ok and chico_ok:

            self.victoria = True

            # parar personajes
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

            self.player_sprite2.change_x = 0
            self.player_sprite2.change_y = 0

        return

    # ---------------------------------------------------
    # TECLAS PRESIONADAS
    # ---------------------------------------------------

    def on_key_press(self, key, modifiers):

        # ---------------- CHICA ----------------

        if key == arcade.key.UP:

            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED

        elif key == arcade.key.LEFT:

            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED

        elif key == arcade.key.RIGHT:

            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # ---------------- CHICO ----------------

        if key == arcade.key.W:

            if self.physics_engine2.can_jump():
                self.player_sprite2.change_y = PLAYER_JUMP_SPEED

        elif key == arcade.key.A:

            self.player_sprite2.change_x = -PLAYER_MOVEMENT_SPEED

        elif key == arcade.key.D:

            self.player_sprite2.change_x = PLAYER_MOVEMENT_SPEED
            
        # reiniciar
        if key == arcade.key.R and self.victoria:

            self.victoria = False
            self.setup()

    # ---------------------------------------------------
    # SOLTAR TECLAS
    # ---------------------------------------------------

    def on_key_release(self, key, modifiers):

        # chica
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0

        # chico
        if key in (arcade.key.A, arcade.key.D):
            self.player_sprite2.change_x = 0



# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

def main():

    game = MyGame()

    game.setup()

    arcade.run()


if __name__ == "__main__":
    main()