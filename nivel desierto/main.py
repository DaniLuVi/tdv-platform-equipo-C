import arcade
import os

# =========================================================================
# 1. CONFIGURACIÓN INICIAL
# =========================================================================
TOTAL_MONEDAS = 12
ANCHO_VENTANA = 760
ALTO_VENTANA = 768
TITULO_VENTANA = "Nuestro Videojuego - Cooperativo Extremo"
DIRECTORIO_ACTUAL = os.path.dirname(__file__)

class JuegoDesierto(arcade.Window):
    def __init__(self):
        super().__init__(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA, antialiasing=False)
        
        self.textura_fondo = None
        self.ancho_mapa = 0
        self.alto_mapa = 0
        self.tiempo_total = 120  # segundos (ajústalo a lo que quieras)
        self.tiempo_restante = self.tiempo_total
        # Entradas del teclado
        self.teclas_pulsadas = set()

        # Elementos del mapa y cámara
        self.escena = None
        self.camara = None
        
        # Listas de Sprites de los elementos
        self.lista_jugadores = arcade.SpriteList()
        self.monedas = arcade.SpriteList()
        self.agua = arcade.SpriteList()
        self.lava = arcade.SpriteList()   # <- Nueva lista para la lava
        self.veneno = arcade.SpriteList()
        self.puerta_chico = arcade.SpriteList()
        self.puerta_chica = arcade.SpriteList()
        
        # Variables de control de personajes y motores
        self.chico = None
        self.chica = None
        self.motor_chico = None
        self.motor_chica = None
        
        # Estados del juego
        self.chico_en_meta = False
        self.chica_en_meta = False
        self.juego_terminado = False
        self.contador_monedas = 0

    def setup(self):
        """ Configura el juego y carga los recursos """
        self.background_color = arcade.color.SKY_BLUE

        # -----------------------------------------------------------------
        # 2. CARGAR EL MAPA Y LA CÁMARA (.tmj)
        # -----------------------------------------------------------------
        ruta_mapa = os.path.join("nivel desierto", "desierto_mapa.tmj")
        try:
            mapa_tiled = arcade.load_tilemap(ruta_mapa, scaling=1.0)
            self.escena = arcade.Scene.from_tilemap(mapa_tiled)
        except Exception as e:
            print(f"Error al cargar el mapa: {e}")
            arcade.exit()
            return

        # Modifica esta parte en tu setup():
        self.ancho_mapa = mapa_tiled.width * mapa_tiled.tile_width
        self.alto_mapa = mapa_tiled.height * mapa_tiled.tile_height

        # Configurar la cámara usando las nuevas variables con self.
        self.camara = arcade.camera.Camera2D()
        self.camara.position = (self.ancho_mapa / 2, self.alto_mapa / 2)
        zoom_x = ANCHO_VENTANA / self.ancho_mapa
        zoom_y = ALTO_VENTANA / self.alto_mapa
        self.camara.zoom = min(zoom_x, zoom_y)

        # --- CARGAR TU IMAGEN DE FONDO AQUÍ ---
        # Coloca tu imagen dentro de la carpeta "nivel desierto" junto a tu mapa
        ruta_fondo = os.path.join("nivel desierto", "fondo desierto.png") 
        if os.path.exists(ruta_fondo):
            self.textura_fondo = arcade.load_texture(ruta_fondo)
        else:
            print(f"Advertencia: No se encontró la imagen de fondo en {ruta_fondo}")

        # -----------------------------------------------------------------
        # 3. EXTRAER LAS CAPAS DE TILED
        # -----------------------------------------------------------------
        # Capas sólidas (Paredes y suelo)
        plataformas = arcade.SpriteList()
        for nombre_capa in ["suelo", "arena", "plataformas"]:
            try:
                plataformas.extend(self.escena.get_sprite_list(nombre_capa))
            except:
                pass

        # Cargar el resto de capas de forma independiente (Triggers)
        try: self.monedas = self.escena.get_sprite_list("monedas")
        except: pass

        try: self.agua = self.escena.get_sprite_list("agua")
        except: pass

        try: self.lava = self.escena.get_sprite_list("lava") # <- Cargamos la lava
        except: pass

        try: self.veneno = self.escena.get_sprite_list("veneno")
        except: pass

        try: self.puerta_chico = self.escena.get_sprite_list("puerta_chico")
        except: pass
        
        try: self.puerta_chica = self.escena.get_sprite_list("puerta_chica")
        except: pass

        # -----------------------------------------------------------------
        # 4. CREAR A LOS PERSONAJES
        # -----------------------------------------------------------------
        def crear_personaje(nombre, color_error):
            ruta = os.path.join(f"{nombre}.png")
            if os.path.exists(ruta):
                sprite = arcade.Sprite(ruta)
            else:
                sprite = arcade.SpriteSolidColor(96, 144, color_error)
            sprite.width = 96
            sprite.height = 144
            return sprite

        self.chico = crear_personaje("chico", arcade.color.BLUE) # Controles WASD
        self.chico.center_x = 150
        self.chico.center_y = self.alto_mapa - 150

        self.chica = crear_personaje("chica", arcade.color.RED) # Controles Flechas
        self.chica.center_x = self.ancho_mapa - 300
        self.chica.center_y = 400

        self.lista_jugadores.append(self.chico)
        self.lista_jugadores.append(self.chica)

        # Motores de físicas (solo chocan con las plataformas sólidas, los fluidos los atraviesan)
        self.motor_chico = arcade.PhysicsEnginePlatformer(self.chico, gravity_constant=0.8, walls=plataformas)
        self.motor_chica = arcade.PhysicsEnginePlatformer(self.chica, gravity_constant=0.8, walls=plataformas)

    # =========================================================================
    # CONTROLES Y ACTUALIZACIÓN
    # =========================================================================
    def on_key_press(self, key, modifiers):
        self.teclas_pulsadas.add(key)

    def on_key_release(self, key, modifiers):
        if key in self.teclas_pulsadas:
            self.teclas_pulsadas.remove(key)

    def on_update(self, delta_time):
        if self.juego_terminado:
            return 
        
        self.tiempo_restante -= delta_time

        # --- Controles del Chico (WASD) ---
        self.chico.change_x = 0
        if arcade.key.A in self.teclas_pulsadas:
            self.chico.change_x = -8
        if arcade.key.D in self.teclas_pulsadas:
            self.chico.change_x = 8
        if arcade.key.W in self.teclas_pulsadas and self.motor_chico.can_jump():
            self.chico.change_y = 22

        # --- Controles de la Chica (Flechas) ---
        self.chica.change_x = 0
        if arcade.key.LEFT in self.teclas_pulsadas:
            self.chica.change_x = -8
        if arcade.key.RIGHT in self.teclas_pulsadas:
            self.chica.change_x = 8
        if arcade.key.UP in self.teclas_pulsadas and self.motor_chica.can_jump():
            self.chica.change_y = 22

        # Aplicar movimientos y gravedades
        self.motor_chico.update()
        self.motor_chica.update()

        # -----------------------------------------------------------------
        # LÓGICA 1: RECOGER MONEDAS
        # -----------------------------------------------------------------
        for jugador in [self.chico, self.chica]:
            monedas_tocadas = arcade.check_for_collision_with_list(jugador, self.monedas)
            for moneda in monedas_tocadas:
                moneda.remove_from_sprite_lists()
                self.contador_monedas += 1

        # -----------------------------------------------------------------
        # LÓGICA 2: REGLAS DE SUPERVIVENCIA (Agua, Lava, Veneno y Tiempo)
        # -----------------------------------------------------------------
        if self.tiempo_restante <= 0:
            self.tiempo_restante = 0
            self.juego_terminado = True
            print("¡GAME OVER! Se acabó el tiempo.")
        # REGLA 1: Si la chica toca el AGUA -> GAME OVER
        if arcade.check_for_collision_with_list(self.chica, self.agua):
            self.juego_terminado = True
            print("¡GAME OVER! La chica ha tocado el agua.")
            
        # REGLA 2: Si el chico toca la LAVA -> GAME OVER
        if arcade.check_for_collision_with_list(self.chico, self.lava):
            self.juego_terminado = True
            print("¡GAME OVER! El chico ha tocado la lava.")

        # REGLA 3: Si CUALQUIERA toca el VENENO -> GAME OVER
        if arcade.check_for_collision_with_list(self.chico, self.veneno) or \
           arcade.check_for_collision_with_list(self.chica, self.veneno):
            self.juego_terminado = True
            print("¡GAME OVER! Un jugador ha tocado el veneno.")

        # -----------------------------------------------------------------
        # LÓGICA 3: CONDICIÓN DE VICTORIA (PUERTAS)
        # -----------------------------------------------------------------
        self.chico_en_meta = bool(arcade.check_for_collision_with_list(self.chico, self.puerta_chico))
        self.chica_en_meta = bool(arcade.check_for_collision_with_list(self.chica, self.puerta_chica))

        if (self.chico_en_meta and 
            self.chica_en_meta and 
            self.contador_monedas >= TOTAL_MONEDAS):

            self.juego_terminado = True
            print("¡VICTORIA COOPERATIVA!")

    # =========================================================================
    # DIBUJO
    # =========================================================================
    def on_draw(self):
        self.clear()

        # -------------------------------
        # DIBUJAR EL MUNDO DEL JUEGO
        # -------------------------------
        self.camara.use()

        self.escena.draw()
        self.lista_jugadores.draw()

        # -------------------------------
        # DIBUJAR LA INTERFAZ (HUD)
        # -------------------------------
        self.use()

        # Fondo del contador
        arcade.draw_lrbt_rectangle_filled(
            1535, 1800,
            1670,   # bottom
            1800,   # top
            arcade.color.GOLDENROD
        )

        arcade.draw_text(
            f"Monedas: {self.contador_monedas}",
            ANCHO_VENTANA + 800,
            ALTO_VENTANA + 975,
            arcade.color.BLACK,
            34,
            bold=True,
        )
        arcade.draw_text(
            f"Tiempo: {int(self.tiempo_restante)}",
            ANCHO_VENTANA + 800,
            ALTO_VENTANA + 930,
            arcade.color.BLACK,
            34,
            bold=True,
        )
        

        # -------------------------------
        # MENSAJES FINALES
        # -------------------------------
        if self.juego_terminado:
            if self.chico_en_meta and self.chica_en_meta:
                arcade.draw_text(
                    "¡VICTORIA!",
                    ANCHO_VENTANA / 2,
                    ALTO_VENTANA / 2,
                    arcade.color.GOLDENROD,
                    font_size=50,
                    anchor_x="center"
            )
            else:
                arcade.draw_text(
                    "GAME OVER",
                    ANCHO_VENTANA / 2,
                    ALTO_VENTANA / 2,
                    arcade.color.RED,
                    font_size=50,
                    anchor_x="center"
                )


if __name__ == "__main__":
    juego = JuegoDesierto()
    juego.setup()
    arcade.run()