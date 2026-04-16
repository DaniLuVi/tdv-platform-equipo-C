import arcade

# --- CONFIGURACIÓN DINÁMICA ---
# Obtenemos el tamaño del monitor para que casi lo ocupe todo
# (Le restamos un poco de margen para que se vea la barra de tareas)
monitor = arcade.get_display_size()
SCREEN_WIDTH = int(monitor[0] * 0.9)
SCREEN_HEIGHT = int(monitor[1] * 0.8)
SCREEN_TITLE = "Menú Principal - Pantalla Completa"

# --- VISTA: MENÚ PRINCIPAL ---
class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        
        # Título centrado dinámicamente
        arcade.draw_text("MI VIDEOJUEGO", self.window.width / 2, self.window.height * 0.75,
                         arcade.color.WHITE, font_size=60, anchor_x="center")

        # --- BOTÓN 1: INICIAR PARTIDA ---
        # Calculamos la posición central
        cx, cy = self.window.width / 2, self.window.height / 2
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy - 25, cy + 25, arcade.color.ARMY_GREEN)
        arcade.draw_text("INICIAR PARTIDA", cx, cy,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # --- BOTÓN 2: AJUSTES ---
        # Lo ponemos un poco más abajo del centro
        cy_ajustes = cy - 80
        arcade.draw_lrbt_rectangle_filled(cx - 150, cx + 150, cy_ajustes - 25, cy_ajustes + 25, arcade.color.SLATE_GRAY)
        arcade.draw_text("AJUSTES", cx, cy_ajustes,
                         arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2
        
        # Clic en Iniciar
        if cx - 150 < x < cx + 150 and cy - 25 < y < cy + 25:
            game_view = GameView()
            self.window.show_view(game_view)

        # Clic en Ajustes
        cy_ajustes = cy - 80
        if cx - 150 < x < cx + 150 and cy_ajustes - 25 < y < cy_ajustes + 25:
            settings_view = SettingsView()
            self.window.show_view(settings_view)

# --- VISTA: EL JUEGO ---
class GameView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        arcade.draw_text("PANTALLA DE JUEGO", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text("Presiona ESC para volver al menú", self.window.width / 2, 100,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

# --- VISTA: AJUSTES ---
class SettingsView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BATTLESHIP_GREY)

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
        arcade.draw_lrbt_rectangle_filled(cx - 120, cx - 40, cy - 20, cy + 20, arcade.color.RED_DEVIL)
        arcade.draw_text("-", cx - 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Más (+)
        arcade.draw_lrbt_rectangle_filled(cx + 40, cx + 120, cy - 20, cy + 20, arcade.color.GREEN)
        arcade.draw_text("+", cx + 80, cy, arcade.color.WHITE, font_size=30, anchor_x="center", anchor_y="center")

        # Botón Volver
        arcade.draw_lrbt_rectangle_outline(cx - 60, cx + 60, 90, 130, arcade.color.WHITE, border_width=2)
        arcade.draw_text("VOLVER", cx, 110, arcade.color.WHITE, font_size=15, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x, y, button, modifiers):
        cx, cy = self.window.width / 2, self.window.height / 2

        # Clic en MENOS (-)
        if cx - 120 < x < cx - 40 and cy - 20 < y < cy + 20:
            self.window.volumen = max(0.0, self.window.volumen - 0.1)

        # Clic en MÁS (+)
        elif cx + 40 < x < cx + 120 and cy - 20 < y < cy + 20:
            self.window.volumen = min(1.0, self.window.volumen + 0.1)

        # Clic en VOLVER
        elif cx - 60 < x < cx + 60 and 90 < y < 130:
            self.window.show_view(MenuView())

# --- FUNCIÓN PRINCIPAL ---
def main():
    # Creamos la ventana con el tamaño calculado
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

    window.volumen = 0.5

    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()