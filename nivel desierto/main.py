import arcade
import os

# =========================================================================
# 1. CONFIGURACIÓN INICIAL
# =========================================================================
ANCHO_VENTANA = 1024
ALTO_VENTANA = 768
TITULO_VENTANA = "Nuestro Videojuego - Arcade 3.0"
DIRECTORIO_ACTUAL = os.path.dirname(__file__)

class JuegoDesierto(arcade.Window):
    def __init__(self):
        super().__init__(ANCHO_VENTANA, ALTO_VENTANA, TITULO_VENTANA)
        
        # Entradas del teclado
        self.teclas_pulsadas = set()

        # Elementos del mapa y cámara
        self.escena = None
        self.camara = None
        
        # REGLA ARCADE 3.0: Los personajes deben ir en una lista para dibujarse
        self.lista_jugadores = arcade.SpriteList()
        
        self.chico = None
        self.chica = None
        self.motor_chico = None
        self.motor_chica = None

    def setup(self):
        """ Configura el juego y carga los recursos """
        self.background_color = arcade.color.SKY_BLUE

        # -----------------------------------------------------------------
        # 2. CARGAR EL MAPA Y LA CÁMARA (Arcade 3.0)
        # -----------------------------------------------------------------
        ruta_mapa = os.path.join(DIRECTORIO_ACTUAL, "desierto_mapa.tmj") # <--- CAMBIO AQUÍ
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
        
        # Calculamos el zoom para el ancho y el alto, y nos quedamos con el más pequeño (min)
        # Así nos aseguramos de que el mapa nunca se salga de la pantalla por ningún lado
        zoom_x = ANCHO_VENTANA / ancho_mapa
        zoom_y = ALTO_VENTANA / alto_mapa
        self.camara.zoom = min(zoom_x, zoom_y)

        # Juntar todas las capas sólidas
        plataformas = arcade.SpriteList()
        for nombre_capa in ["suelo", "arena", "plataformas"]:
            try:
                capa_encontrada = self.escena.get_sprite_list(nombre_capa)
                plataformas.extend(capa_encontrada)
            except:
                pass # Si no existe la capa, la ignora sin dar error

        # -----------------------------------------------------------------
        # 3. CREAR A LOS PERSONAJES
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

        # Crear y posicionar
        self.chico = crear_personaje("chico", arcade.color.RED)
        self.chico.center_x = 150
        self.chico.center_y = alto_mapa - 150

        self.chica = crear_personaje("chica", arcade.color.HOT_PINK)
        self.chica.center_x = ancho_mapa - 300
        self.chica.center_y = 400

        # ¡OBLIGATORIO ARCADE 3.0! Meterlos en la lista de jugadores
        self.lista_jugadores.append(self.chico)
        self.lista_jugadores.append(self.chica)

        # -----------------------------------------------------------------
        # 4. MOTOR DE FÍSICAS
        # -----------------------------------------------------------------
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
        # Controles del Chico (WASD)
        self.chico.change_x = 0
        if arcade.key.A in self.teclas_pulsadas:
            self.chico.change_x = -5
        if arcade.key.D in self.teclas_pulsadas:
            self.chico.change_x = 5
        if arcade.key.W in self.teclas_pulsadas and self.motor_chico.can_jump():
            self.chico.change_y = 14

        # Controles de la Chica (Flechas)
        self.chica.change_x = 0
        if arcade.key.LEFT in self.teclas_pulsadas:
            self.chica.change_x = -5
        if arcade.key.RIGHT in self.teclas_pulsadas:
            self.chica.change_x = 5
        if arcade.key.UP in self.teclas_pulsadas and self.motor_chica.can_jump():
            self.chica.change_y = 14

        # Físicas y colisiones
        self.motor_chico.update()
        self.motor_chica.update()

    # =========================================================================
    # DIBUJO
    # =========================================================================
    def on_draw(self):
        self.clear() 
        
        self.camara.use() 
        self.escena.draw()
        
        # ARCADE 3.0: Se dibuja la lista entera, no los personajes de uno en uno
        self.lista_jugadores.draw()


# Arrancar el programa
if __name__ == "__main__":
    juego = JuegoDesierto()
    juego.setup()
    arcade.run()