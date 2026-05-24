import pygame
import os
from pytmx.util_pygame import load_pygame

# =========================================================================
# 1. CONFIGURACIÓN INICIAL
# =========================================================================
pygame.init()
# Esta será la ventana real que verás en tu monitor (tamaño estándar)
ANCHO_VENTANA = 1024
ALTO_VENTANA = 768
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Nuestro Videojuego - Mapa Ajustado a Pantalla")
reloj = pygame.time.Clock()

DIRECTORIO_ACTUAL = os.path.dirname(__file__)
RUTA_MAPA = os.path.join(DIRECTORIO_ACTUAL, "desierto mapa.tmx")

# Cargar el mapa
try:
    mapa_tiled = load_pygame(RUTA_MAPA)
except Exception as e:
    print(f"Error al cargar el mapa: {e}")
    pygame.quit()
    exit()

# =========================================================================
# 2. CREAR EL "LIENZO VIRTUAL" Y LAS COLISIONES
# =========================================================================
# Calculamos el tamaño real y gigante del mapa
ANCHO_MAPA_REAL = mapa_tiled.width * mapa_tiled.tilewidth
ALTO_MAPA_REAL = mapa_tiled.height * mapa_tiled.tileheight

# Creamos una superficie invisible del tamaño exacto del mapa
superficie_virtual = pygame.Surface((ANCHO_MAPA_REAL, ALTO_MAPA_REAL))

# Detectar el suelo para no caer al vacío
bloques_con_colision = []
for capa in mapa_tiled.visible_layers:
    if hasattr(capa, 'data'):
        # Recuerda revisar que este nombre coincide con el de tu capa de Tiled
        if capa.name.lower() in ["suelo", "arena", "plataformas"]:
            for x, y, _ in capa.tiles():
                px = x * mapa_tiled.tilewidth
                py = y * mapa_tiled.tileheight
                rect_bloque = pygame.Rect(px, py, mapa_tiled.tilewidth, mapa_tiled.tileheight)
                bloques_con_colision.append(rect_bloque)

# =========================================================================
# 3. CLASE DEL PERSONAJE
# =========================================================================
class Jugador:
    def __init__(self, x, y, nombre_imagen, controles):
        # 1. Mantenemos el rectángulo de colisión (Ancho: 96, Alto: 144)
        self.rect = pygame.Rect(x, y, 96, 144)
        
        # 2. Guardamos los controles asignados a este jugador ("flechas" o "wasd")
        self.controles = controles
        
        # 3. Cargar la imagen del personaje según el nombre que le pasemos ('chico' o 'chica')
        ruta_personaje = os.path.join(DIRECTORIO_ACTUAL, f"{nombre_imagen}.png")
        try:
            imagen_original = pygame.image.load(ruta_personaje).convert_alpha()
            # Escalamos la imagen para que encaje en el rectángulo de 96x144
            self.imagen = pygame.transform.scale(imagen_original, (self.rect.width, self.rect.height))
        except Exception as e:
            print(f"Error: No se encontró la imagen en {ruta_personaje}. Usando un cuadro temporal.")
            # Si no encuentra la imagen, crea un cuadro de color liso para que el juego no se rompa
            self.imagen = pygame.Surface((self.rect.width, self.rect.height))
            self.imagen.fill((255, 0, 0) if nombre_imagen == "chico" else (255, 105, 180))

        # Variables de físicas
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_suelo = False
        
        self.GRAVEDAD = 0.8
        self.FUERZA_SALTO = -14
        self.VELOCIDAD_CAMINAR = 5

    def manejar_entrada(self):
        teclas = pygame.key.get_pressed()
        self.velocidad_x = 0
        
        # --- CONTROLES PERSONALIZADOS ---
        if self.controles == "wasd":
            if teclas[pygame.K_a]:
                self.velocidad_x = -self.VELOCIDAD_CAMINAR
            if teclas[pygame.K_d]:
                self.velocidad_x = self.VELOCIDAD_CAMINAR
            if teclas[pygame.K_w] and self.en_suelo:
                self.velocidad_y = self.FUERZA_SALTO
                self.en_suelo = False
                
        elif self.controles == "flechas":
            if teclas[pygame.K_LEFT]:
                self.velocidad_x = -self.VELOCIDAD_CAMINAR
            if teclas[pygame.K_RIGHT]:
                self.velocidad_x = self.VELOCIDAD_CAMINAR
            if teclas[pygame.K_UP] and self.en_suelo:
                self.velocidad_y = self.FUERZA_SALTO
                self.en_suelo = False

    def actualizar(self, plataformas):
        # Gravedad
        self.velocidad_y += self.GRAVEDAD
        if self.velocidad_y > 15:
            self.velocidad_y = 15

        # Movimiento Horizontal
        self.rect.x += self.velocidad_x
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.velocidad_x > 0: self.rect.right = p.left
                if self.velocidad_x < 0: self.rect.left = p.right

        # Movimiento Vertical
        self.rect.y += self.velocidad_y
        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p):
                if self.velocidad_y > 0:
                    self.rect.bottom = p.top
                    self.velocidad_y = 0
                    self.en_suelo = True
                elif self.velocidad_y < 0:
                    self.rect.top = p.bottom
                    self.velocidad_y = 0

    def dibujar(self, superficie):
        # Dibujamos la imagen del personaje en su posición
        superficie.blit(self.imagen, self.rect)


# =========================================================================
# CREAR A LOS PERSONAJES
# =========================================================================

# 1. El personaje de la izquierda (arriba)
# X = 150 (cerca de la izquierda), Y = 50 (muy arriba, caerá sobre la primera plataforma)
chico = Jugador(150, 50, "chico", "wasd")

# 2. El personaje de la derecha (abajo)
# Como Python ya sabe cuánto mide el mapa de ancho y de alto, usamos esas 
# variables restándoles un trozo para colocarlo en la esquina inferior derecha.
chica = Jugador(ANCHO_MAPA_REAL - 300, ALTO_MAPA_REAL - 400, "chica", "flechas")

lista_jugadores = [chico, chica]

# =========================================================================
# 4. BUCLE PRINCIPAL DEL JUEGO
# =========================================================================
ejecutando = True
while ejecutando:
    reloj.tick(60)

    # === ACTUALIZAR LÓGICAS ===
    for personaje in lista_jugadores:
        personaje.manejar_entrada()
        personaje.actualizar(bloques_con_colision)

    # === FASE DE DIBUJO ===
    superficie_virtual.fill((135, 206, 235)) # Cielo azul

    # Dibujar el mapa gigante
    for capa in mapa_tiled.visible_layers:
        if hasattr(capa, 'data'):
            for x, y, imagen_bloque in capa.tiles():
                px = x * mapa_tiled.tilewidth
                py = y * mapa_tiled.tileheight
                superficie_virtual.blit(imagen_bloque, (px, py))

    # Dibujar a TODOS los personajes de la lista encima del mapa
    for personaje in lista_jugadores:
        personaje.dibujar(superficie_virtual)

    # Encoger el lienzo virtual y pegarlo en la ventana real
    pantalla_escalada = pygame.transform.scale(superficie_virtual, (ANCHO_VENTANA, ALTO_VENTANA))
    pantalla.blit(pantalla_escalada, (0, 0))

    pygame.display.flip()

pygame.quit()