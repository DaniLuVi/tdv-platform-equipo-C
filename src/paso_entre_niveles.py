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
        arcade.draw_text("SELECCIONA UNA PARTIDA", self.window.width / 2, self.window.height * 0.85,
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
    def on_show_view(self):
        arcade.set_background_color(arcade.color.ORANGE_PEEL)

    def on_draw(self):
        self.clear()
        cx, cy = self.window.width / 2, self.window.height / 2
        
        arcade.draw_text("AJUSTES DE SONIDO", cx, self.window.height * 0.7,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        
        # Muestra el volumen actual
        vol_porcentaje = int(self.window.volumen * 100)
        arcade.draw_text(f"VOLUMEN: {vol_porcentaje}%", cx, cy + 50,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

        # Botón Menos (-)
        arcade.draw_lrbt_rectangle_filled(cx - 120, cx - 40, cy - 20, cy + 20, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("-", cx - 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Más (+)
        arcade.draw_lrbt_rectangle_filled(cx + 40, cx + 120, cy - 20, cy + 20, arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_text("+", cx + 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Volver
        arcade.draw_lrbt_rectangle_outline(cx - 60, cx + 60, 90, 130, arcade.color.WHITE, border_width=2)
        arcade.draw_text("VOLVER", cx, 110, arcade.color.WHITE, font_size=15, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2

        # Clic en MENOS (-)
        if cx - 120 < x < cx - 40 and cy - 20 < y < cy + 20:
            self.window.volumen = max(0.0, self.window.volumen - 0.1)
            if getattr(self.window, 'reproductor_menu', None):
                self.window.reproductor_menu.volume = self.window.volumen

        # Clic en MÁS (+)
        elif cx + 40 < x < cx + 120 and cy - 20 < y < cy + 20:
            self.window.volumen = min(1.0, self.window.volumen + 0.1)
            if getattr(self.window, 'reproductor_menu', None):
                self.window.reproductor_menu.volume = self.window.volumen

        # Clic en VOLVER
        elif cx - 60 < x < cx + 60 and 90 < y < 130:
            self.window.show_view(MenuView())

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

        self.niveles = {
           1: VistaNivelEnMapa(nivel=1, x=250, y=500, conexiones=[2]),
           2: VistaNivelEnMapa(nivel=2, x=500, y=350, conexiones=[1, 3]),
           3: VistaNivelEnMapa(nivel=3, x=750, y=500, conexiones=[2, 4]),
           4: VistaNivelEnMapa(nivel=4, x=1000, y=350, conexiones=[3, 5]),
           5: VistaNivelEnMapa(nivel=5, x=1250, y=500, conexiones=[4]),
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

        # Creamos un botón para guardar la partida
        self.img_guardado = arcade.load_texture(os.path.join("assets", "imgs_niveles_en_mapa", "guardado.png"))
        self.boton_guardado = arcade.gui.UITextureButton(
            texture=self.img_guardado,
            texture_hovered=self.img_guardado,
            texture_pressed=self.img_guardado,
            scale=0.15
        )

        # Lo ponemos en la esquina superior derecha
        self.ancho = arcade.gui.UIAnchorLayout()
        self.ancho.add(
            child = self.boton_guardado,
            anchor_x = "right",
            anchor_y = "top",
            align_x = -20,
            align_y = -20
        )
        self.manager.add(self.ancho)

        self.mostrar_mensaje_guardado = False
        self.tiempo = 0.0

        # Asignamos la función del botón cuando se hace click
        @self.boton_guardado.event("on_click")
        def guardar(event):
            guardar_partida()
            self.mostrar_mensaje_guardado = True
            self.tiempo = 0.0

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

        if self.mostrar_mensaje_guardado:
            arcade.draw_text("Partida guardada con éxito", 20, SCREEN_HEIGHT - 120,
                             arcade.color.GREEN, font_size = 16, font_name = "Impact")
        
    def on_update(self, delta_time):
        if self.mostrar_mensaje_guardado:
            self.tiempo += delta_time
            if self.tiempo > 3.0:  # Desaparece tras 3 segundos
                self.mostrar_mensaje_guardado = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for nivel in self.niveles.values():
                distancia = math.dist((x, y), (nivel.x, nivel.y))

                if distancia <= nivel.radio_logo:
                    if ESTADOS_NIVELES[nivel.nivel] != "bloqueado":
                        print(f"¡Cargando el nivel {nivel.nivel}!")
                        if nivel.nivel in CLASES_NIVELES: 
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

# Esta va a ser la vista final que va a mostrar que se ha completado todo el juego y cerrará el programa cuando se pulse una tecla
class Victoria_Fin_Juego(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
    
    #def on_show_view(self):

    
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
            if self.nivel == 10 and self.color == arcade.color.GOLD:
                # Si hemos ganado el nivel 10, vamos a la pantalla de créditos/final
                self.window.show_view(Victoria_Fin_Juego())
            elif self.color == arcade.color.GREEN:
                # Lógica: Desbloquear siguiente y abrirlo
                siguiente = self.nivel + 1
                if siguiente in CLASES_NIVELES:
                    self.window.show_view(CLASES_NIVELES[siguiente]())
                else:
                    # Si no hay más niveles, volvemos al mapa
                    self.window.show_view(Mapa())
            else:
                # Reiniciar el mismo nivel
                self.window.show_view(CLASES_NIVELES[self.nivel]())

        @boton_mapa.event("on_click")
        def on_click_mapa(event):
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
                # Pasar al siguiente nivel
                siguiente = self.nivel + 1
                if siguiente in CLASES_NIVELES:
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

        if nivel == 10:
            self.window.show_view(Victoria_Fin_Juego()) 
        else:
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
class Fireboy(Personaje):
    def es_seguro(self, tipo):
        return tipo == LAVA

class Watergirl(Personaje):
    def es_seguro(self, tipo):
        return tipo == AGUA

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
        self.fireboy = None
        self.watergirl = None
        self.physics_engine_fireboy = None
        self.physics_engine_watergirl = None
        self.victoria = False

    def on_show_view(self): 
        arcade.set_background_color(arcade.color.BLACK)
        self.setup()

    # ---------------- CONTROLES ----------------
    def on_key_press(self, key, modifiers):
        # Fireboy (flechas)
        if key == arcade.key.LEFT:
            self.fireboy.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.fireboy.change_x = PLAYER_SPEED
        elif key == arcade.key.UP:
            self.fireboy.saltar()

        # Watergirl (WASD)
        if key == arcade.key.A:
            self.watergirl.change_x = -PLAYER_SPEED
        elif key == arcade.key.D:
            self.watergirl.change_x = PLAYER_SPEED
        elif key == arcade.key.W:
            self.watergirl.saltar()

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.fireboy.change_x = 0

        if key in [arcade.key.A, arcade.key.D]:
            self.watergirl.change_x = 0

class Nivel1(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=1)
        
        """# Cargamos el sonido de la vista del nivel 1
        musica = os.path.join("assets", "musica_niveles", "musica_mapa_niveles.mp3")
        self.musica_mapa = arcade.load_sound(musica)"""

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
        self.fireboy = Fireboy()
        self.fireboy.texture = arcade.load_texture("chico.png")
        self.fireboy.scale = 0.1
        self.fireboy.center_x = 150
        self.fireboy.center_y = 100
        self.scene.add_sprite("Fireboy", self.fireboy)

        self.watergirl = Watergirl()
        self.watergirl.texture = arcade.load_texture("chica.png")
        self.watergirl.scale = 0.1
        self.watergirl.center_x = 100
        self.watergirl.center_y = 200
        self.scene.add_sprite("Watergirl", self.watergirl)

        # Motores de física
        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        # Física
        self.fireboy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.fireboy, gravity_constant = GRAVITY, walls = muros
        )

        self.watergirl.physics_engine = arcade.PhysicsEnginePlatformer(
            self.watergirl, gravity_constant = GRAVITY, walls = muros
        )

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

        if not self.scene or not self.fireboy.physics_engine or not self.watergirl.physics_engine:
            return
        # Física
        self.fireboy.physics_engine.update()
        self.watergirl.physics_engine.update()

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.fireboy, self.watergirl):
            self.window.show_view(NivelPerdido(self.numero_nivel))
            return

        capas_muerte_water = ["Capa de patrones 2", "Capa de patrones 5"]
        capas_muerte_fire = ["Capa de patrones 2", "Capa de patrones 4"]

        # Colisiones de muerte
        for jugador, capas in [(self.fireboy, capas_muerte_fire), (self.watergirl, capas_muerte_water)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                except (KeyError, TypeError):
                    pass
        
        # Colisiones de victoria
        try:
            en_puerta_fire = arcade.check_for_collision_with_list(self.fireboy, self.scene["Capa de patrones 7"])
            en_puerta_water = arcade.check_for_collision_with_list(self.watergirl, self.scene["Capa de patrones 6"])
            if en_puerta_fire and en_puerta_water:
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except (KeyError, TypeError):
            pass

class Nivel2(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=2)

        self.objetos_que_caen = None
        self.tiempo_spawn = 0

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
        
        self.fireboy = Fireboy()
        self.fireboy.texture = arcade.load_texture("chico.png")
        self.fireboy.scale = 0.07 
        self.fireboy.center_x = self.ancho_logico - 50
        self.fireboy.center_y = 50
        self.scene.add_sprite("Fireboy", self.fireboy)

        self.watergirl = Watergirl()
        self.watergirl.texture = arcade.load_texture("chica.png")
        self.watergirl.scale = 0.07  
        self.watergirl.center_x = 50
        self.watergirl.center_y = self.alto_logico - 50 
        self.scene.add_sprite("Watergirl", self.watergirl)

        self.objetos_que_caen = arcade.SpriteList()
        self.tiempo_spawn = 0

        try:
            muros = self.scene["Capa de patrones 1"]
        except KeyError:
            muros = []

        self.fireboy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.fireboy, gravity_constant=GRAVITY, walls=muros
        )
        self.watergirl.physics_engine = arcade.PhysicsEnginePlatformer(
            self.watergirl, gravity_constant=GRAVITY, walls=muros
        )

    def crear_objeto_que_cae(self):
        """Crea un coco que cae desde arriba"""
        ruta = os.path.join("proyecto2", "WhatsApp_Image_2026-05-07_at_00.13.20-removebg-preview.png")

        sprite = arcade.Sprite(ruta, 0.15)

        sprite.center_x = random.randint(0, self.ancho_logico)
        sprite.center_y = self.alto_logico + 50
        sprite.change_y = -5

        self.objetos_que_caen.append(sprite)

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
        if not self.scene or not self.fireboy.physics_engine or not self.watergirl.physics_engine:
            return
            
        self.fireboy.physics_engine.update()
        self.watergirl.physics_engine.update()

        # Colisiones entre los personajes
        if arcade.check_for_collision(self.fireboy, self.watergirl):
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
            if arcade.check_for_collision(coco, self.fireboy) or arcade.check_for_collision(coco, self.watergirl):
                self.window.show_view(NivelPerdido(self.numero_nivel))
                return
            # Limpiar cocos que ya cayeron por debajo del mapa
            if coco.center_y < -100:
                coco.remove_from_sprite_lists()

        capas_muerte_water = ["Capa de patrones 7", "agua"]
        capas_muerte_fire = ["Capa de patrones 7", "Capa de patrones 5"]

        # Colisiones de muerte por zonas peligrosas
        for jugador, capas in [(self.fireboy, capas_muerte_fire), (self.watergirl, capas_muerte_water)]:
            for nombre in capas:
                try:
                    if arcade.check_for_collision_with_list(jugador, self.scene[nombre]):
                        self.window.show_view(NivelPerdido(self.numero_nivel))
                        return
                except (KeyError, TypeError):
                    pass

        # Colisiones de victoria
        try:
            en_puerta_fire = arcade.check_for_collision_with_list(self.fireboy, self.scene["Capa de patrones 2"])
            en_puerta_water = arcade.check_for_collision_with_list(self.watergirl, self.scene["Capa de patrones 3"])
            
            if en_puerta_fire and en_puerta_water:
                self.window.show_view(NivelConseguido(self.numero_nivel))
        except (KeyError, TypeError):
            pass

class Nivel3(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=3)

class Nivel4(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=4)

class Nivel5(Nivel):
    def __init__(self):
        super().__init__(numero_nivel=5)

CLASES_NIVELES = {
    1: Nivel1,
    2: Nivel2,
    3: Nivel3,
    4: Nivel4,
    5: Nivel5
}

if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Juego", resizable=True)
    window.volumen = 0.5
    menu = MenuView()
    window.show_view(menu)
    arcade.run()