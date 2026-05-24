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
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_suelo = False
        
        # Puedes cambiar estos números si quieres que salte menos o corra más
        self.GRAVEDAD = 0.8
        self.FUERZA_SALTO = -14
        self.VELOCIDAD_CAMINAR = 5

    def manejar_entrada(self):
        teclas = pygame.key.get_pressed()
        self.velocidad_x = 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.velocidad_x = -self.VELOCIDAD_CAMINAR
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.velocidad_x = self.VELOCIDAD_CAMINAR
            
        if (teclas[pygame.K_SPACE] or teclas[pygame.K_w]) and self.en_suelo:
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
                if self.velocidad_x > 0:
                    self.rect.right = p.left
                if self.velocidad_x < 0:
                    self.rect.left = p.right

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
        pygame.draw.rect(superficie, (255, 0, 0), self.rect)


# Posición inicial del jugador (x=100, y=100)
jugador = Jugador(100, 100)

# =========================================================================
# 4. BUCLE PRINCIPAL DEL JUEGO
# =========================================================================
ejecutando = True
while ejecutando:
    reloj.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Actualizar jugador
    jugador.manejar_entrada()
    jugador.actualizar(bloques_con_colision)

    # -------------------------------------------------------------
    # FASE DE DIBUJO
    # -------------------------------------------------------------
    # 1. Limpiamos el lienzo virtual (azul cielo)
    superficie_virtual.fill((135, 206, 235)) 

    # 2. Dibujamos el mapa gigante en el lienzo virtual
    for capa in mapa_tiled.visible_layers:
        if hasattr(capa, 'data'):
            for x, y, imagen_bloque in capa.tiles():
                px = x * mapa_tiled.tilewidth
                py = y * mapa_tiled.tileheight
                superficie_virtual.blit(imagen_bloque, (px, py))

    # 3. Dibujamos al jugador en el lienzo virtual
    jugador.dibujar(superficie_virtual)

    # 4. Magia: Encogemos el lienzo virtual para que quepa en nuestra ventana
    pantalla_escalada = pygame.transform.scale(superficie_virtual, (ANCHO_VENTANA, ALTO_VENTANA))
    
    # 5. Pegamos el resultado final en la ventana del juego
    pantalla.blit(pantalla_escalada, (0, 0))

    pygame.display.flip()

pygame.quit()