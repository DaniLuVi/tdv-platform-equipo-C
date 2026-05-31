from abc import ABC, abstractmethod
import arcade
import arcade.gui
import json
import math
import os
import random

# --- CONFIGURACIÓN DINÁMICA ---
# Obtenemos el tamaño del monitor para que casi lo ocupe todo
# (Le restamos un poco de margen para que se vea la barra de tareas)
monitor = arcade.get_display_size()
SCREEN_WIDTH = int(monitor[0] * 0.9)
SCREEN_HEIGHT = int(monitor[1] * 0.8)

# Ruta del archivo JSON en el que se va a guardar el progreso de una partida
ARCHIVO_GUARDADO = "progreso_partidas.json"

# Diccionario para almacenar el estado de cada nivel: no conseguido, conseguido o bloqueado
ESTADOS_NIVELES = {
    1: "no_conseguido",
    2: "bloqueado",
    3: "bloqueado",
    4: "bloqueado",
    5: "bloqueado"
}

# Diccionario para saber si la historia de un nivel ya se ha visto en esta sesión
HISTORIA_VISTA = {
    1: False,
    2: False,
    3: False,
    4: False,
    5: False
}

# ------------------ CONSTANTES ------------------

# Velocidad de movimiento, gravedad y salto en píxeles por frame
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_SPEED = 12

# Se usan para determinar la dirección del personaje
RIGHT_FACING = 0
LEFT_FACING = 1

# Tipos de zonas
LAVA = 0
AGUA = 1
VERDE = 2

PARTIDA_ACTUAL = None

#------------------- FUNCIONES DE GUARDADO Y CARGADO DE PARTIDAS -------------------
def obtener_nombre_ultima_partida():
    """Obtiene el nombre de la última partida guardada en el archivo JSON"""
    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r") as f:
                datos = json.load(f)
                if datos:
                    if len(datos) >= 10:
                        return "LLENO"
                    numero_partida =  max(int(nombre.split(" ")[1]) for nombre in datos.keys() if nombre.startswith("Partida "))
                    return numero_partida + 1
        except json.JSONDecodeError:
            return 1
    return 1


def guardar_partida():
    """Guarda el progreso de la partida en un archivo JSON"""
    global ESTADOS_NIVELES, PARTIDA_ACTUAL

    if PARTIDA_ACTUAL is None:
        res = obtener_nombre_ultima_partida()
        if res == "LLENO":
            print("No se pueden crear más de 10 partidas.")
            return
        PARTIDA_ACTUAL = "Partida " + str(res)

    datos = {}

    # Leer el archivo, si existe, para no borrar otras partidas guardadas
    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r") as f:
                datos = json.load(f)
        except json.JSONDecodeError:
            pass  # Si el archivo está corrupto, lo sobrescribiremos con la nueva partida
    
    
    datos[PARTIDA_ACTUAL] = ESTADOS_NIVELES

    # Guardamos los datos actualizados en el archivo
    with open(ARCHIVO_GUARDADO, "w") as f:
        json.dump(datos, f, indent=4)
        print(f"Partida guardada: {PARTIDA_ACTUAL}")

def cargar_partida(partida):
    """ Carga una partida"""
    global ESTADOS_NIVELES, PARTIDA_ACTUAL

    if os.path.exists(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r") as f:
                datos = json.load(f)

                # Verificamos si la partida existe
                if partida in datos:
                    ESTADOS_NIVELES.clear()
                    ESTADOS_NIVELES.update({int(k): v for k, v in datos[partida].items()})
                    PARTIDA_ACTUAL = partida
                    print(f"Partida cargada: {PARTIDA_ACTUAL}")
                    return True
        except Exception as e:
            print(f"Error al cargar la partida: {e}")

    return False


class SeleccionPartida(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

    def on_show_view(self):
        self.manager.enable()
        self.manager.clear()  # Limpiamos cualquier elemento previo del manager

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Contenedor Grid: Guardará las dos columnas separadas por 50 píxeles
        contenedor_columnas = arcade.gui.UIBoxLayout(vertical=False, space_between=100)
        
        # Las dos columnas: Guardarán un máximo de 5 botones cada una
        columna_1 = arcade.gui.UIBoxLayout(vertical=True, space_between=15)
        columna_2 = arcade.gui.UIBoxLayout(vertical=True, space_between=15)

        contenedor_columnas.add(columna_1)
        contenedor_columnas.add(columna_2)

        if os.path.exists(ARCHIVO_GUARDADO):
            try:
                with open(ARCHIVO_GUARDADO, "r") as f:
                    datos = json.load(f)
                    # Creamos un botón por cada partida guardada
                    for i, nombre_partida in enumerate(datos.keys()):
                        btn = arcade.gui.UIFlatButton(text=nombre_partida, width=250)

                        @btn.event("on_click")
                        def on_click_btn(event):
                            if cargar_partida(event.source.text):
                                if getattr(self.window, 'reproductor_menu', None):
                                    arcade.stop_sound(self.window.reproductor_menu)
                                    self.window.reproductor_menu = None

                                self.window.show_view(Mapa())

                        if i < 5:
                            columna_1.add(btn)
                        else:
                            columna_2.add(btn)

            except Exception as es:
                print(f"Error al cargar las partidas: {es}")

        anclaje_columnas = arcade.gui.UIAnchorLayout()
        anclaje_columnas.add(
            child=contenedor_columnas,
            anchor_x="center_x",
            anchor_y="center_y",
            align_x = -100  # Ajuste horizontal para que quede un poco más a la izquierda del centro
        )
        self.manager.add(anclaje_columnas)

        # Botón para volver al menú principal
        btn_volver = arcade.gui.UIFlatButton(text = "VOLVER AL MENÚ (ESC)", width=300)
        
        @btn_volver.event("on_click")
        def on_click_volver(event):
            self.window.show_view(MenuView())

        anclaje_volver = arcade.gui.UIAnchorLayout()
        anclaje_volver.add(
            child=btn_volver,
            anchor_x="center_x",
            anchor_y="bottom",
            align_y=60  # Lo separamos 60 píxeles del borde inferior de la ventana
        )
        self.manager.add(anclaje_volver)

    def on_draw(self):
        self.clear()
        arcade.draw_text("PARTIDAS GUARDADAS", self.window.width / 2, self.window.height * 0.85,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

# --- VISTA: MENÚ PRINCIPAL ---
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        # Variables para controlar el mensaje de error de "Continuar Partida"
        self.mostrar_error = False
        self.tiempo_error = 0.0

        # Creamos la lista para manejar los sprites
        self.lista_sprites = arcade.SpriteList()

        self.fondo = arcade.Sprite(os.path.join("assets", "fondo_inicio.png"))
        self.fondo.width = SCREEN_WIDTH
        self.fondo.height = SCREEN_HEIGHT
        self.fondo.center_x = SCREEN_WIDTH / 2
        self.fondo.center_y = SCREEN_HEIGHT / 2
        self.lista_sprites.append(self.fondo)

        # --- SPRITE 1 (Izquierda) ---
        self.sprite_1 = arcade.Sprite("chico.png", scale=1.0)
        self.sprite_1.center_x = SCREEN_WIDTH * 0.17  # 17% del ancho (izquierda)
        self.sprite_1.bottom = 20    # Suelo
        self.lista_sprites.append(self.sprite_1)

        # --- SPRITE 2 (Derecha) ---
        self.sprite_2 = arcade.Sprite("chica.png", scale=1.0)
        self.sprite_2.center_x = SCREEN_WIDTH * 0.72  # 72% del ancho (derecha)
        self.sprite_2.bottom = 20    # Suelo
        self.lista_sprites.append(self.sprite_2)

        # Cargamos el sonido de la pantalla principal
        musica = os.path.join("assets", "musica_niveles", "musica_menu_inicial.mp3")
        self.musica_inicio = arcade.load_sound(musica)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        self.fondo.width = self.window.width
        self.fondo.height = self.window.height
        self.fondo.center_x = self.window.width / 2
        self.fondo.center_y = self.window.height / 2

        self.sprite_1.center_x = self.window.width * 0.17
        self.sprite_2.center_x = self.window.width * 0.72

        if not getattr(self.window, 'reproductor_menu', None) or not self.window.reproductor_menu.playing:
            self.window.reproductor_menu = arcade.play_sound(self.musica_inicio, volume=self.window.volumen, loop=True)

    def on_update(self, delta_time):
        # Si el error está activo, sumamos el tiempo para que desaparezca tras 3 segundos
        if self.mostrar_error:
            self.tiempo_error += delta_time
            if self.tiempo_error > 3.0:
                self.mostrar_error = False
                self.tiempo_error = 0.0

    def on_draw(self):
        self.clear()

        self.lista_sprites.draw()
        
        # Título centrado dinámicamente
        arcade.draw_text("Stella & Galaxy", self.window.width / 2, self.window.height * 0.75,
                         arcade.color.WHITE, font_size=50, anchor_x="center")

        # --- BOTÓN 1: INICIAR PARTIDA ---
        # Calculamos la posición central
        cx, cy = self.window.width / 2, self.window.height / 2
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy - 25, cy + 25, arcade.color.ARMY_GREEN)
        arcade.draw_text("INICIAR PARTIDA", cx, cy,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- BOTÓN 2: CONTINUAR PARTIDA ---
        # Lo ponemos un poco más abajo del centro
        cy_continuar = cy - 80
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy_continuar - 25, cy_continuar + 25, arcade.color.YELLOW_GREEN)
        arcade.draw_text("CONTINUAR PARTIDA", cx, cy_continuar,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- BOTÓN 3: AJUSTES ---
        # Lo ponemos un poco más abajo del centro
        cy_ajustes = cy_continuar - 80
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy_ajustes - 25, cy_ajustes + 25, arcade.color.SLATE_GRAY)
        arcade.draw_text("AJUSTES", cx, cy_ajustes,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- MENSAJE DE ERROR DINAMICO ---
        if self.mostrar_error:
            arcade.draw_text("No hay ninguna partida empezada todavía.", cx, cy_ajustes - 80,
                             arcade.color.LIGHT_RED_OCHRE, font_size=16, anchor_x="center", bold=True)

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2
        global ESTADOS_NIVELES, PARTIDA_ACTUAL
        
        # Clic en Iniciar
        if cx - 150 < x < cx + 150 and cy - 25 < y < cy + 25:
            # Reseteamos el progreso usando la variable global              
            ESTADOS_NIVELES[1] = "no_conseguido"
            for i in range(2, 6):
                ESTADOS_NIVELES[i] = "bloqueado"
            
            # Limpiamos cualquier error previo y entramos al mapa
            self.mostrar_error = False

            if getattr(self.window, 'reproductor_menu', None):
                arcade.stop_sound(self.window.reproductor_menu)
                self.window.reproductor_menu = None

            mapa = Mapa()
            self.window.show_view(mapa)

        # Clic en Continuar
        cy_continuar = cy - 80
        if cx - 150 < x < cx + 150 and cy_continuar - 25 < y < cy_continuar + 25:
            if os.path.exists(ARCHIVO_GUARDADO):
                self.window.show_view(SeleccionPartida())

            else:
                self.mostrar_error = True
                self.tiempo_error = 0.0

        # Clic en Ajustes
        cy_ajustes = cy_continuar - 80
        if cx - 150 < x < cx + 150 and cy_ajustes - 25 < y < cy_ajustes + 25:
            settings_view = SettingsView()
            self.window.show_view(settings_view)

# --- VISTA: AJUSTES ---
class SettingsView(arcade.View):
    def __init__(self):
        super().__init__()
        # Inicializamos el gestor de UI para el botón nuevo y los pop-ups
        self.manager = arcade.gui.UIManager()
        
        self.boton_borrar = arcade.gui.UIFlatButton(text="BORRAR PARTIDAS GUARDADAS", width=300)
        
        # Función a realizar al pulsar el botón de borrar
        @self.boton_borrar.event("on_click")
        def on_click_borrar(event):

            # Creamos un mensaje de seguridad inicial
            caja_alerta = arcade.gui.UIMessageBox(
                width=420,
                height=200,
                message_text="¿Seguro que quieres borrar TODAS las partidas?\nEsta acción es irreversible.",
                buttons=["Cancelar", "Borrar"]
            )
            
            @caja_alerta.event("on_action")
            def accion_borrar(action_event):
                if action_event.action == "Borrar":

                    if os.path.exists(ARCHIVO_GUARDADO):
                        os.remove(ARCHIVO_GUARDADO)
                    
                    # Reiniciamos las variables de progreso en la memoria del juego
                    global ESTADOS_NIVELES, PARTIDA_ACTUAL
                    ESTADOS_NIVELES.update({
                        1: "no_conseguido",
                        2: "bloqueado",
                        3: "bloqueado",
                        4: "bloqueado",
                        5: "bloqueado"
                    })
                    PARTIDA_ACTUAL = None
                    
                    caja_confirmacion = arcade.gui.UIMessageBox(
                        width=350,
                        height=150,
                        message_text="¡Las partidas han sido borradas!",
                        buttons=["Aceptar"]
                    )
                    self.manager.add(caja_confirmacion)

            self.manager.add(caja_alerta)
        
        self.anclaje = arcade.gui.UIAnchorLayout()
        self.anclaje.add(
            child=self.boton_borrar,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-150
        )
        self.manager.add(self.anclaje)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

    def on_draw(self):
        self.clear()
        cx, cy = self.window.width / 2, self.window.height / 2
        
        arcade.draw_text("AJUSTES DE SONIDO", cx, self.window.height * 0.75,
                         arcade.color.WHITE, font_size = 35, anchor_x="center")
        
        # Muestra el volumen actual
        vol_porcentaje = int(self.window.volumen * 100)
        arcade.draw_text(f"VOLUMEN: {vol_porcentaje}%", cx, cy + 100,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

        # Botón Menos (-)
        arcade.draw_lrbt_rectangle_filled(cx - 120, cx - 40, cy + 20, cy + 60, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("-", cx - 80, cy + 40, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Más (+)
        arcade.draw_lrbt_rectangle_filled(cx + 40, cx + 120, cy + 20, cy + 60, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("+", cx + 80, cy + 40, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        arcade.draw_text("BORRADO DE PARTIDAS", cx, self.window.height * 0.4,
                         arcade.color.WHITE, font_size = 35, anchor_x="center")

        # Botón Volver
        y_volver = self.window.height * 0.15
        arcade.draw_lrbt_rectangle_outline(cx - 60, cx + 60, y_volver - 20, y_volver + 20, arcade.color.WHITE, border_width=2)
        arcade.draw_text("VOLVER", cx, y_volver, arcade.color.WHITE, font_size=15, anchor_x="center", anchor_y="center")

        self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2

        # Clic en MENOS (-)
        if cx - 120 < x < cx - 40 and cy + 20 < y < cy + 60:
            self.window.volumen = max(0.0, self.window.volumen - 0.1)
            if getattr(self.window, 'reproductor_menu', None):
                self.window.reproductor_menu.volume = self.window.volumen

        # Clic en MÁS (+)
        elif cx + 40 < x < cx + 120 and cy + 20 < y < cy + 60:
            self.window.volumen = min(1.0, self.window.volumen + 0.1)
            if getattr(self.window, 'reproductor_menu', None):
                self.window.reproductor_menu.volume = self.window.volumen

        # Clic en VOLVER
        y_volver = self.window.height * 0.15
        if cx - 60 < x < cx + 60 and y_volver - 20 < y < y_volver + 20:
            self.window.show_view(MenuView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())

    def on_hide_view(self):
        self.manager.disable()

class VistaNivelEnMapa:
    """
    Vista del logo de cada nivel en el mapa, en el que cada nivel puede ser no conseguido, conseguido o bloqueado"""

    def __init__(self, nivel, x, y, conexiones):
        self.nivel = nivel  # Número o identificador del nivel
        self.x = x  # Coordenada x del logo del nivel
        self.y = y  # Coordenada y del logo del nivel
        self.conexiones = conexiones  # Conexiones con otros niveles (lista con los niveles)
        self.radio_logo = 40  # Radio para hacer click en el nivel

        self.sprite_bloqueado = arcade.Sprite(os.path.join("assets", "imgs_niveles_en_mapa", "candado_cerrado.png"), scale=0.2)
        self.sprite_accesible = arcade.Sprite(os.path.join("assets", "imgs_niveles_en_mapa", "candado_abierto.png"), scale=0.3)
        self.sprite_completado = arcade.Sprite(os.path.join("assets", "imgs_niveles_en_mapa", "gema.png"), scale=0.15)

        for s in [self.sprite_bloqueado, self.sprite_accesible, self.sprite_completado]:
            s.center_x = self.x
            s.center_y = self.y

class Mapa(arcade.View):
    """
    Vista en la que se muestran los distintos niveles del juego.
    """
    def __init__(self):
        super().__init__()

        # Obtenemos el ancho y alto de la ventana dinámicamente
        aw = arcade.get_window().width
        ah = arcade.get_window().height

        self.niveles = {
           1: VistaNivelEnMapa(nivel=1, x=aw * 0.20, y=ah * 0.55, conexiones=[2]),
           2: VistaNivelEnMapa(nivel=2, x=aw * 0.35, y=ah * 0.40, conexiones=[1, 3]),
           3: VistaNivelEnMapa(nivel=3, x=aw * 0.50, y=ah * 0.55, conexiones=[2, 4]),
           4: VistaNivelEnMapa(nivel=4, x=aw * 0.65, y=ah * 0.40, conexiones=[3, 5]),
           5: VistaNivelEnMapa(nivel=5, x=aw * 0.80, y=ah * 0.55, conexiones=[4])
        }

        self.fondo = arcade.Sprite(os.path.join("assets", "imgs_niveles_en_mapa", "fondo.png"), scale = 0.9)
        
        self.fondo.center_x = self.window.width / 2
        self.fondo.center_y = self.window.height / 2

        self.lista_sprites = arcade.SpriteList()

        # Cargamos el sonido de la pantalla del mapa de niveles
        musica = os.path.join("assets", "musica_niveles", "musica_mapa_niveles.mp3")
        self.musica_mapa = arcade.load_sound(musica)

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.contenedor_botones = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        # Creamos un botón de ayuda
        self.img_ayuda = arcade.load_texture(os.path.join("assets", "imgs_niveles_en_mapa", "ayuda.png"))
        self.boton_ayuda = arcade.gui.UITextureButton(
            texture=self.img_ayuda,
            texture_hovered=self.img_ayuda,
            texture_pressed=self.img_ayuda,
            scale=0.08
        )

        # Creamos un botón para guardar la partida
        self.img_guardado = arcade.load_texture(os.path.join("assets", "imgs_niveles_en_mapa", "guardado.png"))
        self.boton_guardado = arcade.gui.UITextureButton(
            texture=self.img_guardado,
            texture_hovered=self.img_guardado,
            texture_pressed=self.img_guardado,
            scale=0.15
        )

        self.contenedor_botones.add(self.boton_ayuda)
        self.contenedor_botones.add(self.boton_guardado)

        # Lo ponemos en la esquina superior derecha
        self.ancho = arcade.gui.UIAnchorLayout()
        self.ancho.add(
            child = self.contenedor_botones,
            anchor_x = "right",
            anchor_y = "top",
            align_x = -20,
            align_y = -20
        )
        self.manager.add(self.ancho)

        # Asignamos la función del botón cuando se hace click
        @self.boton_guardado.event("on_click")
        def guardar(event):
            guardar_partida()
            
            mensaje_guardado = (
                "¡PARTIDA GUARDADA!\n\n"
                "Tu progreso actual se ha guardado\n"
                "correctamente. Podrás continuar\n"
                "desde aquí la próxima vez."
            )
            
            caja_guardado = arcade.gui.UIMessageBox(
                width=350,
                height=200,
                message_text=mensaje_guardado,
                buttons=["Aceptar"]
            )
            self.manager.add(caja_guardado)

        # Asignamos la función del botón de ayuda cuando se hace click
        @self.boton_ayuda.event("on_click")
        def mostrar_ayuda(event):
            mensaje_controles = (
                "TIPO DE NIVEL:\n\n"
                "    - Niveles accesibles: Candado abierto\n"
                "    - Niveles bloqueados: Candado cerrado\n"
                "    - Niveles conseguidos: Gema\n\n"
                "CONTROLES DEL JUEGO:\n\n"
                "🔥 Stella (Rojo):\n"
                "    - Moverse: A (izquierda) / D (derecha)\n"
                "    - Saltar: W (arriba)\n\n"
                "💧 Galaxy (Azul):\n"
                "    - Moverse: Flecha izquierda / Flecha derecha\n"
                "    - Saltar: Flecha arriba\n\n"
                "OBJETIVO DEL JUEGO:\n\n"
                "Ambos deben llegar a sus respectivas puertas para\n"
                "completar los niveles. Si alguno de los personajes\n"
                "toca el veneno, otro personaje, obstáculos o su\n"
                "elemento opuesto, ¡la partida terminará para los dos!\n"
            )
            
            # Generamos el desplegable nativo de Arcade
            caja_mensaje = arcade.gui.UIMessageBox(
                width=450,
                height=525,
                message_text=mensaje_controles,
                buttons=["Cerrar"]
            )
            self.manager.add(caja_mensaje)

    def actualizar_iconos(self):
        """Carga en el SpriteList solo los iconos que correspondan al estado actual"""
        self.lista_sprites.clear()

        self.lista_sprites.append(self.fondo)
        
        for nivel in self.niveles.values():
            estado = ESTADOS_NIVELES[nivel.nivel]
            if estado == "bloqueado":
                self.lista_sprites.append(nivel.sprite_bloqueado)
            elif estado == "conseguido":
                self.lista_sprites.append(nivel.sprite_completado)
            else:
                self.lista_sprites.append(nivel.sprite_accesible)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BROWN_NOSE)
        
        self.actualizar_iconos()

        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        # Dibujar las conexiones entre los niveles
        for nivel in self.niveles.values():
            for conexion in nivel.conexiones:
                if conexion in self.niveles:
                    destino = self.niveles[conexion]

                    if ESTADOS_NIVELES[nivel.nivel] != "bloqueado" and ESTADOS_NIVELES[destino.nivel] != "bloqueado":
                        color_conexion = arcade.color.GOLD
                    else:
                        color_conexion = arcade.color.DARK_BROWN

                    arcade.draw_line(nivel.x, nivel.y, destino.x, destino.y, color_conexion, 3)

        self.lista_sprites.draw()   # Dibujamos los iconos de los niveles

        self.manager.draw() # Se muestra el botón de guardado

        arcade.draw_text("Niveles completados: " + str(sum(1 for estado in ESTADOS_NIVELES.values() if estado == "conseguido")), self.window.width / 8, 60, 
                         arcade.color.WHITE, font_size = 20, font_name = "Impact", anchor_x = "center")

        arcade.draw_text("Presiona ESC para volver al menú", self.window.width / 1.2, 60,
                         arcade.color.WHITE, font_size=20, font_name = "Impact", anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for nivel in self.niveles.values():
                distancia = math.dist((x, y), (nivel.x, nivel.y))

                if distancia <= nivel.radio_logo:
                    if ESTADOS_NIVELES[nivel.nivel] == "no_conseguido":
                        print(f"¡Cargando el nivel {nivel.nivel}!")
                        if nivel.nivel in CLASES_NIVELES: 
                            if not HISTORIA_VISTA[nivel.nivel]:
                                self.window.show_view(VistaHistoria(nivel.nivel))
                            else:
                                self.window.show_view(CLASES_NIVELES[nivel.nivel]())
                
                    else:
                        print(f"El nivel {nivel.nivel} aún está bloqueado.")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_hide_view(self):
        # Paramos la música antes de pasar a la siguiente vista que se muestra
        arcade.stop_sound(self.musica_actual)

        self.manager.disable()  # Se deshabilita para que no intervenga en otras vistas

# Vista que se muestra con la historia de cada nivel
class VistaHistoria(arcade.View):
    def __init__(self, numero_nivel):
        super().__init__()
        self.numero_nivel = numero_nivel
        self.manager = arcade.gui.UIManager()

        self.tam_caja = min(800, arcade.get_window().height * 0.85)
        self.escala_extra = self.tam_caja / 800.0

        try:
            if (numero_nivel == 1):
                todos_los_mapas = [
                    os.path.join("primer capitulo", f)
                    for f in os.listdir("primer capitulo")
                    if f.endswith(".tmx")
                ]
            elif (numero_nivel >= 2 and numero_nivel <= 5):
                todos_los_mapas = [
                    os.path.join("cap_de2a4", f)
                    for f in os.listdir("cap_de2a4")
                    if f.endswith(".tmx")
                ]
            # Ordenamos por nombre numérico
            todos_los_mapas.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
        except:
            todos_los_mapas = []

        if numero_nivel == 1:
            self.mapas = todos_los_mapas     # Para el Nivel 1
        elif numero_nivel == 2:
            self.mapas = todos_los_mapas[:3]     # Para el Nivel 2
        elif numero_nivel == 3:
            self.mapas = todos_los_mapas[3:4]    # Para el Nivel 3
        elif numero_nivel == 4:
            self.mapas = todos_los_mapas[4:6]    # Para el Nivel 4
        elif numero_nivel == 5:
            self.mapas = todos_los_mapas[6:9]     # Para el Nivel 5
        else:
            self.mapas = []

        self.indice = 0
        self.camara = arcade.Camera2D()
        self.scene = None

        if self.mapas:
            self.cargar_mapa()

        # Boton siguiente
        self.boton_siguiente = arcade.load_texture(os.path.join("assets", "siguiente.png"))
        self.boton_siguiente = arcade.gui.UITextureButton(
            texture=self.boton_siguiente,
            texture_hovered=self.boton_siguiente,
            texture_pressed=self.boton_siguiente,
            scale=0.13
        )

        @self.boton_siguiente.event("on_click")
        def on_click_siguiente(event):
            self.indice += 1
            if self.indice < len(self.mapas):
                self.cargar_mapa()
            else:
                # Fin de la historia: Marcamos como vista e iniciamos el nivel real
                HISTORIA_VISTA[self.numero_nivel] = True
                self.window.show_view(CLASES_NIVELES[self.numero_nivel]())

        # Lo ponemos en la esquina inferior derecha
        self.anclaje = arcade.gui.UIAnchorLayout()
        self.anclaje.add(
            child=self.boton_siguiente,
            anchor_x="center_x",
            anchor_y="center_y",
            align_x=(self.tam_caja / 2) - 60,
            align_y=-(self.tam_caja / 2) + 60
        )
        self.manager.add(self.anclaje)

    def cargar_mapa(self):
        try:
            tile_map = arcade.load_tilemap(self.mapas[self.indice])
            self.scene = arcade.Scene.from_tilemap(tile_map)

            ancho = tile_map.width * tile_map.tile_width
            alto = tile_map.height * tile_map.tile_height

            self.camara.position = (ancho / 2, alto / 2)
            self.camara.zoom = 0.35 * self.escala_extra
        except Exception as e:
            print(f"Error cargando mapa de historia: {e}")
            self.scene = None

    def on_show_view(self):
        self.manager.enable()

        if not self.mapas:
            HISTORIA_VISTA[self.numero_nivel] = True
            self.window.show_view(CLASES_NIVELES[self.numero_nivel]())

    def on_draw(self):
        self.clear()
        
        # Color de fondo de la ventana entera
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # Dibujamos el recuadro negro centrado de 800x800 para el cómic
        cx, cy = self.window.width / 2, self.window.height / 2
        recuadro_panel = arcade.rect.LBWH(cx - self.tam_caja/2, cy - self.tam_caja/2, self.tam_caja, self.tam_caja)
        arcade.draw_rect_filled(recuadro_panel, arcade.color.BLACK)
        arcade.draw_rect_outline(recuadro_panel, arcade.color.WHITE, border_width=4)

        # Dibujamos la escena de Tiled con su cámara configurada
        if self.scene:
            with self.camara.activate():
                self.scene.draw()
        
        # Volvemos a la cámara principal para dibujar los botones por encima
        self.window.use()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

class VistaHistoriaFinal(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        self.tam_caja = min(800, arcade.get_window().height * 0.85)
        self.escala_extra = self.tam_caja / 800.0

        try:
            todos_los_mapas = [
                os.path.join("cap_de2a4", f)
                for f in os.listdir("cap_de2a4")
                if f.endswith(".tmx")
            ]
            todos_los_mapas.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

            self.mapas = todos_los_mapas[9:13]     # Mapas de la historia final
        except:
            self.mapas = []

        self.indice = 0
        self.camara = arcade.Camera2D()
        self.scene = None

        if self.mapas:
            self.cargar_mapa()

        self.boton_siguiente = arcade.load_texture(os.path.join("assets", "siguiente.png"))
        self.boton_siguiente = arcade.gui.UITextureButton(
            texture=self.boton_siguiente,
            texture_hovered=self.boton_siguiente,
            texture_pressed=self.boton_siguiente,
            scale=0.13
        )

        @self.boton_siguiente.event("on_click")
        def on_click_siguiente(event):
            self.indice += 1
            if self.indice < len(self.mapas):
                self.cargar_mapa()
            else:
                self.window.show_view(Victoria_Fin_Juego())

        # Lo ponemos en la esquina inferior derecha
        self.anclaje = arcade.gui.UIAnchorLayout()
        self.anclaje.add(
            child=self.boton_siguiente,
            anchor_x="center_x",
            anchor_y="center_y",
            align_x=(self.tam_caja / 2) - 60,
            align_y=-(self.tam_caja / 2) + 60
        )
        self.manager.add(self.anclaje)

    def cargar_mapa(self):
        try:
            tile_map = arcade.load_tilemap(self.mapas[self.indice])
            self.scene = arcade.Scene.from_tilemap(tile_map)
            ancho = tile_map.width * tile_map.tile_width
            alto = tile_map.height * tile_map.tile_height
            self.camara.position = (ancho / 2, alto / 2)
            self.camara.zoom = 0.35 * self.escala_extra
        except Exception as e:
            print(f"Error cargando mapa de historia final: {e}")
            self.scene = None

    def on_show_view(self):
        self.manager.enable()
        if not self.mapas:
            self.window.show_view(Victoria_Fin_Juego())

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        cx, cy = self.window.width / 2, self.window.height / 2
        recuadro_panel = arcade.rect.LBWH(cx - self.tam_caja/2, cy - self.tam_caja/2, self.tam_caja, self.tam_caja)
        arcade.draw_rect_filled(recuadro_panel, arcade.color.BLACK)
        arcade.draw_rect_outline(recuadro_panel, arcade.color.WHITE, border_width=4)

        if self.scene:
            with self.camara.activate():
                self.scene.draw()
        
        self.window.use()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

# Vista final que va a mostrar que se ha completado todo el juego y cerrará el programa cuando se pulse una tecla
class Victoria_Fin_Juego(arcade.View):
    def __init__(self):
        super().__init__()

        # Variables de control del scroll
        self.scroll_y = 0
        self.velocidad_scroll = 0.75
        self.scroll_maximo = 2500  # Distancia total que recorrerá la pantalla
        self.tiempo_juego = 0  

        self.lista_corona = arcade.SpriteList()  
        self.lista_sprites = arcade.SpriteList()  

        self.corona = arcade.Sprite(os.path.join("assets", "corona.png"), scale=1)
        self.stella = arcade.Sprite(os.path.join("chica.png"), scale=0.9)
        self.galaxy = arcade.Sprite(os.path.join("chico.png"), scale=0.9)

        self.lista_corona.append(self.corona)
        self.lista_sprites.append(self.stella)
        self.lista_sprites.append(self.galaxy)

        musica_final = os.path.join("assets", "musica_niveles", "musica_final.mp3")
        self.musica_final = arcade.load_sound(musica_final)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        if getattr(self, 'musica_final', None):
            self.reproductor_final = arcade.play_sound(self.musica_final, volume=self.window.volumen, loop=True)

    def on_update(self, delta_time):
        self.tiempo_juego += delta_time
        
        # Aumentamos el scroll hasta que alcance el plano final
        if self.scroll_y < self.scroll_maximo:
            self.scroll_y += self.velocidad_scroll

    def on_draw(self):
        self.clear()

        cx = self.window.width / 2
        cy = self.window.height / 2

        # Dibujamos la corona
        self.corona.center_x = cx
        self.corona.center_y = cy + self.scroll_y
        self.lista_corona.draw()

        # Mensaje de felicitación
        y_felicitacion = cy - 1000 + self.scroll_y
        arcade.draw_text("¡ENHORABUENA!", cx, y_felicitacion, arcade.color.GOLD, font_size=45, anchor_x="center", font_name="Impact")
        arcade.draw_text("Habéis superado todos los peligros y habéis completado el juego.", cx, y_felicitacion - 130, arcade.color.WHITE, font_size=28, anchor_x="center")

        # Créditos de los desarrolladores
        y_creadores = cy - 1600 + self.scroll_y
        arcade.draw_text("DESARROLLADO POR:", cx, y_creadores, arcade.color.YELLOW_GREEN, font_size=45, anchor_x="center", font_name="Impact")
        arcade.draw_text("Jefe de proyecto: Daniel Luque Villa", cx, y_creadores - 70, arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("  Integrantes del equipo: \n      Minia Cortés Zahonero \n      Rodrigo Calvo Ablanque \n      Adrián Fernández García", cx, y_creadores - 140, arcade.color.LIGHT_GRAY, font_size=20, width=400, anchor_x="center", multiline=True)

        # Plano final
        y_final = cy - 2500 + self.scroll_y
        # Dibujamos a Stella y Galaxy a los lados
        if self.stella and self.galaxy:
            self.stella.center_x = cx - 250
            self.stella.center_y = y_final - 40
            
            self.galaxy.center_x = cx + 250
            self.galaxy.center_y = y_final - 40

            self.lista_sprites.draw()

        arcade.draw_text("¡GRACIAS POR JUGAR!", cx, y_final + 250, arcade.color.GOLD, font_size=40, anchor_x="center", font_name="Impact")

        # Efecto de parpadeo para salir
        if self.scroll_y >= self.scroll_maximo:
            if int(self.tiempo_juego * 2) % 2 == 0:
                arcade.draw_text("Presiona ENTER para salir del juego", cx, y_final - 320, arcade.color.GRAY, font_size=18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        # Salimos del juego al pulsar ENTER cuando termine el scroll
        if key == arcade.key.ENTER and self.scroll_y >= self.scroll_maximo:
            arcade.exit()

    def on_hide_view(self):
        # Paramos la música final al salir de la vista
        if getattr(self, 'reproductor_final', None):
            arcade.stop_sound(self.reproductor_final)
    
class VistaFinNivel(arcade.View):
    def __init__(self, nivel, mensaje, color):
        super().__init__()
        self.nivel = nivel
        self.mensaje = mensaje
        self.color = color

        self.manager = arcade.gui.UIManager()

    def on_show_view(self): 
        self.manager.enable()
        arcade.set_background_color(arcade.color.BLACK)

        # Creamos una caja vertical para organizar los botones
        self.h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=20)

        # --- BOTÓN PRINCIPAL (Siguiente o Reiniciar) ---
        texto_boton_1 = "Siguiente nivel (ENTER)" if self.color == arcade.color.GREEN else "Reiniciar nivel (ENTER)"
        boton_accion = arcade.gui.UIFlatButton(text=texto_boton_1, width=250)
        self.h_box.add(boton_accion)

        # --- BOTÓN VOLVER AL MAPA ---
        boton_mapa = arcade.gui.UIFlatButton(text="Volver al mapa", width=250)
        self.h_box.add(boton_mapa)

        # Asignar funciones a los clics
        @boton_accion.event("on_click")
        def on_click_accion(event):
            if self.color == arcade.color.GREEN:

                # Si hemos ganado el Nivel 5, vamos a la Historia Final
                if self.nivel == 5:
                    self.window.show_view(VistaHistoriaFinal())
                else:
                    # Se desbloquea el siguiente nivel
                    siguiente = self.nivel + 1
                    if siguiente in CLASES_NIVELES:
                        if not HISTORIA_VISTA[siguiente]:
                            self.window.show_view(VistaHistoria(siguiente))
                        else:
                            self.window.show_view(CLASES_NIVELES[siguiente]())
                    else:
                        # Si no hay más niveles, volvemos al mapa
                        self.window.show_view(Mapa())
            else:
                # Reiniciar el mismo nivel
                self.window.show_view(CLASES_NIVELES[self.nivel]())

        @boton_mapa.event("on_click")
        def on_click_mapa(event):
            if self.nivel == 5 and self.color == arcade.color.GREEN:
                self.window.show_view(VistaHistoriaFinal())
            else:
                self.window.show_view(Mapa())

        # Centrar la caja en la pantalla
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(
            child=self.h_box,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=-100  # Ajuste vertical para que quede un poco más abajo del centro
        )
        self.manager.add(anchor)
    
    def on_hide_view(self):
        # Es vital deshabilitar el manager al cambiar de vista
        self.manager.disable()

    def on_draw(self):
        self.clear()

        # Mensaje de victoria
        arcade.draw_text(
            self.mensaje, self.window.width / 2, self.window.height / 2 + 50, self.color, font_size=40, anchor_x="center")
        
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        # Permitir reiniciar el nivel o pasar al siguiente con la tecla ENTER
        if key == arcade.key.ENTER:
            if self.color == arcade.color.GREEN:

                # Si hemos ganado el Nivel 5, vamos a la Historia Final
                if self.nivel == 5:
                    self.window.show_view(VistaHistoriaFinal())
                else:
                    # Pasar al siguiente nivel
                    siguiente = self.nivel + 1
                    if siguiente in CLASES_NIVELES:
                        if not HISTORIA_VISTA[siguiente]:
                            self.window.show_view(VistaHistoria(siguiente))
                        else:
                            self.window.show_view(CLASES_NIVELES[siguiente]())
                    else:
                        self.window.show_view(Mapa())
            else:
                # Reiniciar el mismo nivel
                self.window.show_view(CLASES_NIVELES[self.nivel]())

class NivelPerdido(VistaFinNivel):
    """
    Vista que se muestra al perder un nivel, con un mensaje de derrota y posibilidad de reiniciar el nivel o ir al mapa.
    """
    def __init__(self, nivel):
        super().__init__(nivel, "No ha conseguido superar el nivel", arcade.color.RED)

class NivelConseguido(VistaFinNivel):
    """
    Vista que se muestra al conseguir un nivel, con un mensaje de victoria y posibilidad de pasar al siguiente nivel o ir al mapa.
    """
    def __init__(self, nivel):
        super().__init__(nivel, "¡Nivel conseguido!", arcade.color.GREEN)
        # Al conseguir el nivel, actualizamos su estado a conseguido
        ESTADOS_NIVELES[nivel] = "conseguido"

        # Si el siguiente nivel está bloqueado,  lo desbloqueamos
        siguiente = nivel + 1
        if siguiente in ESTADOS_NIVELES and ESTADOS_NIVELES[siguiente] == "bloqueado":
            ESTADOS_NIVELES[siguiente] = "no_conseguido"

# ------------------ CLASE ABSTRACTA ------------------
class Personaje(arcade.Sprite, ABC):

    def __init__(self, scale=1):
        super().__init__()

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

# ------------------ PERSONAJES ------------------
class Stella(Personaje):
    def es_seguro(self, tipo):
        return tipo == LAVA

class Galaxy(Personaje):
    def es_seguro(self, tipo):
        return tipo == AGUA

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

    def update(self, delta_time, plataformas_moviles=None):
        # Movemos la piraña
        self.center_x += self.change_x

        choque_con_muro = arcade.check_for_collision_with_list(self, self.muros)
        
        choque_con_plataforma = False
        if plataformas_moviles and len(plataformas_moviles) > 0:
            choque_con_plataforma = arcade.check_for_collision_with_list(self, plataformas_moviles)
        
        # Comprobamos si se ha chocado con alguna muro o plataforma móvil para cambiar de dirección
        if choque_con_muro or choque_con_plataforma:

            # Si choca, retrocedemos un paso
            self.center_x -= self.change_x
            # Y cambiamos la dirección
            self.change_x *= -1
    
            if self.change_x < 0:
                self.texture = self.textura_izq
            else:
                self.texture = self.textura_der


class Nivel(arcade.View):
    """
    Vista del nivel.
    """
    def __init__(self, numero_nivel):
        super().__init__()
        self.numero_nivel = numero_nivel

        self.ancho_logico = 800
        self.alto_logico = 800
        
        self.camera = arcade.Camera2D()
        self.camera.position = (self.ancho_logico / 2, self.alto_logico / 2)
        
        self.scene = None
        self.stella = None
        self.galaxy = None
        self.physics_engine_stella = None
        self.physics_engine_galaxy = None
        self.victoria = False

    def on_show_view(self): 
        arcade.set_background_color(arcade.color.BLACK)

        escala_pantalla = self.window.height / self.alto_logico
        self.camera.zoom = escala_pantalla

        self.setup()

    # ---------------- CONTROLES ----------------
    def on_key_press(self, key, modifiers):
        # Stella (flechas)
        if key == arcade.key.A:
            self.stella.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.stella.change_x = PLAYER_SPEED
        elif key == arcade.key.W:
            self.stella.saltar()

        # Galaxy (WASD)
        if key == arcade.key.LEFT:
            self.galaxy.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.galaxy.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.galaxy.saltar()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.A, arcade.key.D]:
            self.stella.change_x = 0

        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.galaxy.change_x = 0

class Nivel1(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=1)
        
        # Cargamos el sonido de la vista del nivel 1
        musica = os.path.join("assets", "musica_niveles", "musica_nivel_4.mp3")
        self.musica_mapa = arcade.load_sound(musica)

    def setup(self):
        self.victoria = False

        mapa = os.path.join("Nivel prueba", "sin nombre.tmx")

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
            mapa_temp = arcade.load_tilemap(mapa)
            alto_real_mapa = mapa_temp.height * mapa_temp.tile_height
            escala_auto = self.alto_logico / alto_real_mapa
            
            # 2. Cargamos el mapa con esa escala
            tile_map = arcade.load_tilemap(mapa, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
            print("Mapa cargado con éxito.")
        except Exception as e:
            print(f"Error cargando el archivo TMX: {e}")
            self.scene = None
            return

        # Personajes
        self.stella = Stella()
        self.stella.texture = arcade.load_texture("chica.png")
        self.stella.scale = 0.1
        self.stella.center_x = 100
        self.stella.center_y = 200
        self.scene.add_sprite("Stella", self.stella)

        self.galaxy = Galaxy()
        self.galaxy.texture = arcade.load_texture("chico.png")
        self.galaxy.scale = 0.1
        self.galaxy.center_x = 150
        self.galaxy.center_y = 100
        self.scene.add_sprite("Galaxy", self.galaxy)

        # Motores de física
        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        # Física
        self.stella.physics_engine = arcade.PhysicsEnginePlatformer(
            self.stella, gravity_constant = GRAVITY, walls = muros
        )

        self.galaxy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.galaxy, gravity_constant = GRAVITY, walls = muros
        )

    def on_show_view(self):
        
        super().on_show_view()  # Esto se asegura de configurar el fondo y llamar a setup()
        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        # Activamos la camara
        with self.camera.activate():
            # Dibujamos un fondo cuadrado para el nivel (el cielo)
            fondo = arcade.rect.LBWH(0, 0, self.ancho_logico, self.alto_logico)
            arcade.draw_rect_filled(fondo, arcade.color.ONYX)

            if self.scene:

                self.scene.draw()
            else:
                arcade.draw_text("ERROR: TMX no encontrado", self.ancho_logico/2, self.alto_logico/2, 
                                 arcade.color.RED, 20, anchor_x="center")

    def on_update(self, delta_time):

        if not self.scene or not self.stella.physics_engine or not self.galaxy.physics_engine:
            return
        # Física
        self.stella.physics_engine.update()
        self.galaxy.physics_engine.update()

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.stella, self.galaxy):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return

        capas_muerte_stella = ["Capa de patrones 2", "Capa de patrones 5"]
        capas_muerte_galaxy = ["Capa de patrones 2", "Capa de patrones 4"]

        # Colisiones de muerte
        for jugador, capas in [(self.stella, capas_muerte_stella), (self.galaxy, capas_muerte_galaxy)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                except (KeyError, TypeError):
                    pass
        
        # Colisiones de victoria
        try:
            en_puerta_stella = arcade.check_for_collision_with_list(self.stella, self.scene["Capa de patrones 6"])
            en_puerta_galaxy = arcade.check_for_collision_with_list(self.galaxy, self.scene["Capa de patrones 7"])
            if en_puerta_stella and en_puerta_galaxy:
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except (KeyError, TypeError):
            pass

    def on_hide_view(self):
        arcade.stop_sound(self.musica_actual)

class Nivel2(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=2)

        self.objetos_que_caen = None
        self.tiempo_spawn = 0

        # Cargamos el sonido de la vista del nivel 2
        musica = os.path.join("assets", "musica_niveles", "musica_nivel_5.mp3")
        self.musica_mapa = arcade.load_sound(musica)

    def setup(self):
        self.victoria = False

        mapa = os.path.join("proyecto2", "nivel2real.tmx")

        layer_options = {
            "Capa de patrones 1": {"use_spatial_hash": True},
            "Capa de patrones 7": {"use_spatial_hash": True},
            "Capa de patrones 5": {"use_spatial_hash": True},
            "agua": {"use_spatial_hash": True},
            "Capa de patrones 3": {"use_spatial_hash": False},
            "Capa de patrones 2": {"use_spatial_hash": False},
            "Capa de patrones 4": {"use_spatial_hash": False},
        }

        try:
            mapa_temp = arcade.load_tilemap(mapa)
            alto_real_mapa = mapa_temp.height * mapa_temp.tile_height
            
            # Usamos nuestra medida lógica (800) para encajarlo perfectamente en la cámara
            if alto_real_mapa > 0:
                escala_auto = self.alto_logico / alto_real_mapa
            else:
                escala_auto = 1.0

            tile_map = arcade.load_tilemap(mapa, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
        except Exception as e:
            print(f"Error cargando TMX Nivel 2: {e}")
            self.scene = None
            return
        
        self.stella = Stella()
        self.stella.texture = arcade.load_texture("chica.png")
        self.stella.scale = 0.07 
        self.stella.center_x = 50
        self.stella.center_y = self.alto_logico - 50
        self.scene.add_sprite("Stella", self.stella)

        self.galaxy = Galaxy()
        self.galaxy.texture = arcade.load_texture("chico.png")
        self.galaxy.scale = 0.07  
        self.galaxy.center_x = self.ancho_logico - 50
        self.galaxy.center_y = 50 
        self.scene.add_sprite("Galaxy", self.galaxy)

        self.objetos_que_caen = arcade.SpriteList()
        self.tiempo_spawn = 0

        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        self.stella.physics_engine = arcade.PhysicsEnginePlatformer(
            self.stella, gravity_constant=GRAVITY, walls=muros
        )
        self.galaxy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.galaxy, gravity_constant=GRAVITY, walls=muros
        )

    def crear_objeto_que_cae(self):
        """Crea un coco que cae desde arriba"""
        ruta = os.path.join("proyecto2", "WhatsApp_Image_2026-05-07_at_00.13.20-removebg-preview.png")

        sprite = arcade.Sprite(ruta, 0.15)

        sprite.center_x = random.randint(0, self.ancho_logico)
        sprite.center_y = self.alto_logico + 50
        sprite.change_y = -5

        self.objetos_que_caen.append(sprite)

    def on_show_view(self):
        
        super().on_show_view()  # Esto se asegura de configurar el fondo y llamar a setup()
        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        # ACTIVAMOS LA CÁMARA
        with self.camera.activate():
            fondo = arcade.rect.LBWH(0, 0, self.ancho_logico, self.alto_logico)
            arcade.draw_rect_filled(fondo, arcade.color.SKY_BLUE)

            if self.scene:
                self.scene.draw()
            else:
                arcade.draw_text("ERROR: TMX no encontrado", self.ancho_logico/2, self.alto_logico/2, 
                                 arcade.color.RED, 20, anchor_x="center")

            # Dibujamos los cocos por encima del mapa
            if self.objetos_que_caen:
                self.objetos_que_caen.draw()

    def on_update(self, delta_time):
        if not self.scene or not self.stella.physics_engine or not self.galaxy.physics_engine:
            return
            
        self.stella.physics_engine.update()
        self.galaxy.physics_engine.update()

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.stella, self.galaxy):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return
        
        # --- LÓGICA DE COCOS ---
        self.objetos_que_caen.update()

        self.tiempo_spawn += delta_time
        if self.tiempo_spawn > 1.75:
            self.crear_objeto_que_cae()
            self.tiempo_spawn = 0

        # Colisiones de los cocos con los personajes
        for coco in self.objetos_que_caen:
            if arcade.check_for_collision(coco, self.stella) or arcade.check_for_collision(coco, self.galaxy):
                self.window.show_view(NivelPerdido(self.numero_nivel))
                return
            # Limpiar cocos que ya cayeron por debajo del mapa
            if coco.center_y < -100:
                coco.remove_from_sprite_lists()

        capas_muerte_stella = ["Capa de patrones 7", "agua"]
        capas_muerte_galaxy = ["Capa de patrones 7", "Capa de patrones 5"]

        # Colisiones de muerte por zonas peligrosas
        for jugador, capas in [(self.stella, capas_muerte_stella), (self.galaxy, capas_muerte_galaxy)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                except (KeyError, TypeError):
                    pass

        # Colisiones de victoria
        try:
            en_puerta_stella = arcade.check_for_collision_with_list(self.stella, self.scene["Capa de patrones 3"])
            en_puerta_galaxy = arcade.check_for_collision_with_list(self.galaxy, self.scene["Capa de patrones 2"])
            
            if en_puerta_stella and en_puerta_galaxy:
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except (KeyError, TypeError):
            pass

    def on_hide_view(self):
        arcade.stop_sound(self.musica_actual)

class Nivel3(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=3)

        # Cargamos el sonido de la vista del nivel 3
        musica = os.path.join("assets", "musica_niveles", "musica_nivel_6.mp3")
        self.musica_mapa = arcade.load_sound(musica)

        self.velocidad_plataformas = 2
        self.altura_minima = 0
        self.altura_maxima = 0
        self.estado_plataformas = "esperando_arriba"
        self.contador_pausa = 0
        self.tiempo_pausa = 2

    def setup(self):
        mapa = os.path.join("mapa_nivel_acuatico_zip", "nivel_acuatico.tmx")

        layer_options = {
            "capa_agua_solido": {"use_spatial_hash": True},
            "capa_veneno": {"use_spatial_hash": True},
            "capa_plataforma_movil": {"use_spatial_hash": True},
        }

        try:
            mapa_temp = arcade.load_tilemap(mapa)
            escala_auto = self.alto_logico / (mapa_temp.height * mapa_temp.tile_height)
            tile_map = arcade.load_tilemap(mapa, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
        except Exception as e:
            print(f"Error cargando TMX Nivel 3: {e}")
            self.scene = None
            return

        plataformas = arcade.SpriteList()
        if "capa_plataforma_movil" in self.scene:
            plataformas = self.scene["capa_plataforma_movil"]

        # Límites plataformas móviles
        if len(plataformas) > 0:
            self.altura_maxima = plataformas[0].bottom
            self.altura_minima = self.altura_maxima - 102

        # Jugadores
        self.stella = Stella()
        self.stella.texture = arcade.load_texture("chica.png")
        self.stella.scale = 0.08
        self.stella.center_x = 80
        self.stella.center_y = 100
        self.scene.add_sprite("Stella", self.stella)

        self.galaxy = Galaxy()
        self.galaxy.texture = arcade.load_texture("chico.png")
        self.galaxy.scale = 0.08
        self.galaxy.center_x = self.ancho_logico - 80
        self.galaxy.center_y = 100
        self.scene.add_sprite("Galaxy", self.galaxy)

        # Muros y Física
        muros = arcade.SpriteList()
        if "capa_agua_solido" in self.scene:
            muros = self.scene["capa_agua_solido"]

        self.stella.physics_engine = arcade.PhysicsEnginePlatformer(
            self.stella, walls=muros, platforms=plataformas, gravity_constant=GRAVITY
        )
        self.galaxy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.galaxy, walls=muros, platforms=plataformas, gravity_constant=GRAVITY
        )

        # Enemigos
        self.lista_enemigos = arcade.SpriteList()
        pirana1 = Piraña(x=450, y=250, muros=muros)
        pirana2 = Piraña(x=300, y=250, muros=muros)
        pirana3 = Piraña(x=400, y=500, muros=muros)
        
        self.lista_enemigos.append(pirana1)
        self.lista_enemigos.append(pirana2)
        self.lista_enemigos.append(pirana3)

    def on_show_view(self):
        super().on_show_view()  
        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            fondo = arcade.rect.LBWH(0, 0, self.ancho_logico, self.alto_logico)
            arcade.draw_rect_filled(fondo, arcade.color.OCEAN_BOAT_BLUE)
            
            if self.scene:
                self.scene.draw()
            self.lista_enemigos.draw()

    def on_update(self, delta_time):
        if not self.scene:
            return

        self.stella.physics_engine.update()
        self.galaxy.physics_engine.update()
        
        # Obtenemos la lista de plataformas móviles
        plataformas_actuales = arcade.SpriteList()
        if "capa_plataforma_movil" in self.scene:
            plataformas_actuales = self.scene["capa_plataforma_movil"]

        # Actualizamos el movimiento de las pirañas pasando la lista de plataformas móviles
        for piraña in self.lista_enemigos:
            piraña.update(delta_time, plataformas_moviles = plataformas_actuales)

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.stella, self.galaxy):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return
        
        # Colisiones con enemigos
        for pirana in self.lista_enemigos:
            if arcade.check_for_collision(pirana, self.stella) or arcade.check_for_collision(pirana, self.galaxy):
                self.window.show_view(NivelPerdido(self.numero_nivel))
                return
            
        # Plataformas Móviles
        plataformas_sprites = arcade.SpriteList()
        if "capa_plataforma_movil" in self.scene:
            plataformas_sprites = self.scene["capa_plataforma_movil"]
        if plataformas_sprites:
            if self.estado_plataformas == "esperando_arriba":

                self.contador_pausa += delta_time

                if self.contador_pausa >= self.tiempo_pausa:

                    self.contador_pausa = 0
                    self.estado_plataformas = "bajando"

            elif self.estado_plataformas == "bajando":

                for plataforma in plataformas_sprites:
                    plataforma.center_y -= self.velocidad_plataformas

                if (plataformas_sprites[0].bottom <= self.altura_minima):
                    self.estado_plataformas = "esperando_abajo"

            elif self.estado_plataformas == "esperando_abajo":

                self.contador_pausa += delta_time
                if self.contador_pausa >= self.tiempo_pausa:

                    self.contador_pausa = 0
                    self.estado_plataformas = "subiendo"

            elif self.estado_plataformas == "subiendo":

                for plataforma in plataformas_sprites:
                    plataforma.center_y += self.velocidad_plataformas

                if (plataformas_sprites[0].bottom >= self.altura_maxima):
                    self.estado_plataformas = "esperando_arriba"

        # Colisiones de muerte por zonas peligrosas
        capas_muerte_stella = ["capa_agua_estela", "capa_veneno"]
        capas_muerte_galaxy = ["capa_fuego_galaxi", "capa_veneno"]

        for jugador, capas in [(self.stella, capas_muerte_stella), (self.galaxy, capas_muerte_galaxy)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                except (KeyError, TypeError): pass

        # Victoria
        try:
            en_puerta_stella = arcade.check_for_collision_with_list(self.stella, self.scene["puerta_chica_acuatico"])
            en_puerta_galaxy = arcade.check_for_collision_with_list(self.galaxy, self.scene["puerta_chico_acuatico"])
            if en_puerta_stella and en_puerta_galaxy:
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except (KeyError, TypeError): 
            pass

    def on_hide_view(self):
        arcade.stop_sound(self.musica_actual)

class Nivel4(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=4)

        # Cargamos el sonido de la vista del nivel 4
        musica = os.path.join("assets", "musica_niveles", "musica_nivel_2.mp3")
        self.musica_mapa = arcade.load_sound(musica)

        self.victoria = False
        self.tiempo_restante = 30.0
        self.contador_monedas = 0
        self.total_monedas = 12

    def setup(self):
        self.victoria = False
        self.tiempo_restante = 30.0
        self.contador_monedas = 0

        mapa = os.path.join("nivel desierto", "desierto_mapa.tmj")

        layer_options = {
            "suelo": {"use_spatial_hash": True},
            "arena": {"use_spatial_hash": True},
            "plataformas": {"use_spatial_hash": True},
            "monedas": {"use_spatial_hash": True},
            "agua": {"use_spatial_hash": True},
            "lava": {"use_spatial_hash": True},
            "veneno": {"use_spatial_hash": True},
            "puerta_chico": {"use_spatial_hash": True},
            "puerta_chica": {"use_spatial_hash": True},
        }

        try:
            mapa_temp = arcade.load_tilemap(mapa)
            escala_auto = self.alto_logico / (mapa_temp.height * mapa_temp.tile_height)
            tile_map = arcade.load_tilemap(mapa, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
        except Exception as e:
            print(f"Error cargando TMX Nivel 4: {e}")
            self.scene = None
            return
        
        self.ancho_mapa_escalado = mapa_temp.width * mapa_temp.tile_width * escala_auto

        # Personajes
        self.stella = Stella()
        self.stella.texture = arcade.load_texture("chica.png")
        self.stella.scale = 0.07
        self.stella.center_x = self.ancho_mapa_escalado - 100
        self.stella.center_y = 400
        self.scene.add_sprite("Stella", self.stella)

        self.galaxy = Galaxy()
        self.galaxy.texture = arcade.load_texture("chico.png")
        self.galaxy.scale = 0.07
        self.galaxy.center_x = 100
        self.galaxy.center_y = 150
        self.scene.add_sprite("Galaxy", self.galaxy)

        # Muros y Física
        muros = arcade.SpriteList()
        for nombre in ["suelo", "arena", "plataformas"]:
            if nombre in self.scene:
                for sprite in self.scene[nombre]:
                    muros.append(sprite)

        self.stella.physics_engine = arcade.PhysicsEnginePlatformer(
            self.stella, gravity_constant=GRAVITY, walls=muros
        )
        self.galaxy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.galaxy, gravity_constant=GRAVITY, walls=muros
        )

    def on_show_view(self):
        super().on_show_view()  
        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            fondo = arcade.rect.LBWH(0, 0, getattr(self, 'ancho_mapa_escalado', self.ancho_logico), self.alto_logico)
            arcade.draw_rect_filled(fondo, arcade.color.SKY_BLUE)

            if self.scene:
                self.scene.draw()
        
        # Dibujamos los textos por encima pegados a la pantalla de la ventana
        arcade.draw_text(f"Monedas: {self.contador_monedas} / {self.total_monedas}", 
                         20, self.window.height - 40, arcade.color.GOLDENROD, 24, font_name="Impact")
        
        color_tiempo = arcade.color.RED if self.tiempo_restante <= 15 else arcade.color.WHITE
        arcade.draw_text(f"Tiempo: {int(self.tiempo_restante)}", 
                         20, self.window.height - 75, color_tiempo, 24, font_name="Impact")

    def on_update(self, delta_time):
        if not self.scene or self.victoria:
            return
        
        self.stella.physics_engine.update()
        self.galaxy.physics_engine.update()

        # Lógica de la cuenta atrás
        self.tiempo_restante -= delta_time
        if self.tiempo_restante <= 0:
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return
        
        # Límites de pantalla para no salirse del mapa
        for jugador in [self.stella, self.galaxy]:
            if jugador.left < 0:
                jugador.left = 0
            elif jugador.right > getattr(self, 'ancho_mapa_escalado', self.ancho_logico):
                jugador.right = getattr(self, 'ancho_mapa_escalado', self.ancho_logico)

        # Colisiones con monedas
        if "monedas" in self.scene:
            for jugador in [self.stella, self.galaxy]:
                monedas_tocadas = arcade.check_for_collision_with_list(jugador, self.scene["monedas"])
                for moneda in monedas_tocadas:
                    moneda.remove_from_sprite_lists()
                    self.contador_monedas += 1

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.stella, self.galaxy):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return
        
        # Colisiones de muerte por zonas peligrosas
        capas_muerte_stella = ["agua", "veneno"]
        capas_muerte_galaxy = ["lava", "veneno"]

        for jugador, capas in [(self.stella, capas_muerte_stella),
                               (self.galaxy, capas_muerte_galaxy)]:
            for nombre in capas:
                if nombre in self.scene:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                    
        # Victoria
        try:
            if "puerta_chica" in self.scene and "puerta_chico" in self.scene:
                en_puerta1 = arcade.check_for_collision_with_list(self.stella, self.scene["puerta_chica"])
                en_puerta2 = arcade.check_for_collision_with_list(self.galaxy, self.scene["puerta_chico"])
                
                # Se requiere llegar a las puertas Y tener todas las monedas
                if len(en_puerta1) and len(en_puerta2) and self.contador_monedas >= self.total_monedas:
                    self.victoria = True
                    self.window.show_view(NivelConseguido(self.numero_nivel))
        except:
            pass

    def on_hide_view(self):
        arcade.stop_sound(self.musica_actual)

class Nivel5(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=5)

        # Cargamos el sonido de la vista del nivel 5
        musica = os.path.join("assets", "musica_niveles", "musica_nivel_castillo.mp3")
        self.musica_mapa = arcade.load_sound(musica)

        self.palanca_activada = False
        self.victoria = False

    def setup(self):
        self.victoria = False
        self.palanca_activada = False

        mapa = os.path.join("Nivel_final", "nivel_final.tmx")

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

        try:
            mapa_temp = arcade.load_tilemap(mapa)
            escala_auto = self.alto_logico / (mapa_temp.height * mapa_temp.tile_height)
            tile_map = arcade.load_tilemap(mapa, scaling=escala_auto, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(tile_map)
        except Exception as e:
            print(f"Error cargando TMX Nivel 5: {e}")
            self.scene = None
            return

        # Guardar posiciones originales de muros
        for nombre in ["muro1", "muro2", "muro3"]:
            if nombre in self.scene:
                for muro in self.scene[nombre]:
                    muro.original_x = muro.center_x
                    muro.original_y = muro.center_y

        if "palancaactiva" in self.scene:
            for s in self.scene["palancaactiva"]: 
                s.visible = False

        # Personajes
        self.stella = Stella()
        self.stella.texture = arcade.load_texture("chica.png")
        self.stella.scale = 0.07
        self.stella.center_x = 150
        self.stella.center_y = 750
        self.scene.add_sprite("Stella", self.stella)

        self.galaxy = Galaxy()
        self.galaxy.texture = arcade.load_texture("chico.png")
        self.galaxy.scale = 0.07
        self.galaxy.center_x = 700
        self.galaxy.center_y = 750
        self.scene.add_sprite("Galaxy", self.galaxy)

        # Muros físicos
        muros = arcade.SpriteList()
        for nombre in ["Capa de patrones 1", "muro1", "muro2", "muro3"]:
            if nombre in self.scene:
                for sprite in self.scene[nombre]:
                    muros.append(sprite)

        self.stella.physics_engine = arcade.PhysicsEnginePlatformer(
            self.stella, gravity_constant=GRAVITY, walls=muros
        )
        self.galaxy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.galaxy, gravity_constant=GRAVITY, walls=muros
        )

    def on_show_view(self):
        super().on_show_view()  
        self.musica_actual = arcade.play_sound(self.musica_mapa, volume = self.window.volumen, loop = True)

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            fondo = arcade.rect.LBWH(0, 0, self.ancho_logico, self.alto_logico)
            arcade.draw_rect_filled(fondo, arcade.color.EERIE_BLACK)
            
            if self.scene:
                self.scene.draw()

    def on_update(self, delta_time):
        if self.victoria:
            return 
        
        self.stella.physics_engine.update()
        self.galaxy.physics_engine.update()

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.stella, self.galaxy):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return
        
        # Colisiones de muerte por zonas peligrosas
        capas_muerte_stella = ["veneno", "agua"]
        capas_muerte_galaxy = ["veneno", "lava"]

        for jugador, capas in [(self.stella, capas_muerte_stella),
                               (self.galaxy, capas_muerte_galaxy)]:
            for nombre in capas:
                if nombre in self.scene:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return

        # Botón 1
        try:
            tocando_boton1 = (
                arcade.check_for_collision_with_list(self.stella, self.scene["boton1"]) or
                arcade.check_for_collision_with_list(self.galaxy, self.scene["boton1"])
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

        # Botón 2
        try:
            tocando_boton2 = (
                arcade.check_for_collision_with_list(self.stella, self.scene["boton2"]) or
                arcade.check_for_collision_with_list(self.galaxy, self.scene["boton2"])
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

        # Palanca
        try:
            if not self.palanca_activada:
                tocando_palanca = (
                    arcade.check_for_collision_with_list(self.stella, self.scene["palanca"]) or
                    arcade.check_for_collision_with_list(self.galaxy, self.scene["palanca"])
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

        # Victoria
        try:
            en_puerta1 = arcade.check_for_collision_with_list(self.stella, self.scene["puertachica"])
            en_puerta2 = arcade.check_for_collision_with_list(self.galaxy, self.scene["puertachico"])
            if len(en_puerta1) and len(en_puerta2):
                self.victoria = True
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except:
            pass

    def on_hide_view(self):
        arcade.stop_sound(self.musica_actual)

CLASES_NIVELES = {
    1: Nivel1,
    2: Nivel2,
    3: Nivel3,
    4: Nivel4,
    5: Nivel5
}

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Juego", resizable=True)
    window.maximize()
    window.volumen = 0.5
    menu = MenuView()
    window.show_view(menu)
    arcade.run()