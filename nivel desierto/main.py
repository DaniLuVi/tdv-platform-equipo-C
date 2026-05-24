import arcade
import os

# =========================================================================
# 1. CONFIGURACIÓN INICIAL
# =========================================================================
ANCHO_VENTANA = 1024
ALTO_VENTANA = 768
TITULO_VENTANA = "Nuestro Videojuego - Cooperativo Desierto"
DIRECTORIO_ACTUAL = os.path.dirname(__file__)

class JuegoDesierto(arcade.Window):
    def __init__(self):
        super().__init__(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA, antialiasing=False)
        
        # Entradas del teclado
        self.teclas_pulsadas = set()

        # Elementos del mapa y cámara
        self.escena = None
        self.camara = None
        
        # Listas de Sprites de los nuevos elementos
        self.lista_jugadores = arcade.SpriteList()
        self.monedas = arcade.SpriteList()
        self.agua = arcade.SpriteList()
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

    def setup(self):
        """ Configura el juego y carga los recursos """
        self.background_color = arcade.color.SKY_BLUE

        # -----------------------------------------------------------------
        # 2. CARGAR EL MAPA Y LA CÁMARA (.tmj)
        # -----------------------------------------------------------------
        # Buscamos tu mapa en formato TMJ
        # Buscamos tu mapa en formato TMJ (¡atención al guion bajo!)
        ruta_mapa = os.path.join(DIRECTORIO_ACTUAL, "desierto_mapa.tmj")
        try:
            mapa_tiled = arcade.load_tilemap(ruta_mapa, scaling=1.0)
            self.escena = arcade.Scene.from_tilemap(mapa_tiled)
        except Exception as e:
            print(f"Error al cargar el mapa: {e}")
            arcade.exit()
            return

        ancho_mapa = mapa_tiled.width * mapa_tiled.tile_width
        alto_mapa = mapa_tiled.height * mapa_tiled.tile_height

        # Configurar la cámara para que encaje PERFECTAMENTE el mapa entero
        self.camara = arcade.camera.Camera2D()
        self.camara.position = (ancho_mapa / 2, alto_mapa / 2)
        zoom_x = ANCHO_VENTANA / ancho_mapa
        zoom_y = ALTO_VENTANA / alto_mapa
        self.camara.zoom = min(zoom_x, zoom_y)

        # -----------------------------------------------------------------
        # 3. EXTRAER LAS CAPAS DE TILED (Sólidas vs Triggers)
        # -----------------------------------------------------------------
        # Capas sólidas (Paredes y suelo donde se puede caminar)
        plataformas = arcade.SpriteList()
        for nombre_capa in ["suelo", "arena", "plataformas"]:
            try:
                plataformas.extend(self.escena.get_sprite_list(nombre_capa))
            except:
                pass

        # Capa de Monedas
        try:
            self.monedas = self.escena.get_sprite_list("monedas")
        except:
            pass

        # Capa de Agua
        try:
            self.agua = self.escena.get_sprite_list("agua")
        except:
            pass

        # Capas de las Puertas
        try:
            self.puerta_chico = self.escena.get_sprite_list("puerta_chico")
        except:
            pass
        try:
            self.puerta_chica = self.escena.get_sprite_list("puerta_chica")
        except:
            pass

        # -----------------------------------------------------------------
        # 4. CREAR A LOS PERSONAJES
        # -----------------------------------------------------------------
        def crear_personaje(nombre, color_error):
            ruta = os.path.join(DIRECTORIO_ACTUAL, f"{nombre}.png")
            if os.path.exists(ruta):
                sprite = arcade.Sprite(ruta)
            else:
                sprite = arcade.SpriteSolidColor(96, 144, color_error)
            sprite.width = 96
            sprite.height = 144
            return sprite

        # Posicionamos al chico arriba a la izquierda y a la chica abajo a la derecha
        self.chico = crear_personaje("chico", arcade.color.RED)
        self.chico.center_x = 150
        self.chico.center_y = alto_mapa - 150

        self.chica = crear_personaje("chica", arcade.color.HOT_PINK)
        self.chica.center_x = ancho_mapa - 300
        self.chica.center_y = 400

        self.lista_jugadores.append(self.chico)
        self.lista_jugadores.append(self.chica)

        # Motores de físicas (solo para chocar con las plataformas sólidas)
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
            return # Si ya han ganado o perdido, congelamos el juego

        # --- Controles del Chico (WASD) ---
        self.chico.change_x = 0
        if arcade.key.A in self.teclas_pulsadas:
            self.chico.change_x = -5
        if arcade.key.D in self.teclas_pulsadas:
            self.chico.change_x = 5
        if arcade.key.W in self.teclas_pulsadas and self.motor_chico.can_jump():
            self.chico.change_y = 14

        # --- Controles de la Chica (Flechas) ---
        self.chica.change_x = 0
        if arcade.key.LEFT in self.teclas_pulsadas:
            self.chica.change_x = -5
        if arcade.key.RIGHT in self.teclas_pulsadas:
            self.chica.change_x = 5
        if arcade.key.UP in self.teclas_pulsadas and self.motor_chica.can_jump():
            self.chica.change_y = 14

        # Aplicar físicas de movimiento básico
        self.motor_chico.update()
        self.motor_chica.update()

        # -----------------------------------------------------------------
        # LÓGICA 1: RECOGER MONEDAS
        # -----------------------------------------------------------------
        for jugador in [self.chico, self.chica]:
            monedas_tocadas = arcade.check_for_collision_with_list(jugador, self.monedas)
            for moneda in monedas_tocadas:
                moneda.remove_from_sprite_lists()

        # -----------------------------------------------------------------
        # LÓGICA 2: PELIGRO - SUELO DE AGUA
        # -----------------------------------------------------------------
        # Si alguno toca el agua, reaparece en su sitio inicial
        if arcade.check_for_collision_with_list(self.chico, self.agua):
            self.chico.center_x = 150
            self.chico.center_y = 600 # Ajusta según la altura de tu mapa para que no caiga infinitamente
            self.chico.change_y = 0
            
        if arcade.check_for_collision_with_list(self.chica, self.agua):
            # Obtener el ancho del mapa de forma segura
            ancho_ref = self.chica.center_x if self.chica.center_x > 500 else 1000
            self.chica.center_x = ancho_ref - 100
            self.chica.center_y = 400
            self.chica.change_y = 0

        # -----------------------------------------------------------------
        # LÓGICA 3: CONDICIÓN DE VICTORIA (PUERTAS)
        # -----------------------------------------------------------------
        # Comprobar si el chico está tocando su puerta
        if arcade.check_for_collision_with_list(self.chico, self.puerta_chico):
            self.chico_en_meta = True
        else:
            self.chico_en_meta = False

        # Comprobar si la chica está tocando su puerta
        if arcade.check_for_collision_with_list(self.chica, self.puerta_chica):
            self.chica_en_meta = True
        else:
            self.chica_en_meta = False

        # Si AMBOS están en sus respectivas puertas a la vez... ¡Victoria!
        if self.chico_en_meta and self.chica_en_meta:
            self.juego_terminado = True
            print("¡VICTORIA COOPERATIVA! Ambos jugadores han llegado a las puertas.")

    # =========================================================================
    # DIBUJO
    # =========================================================================
    def on_draw(self):
        self.clear() 
        
        self.camara.use() 
        
        # Dibujamos el escenario de Tiled completo de fondo
        self.escena.draw()
        
        # Dibujamos a los dos personajes encima
        self.lista_jugadores.draw()

        # Si han ganado, pintamos un texto en mitad de la pantalla
        if self.juego_terminado:
            arcade.draw_text("¡VICTORIA!", ANCHO_VENTANA / 2, ALTO_VENTANA / 2,
                             arcade.color.GOLDENROD, font_size=50, anchor_x="center")


if __name__ == "__main__":
    juego = JuegoDesierto()
    juego.setup()
    arcade.run()