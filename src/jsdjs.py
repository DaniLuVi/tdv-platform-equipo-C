import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"
class MainMenu(arcade.View):
    def on_show_view(self):
        self.window.background_color = arcade.color.WHITE

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Main Menu - Click To Play",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            arcade.color.BLACK,
            font_size=30,
            anchor_x="center"
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)

if __name__ == "__main__":
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, "JSDJS")
    main_menu = MainMenu()
    window.show_view(main_menu)
    arcade.run()