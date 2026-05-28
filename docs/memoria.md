# Memoria del proyecto

## 1. Introducción y concepto del juego

- Descripción general:

El nombre del videojuego que ha sido diseñado es: Stella & Galaxy.

Es un videojuego de plataformas cooperativo en el que los dos personajes principales deben superar los distintos niveles. Cada personaje tiene que alcanzar su puerta correspondiente, esquivando zonas letales según su elemento afín y colaborar para habilitar o deshabilitar bloqueos del escenario mediante botones y palancas.

Para la concepción de este juego nos inspiramos en el juego 'Fireboy & Watergirl', siguiendo nuestras propias decisiones de diseño, mecánicas y estéticas.

- Objetivos del proyecto:

Para la realización del videojuego se ha utilizado el lenguaje Python, empleando el paradigma imperativo como la Programación Orientado a Objetos (POO). Además, se ha implementado la biblioteca Arcade requerida para la práctica, concretamente con la versión 3.3.3. 

Para el desarrollo del código hemos utilizado Visual Studio Code; para el diseño de niveles, la aplicación Tile Map Editor; y también otras herramientas de edición de imagen para crear nuestros propios personajes y las escenas para representar la historia.

El objetivo principal era crear varios niveles donde la cooperación entre los dos personajes fuera divertida y equilibrada (ni fuera muy fácil, ni tampoco demasiado difícil), e integrar y diseñar distintas mecánicas que rompieran la monotonía del juego.

## 2. Arquitectura del software y estructura del código

- Diseño de vistas e Interfaz Gráfica (GUI):

Para el correcto flujo del juego se ha estructurado una ventana principal sobre la que se intercambian distintas vistas (arcade.View) de forma eficaz.

El programa comienza mostrando una vista inicial llamada MenuView en la que se muestra una pantalla de juego inicial con el título y la ambientación del videojuego. En el centro se muestran unos botones:
  1. El botón de "Iniciar partida" cambia a la vista Mapa en el que se muestra el mapa con los distintos niveles.
  2. El botón de "Continuar partida" cambia a la vista SeleccionPartida en la que se muestran las partidas guardadas que pueden ser cargadas para retomar su progreso
  3. El botón de "Ajustes" cambia a la vista SettingsView en la que se puede modificar el volumen de la música del juego

Pasamos a la vista Mapa, con el mapa de niveles. En esta vista se puede ver un fondo ambiente, el camino de niveles a superar en el que se puede ver claramente con la imagen qué nivel ha sido superado, qué nivel no ha sido superado todavía y qué nivel se encuentra bloqueado y no se puede acceder a él. Tambíen se puede ver arriba a la derecha un botón para guardar el progreso de la partida o abajo unos textos con los niveles superados y la forma de volver atrás.

Las vistas de los distintos niveles se muestran con mas detalle en el archivo "gdd.md". La vista del nivel se muestra con el nivel en el centro de la pantalla, dejando dos franjas negras a ambos laterales de la pantalla. El recuadro del nivel se mantiene encajado en el centro geométrico de la pantalla mediante el uso de una cámara arcade.Camera2D fijada en el centro del escenario, logrando que el espacio restante se rellene automáticamente con franjas negras de forma limpia.

Cuando en un nivel algún personaje muere o se consigue superar el nivel, aparece una vista mostrando la conclusión del intento del nivel y se muestran dos botones:
  1. Un botón de "Reiniciar Nivel"/"Siguiente Nivel" en el que (haciendo click o pulsando ENTER) se reinicia el nivel o se muestra el nivel inmediatemanete posterior
  2. Un botón de "Volver al mapa" para volver a la vista Mapa con el mapa de niveles

- Estructura general:

Se ha hecho un uso bastante eficiente de las vistas en Arcade, como se ha podido explicar antes. Además, el código es eficiente y está bien organizado gracias al buen uso de los paradigmas soportados por el lenguaje Python.

Se hace uso de la herencia para los personajes, Sprites y vistas de Arcade, y para los distintos niveles del juego (con una clase Nivel general que define cosas comunes para todos los niveles). Se implementa una clase abstracta Personaje (que hereda de arcade.Sprite) de la cual nacen las subclases Fireboy y Watergirl, polimorfismo que permite gestionar de manera independiente las reglas de supervivencia de cada elemento (inmunidad a lava o agua). De la misma forma, se diseñó una clase base Nivel(arcade.View) que centraliza la lógica común de captación de teclado, actualización de motores físicos y renderizado de la cámara, permitiendo que las clases específicas de cada nivel hereden toda esta infraestructura y solo tengan que encargarse de inicializar su propio mapa TMX.

## 3. Sistema de guardado y cargado de datos

Para una correcta persistencia de datos se ha utilizado una estructura en formato JSON, que almacenase el estado en el que se encuentran los niveles ('no superado', 'superado' o 'bloqueado'), además de un identificador de la partida guardada. 

Se ha establecido un límite máximo de 10 partidas guardadas, para que la visualización en la vista del cargado de partidas no se cargue de muchos botones.

Un ejemplo de una partida guardada directamente del JSON almacenado pordía ser: 
{...,
    "Partida 3": {
        "1": "no_conseguido",
        "2": "bloqueado",
        "3": "bloqueado",
        "4": "bloqueado",
        "5": "bloqueado"
    }, 
...
}

Para el cargado de partidas que ocurre en la vista SeleccionPartida, se muestran todas las partidas guardadas en distintos botones organizados en dos columnas, mediante un gestor de interfaz de Arcade (UIBoxLayout). 

Para evitar la saturación visual, la interfaz distribuye dinámicamente los botones mediante contenedores UIBoxLayout. El algoritmo lee los índices de las partidas del JSON mediante un bucle enumerado: las primeras 5 partidas se inyectan en una columna vertical izquierda y las 5 restantes en una columna derecha, manteniendo el diseño perfectamente equilibrado y simétrico en el centro de la pantalla.

Al pulsar cualquiera de esos botones, se carga la vista Mapa con el mapa de niveles en el que se muestre el progreso almacenado de forma efectiva con las imágenes del estado de cada nivel.

## 4. Dificultades encontradas

Durante el ciclo de desarrollo han surgido varios retos técnicos, principalmente derivados de la integración de capas y el uso de las funciones de la versión 3.3.3 de la biblioteca Arcade:

Uno de los problemas que tuvimos fue que tras realizar commit y push, los cambios no se reflejaban correctamente en los ordenadores de mis compañeros. Se detectó que el código contenía rutas absolutas vinculadas al directorio local de mi ordenador. Sin embargo, encontramos la solución, modificamos todas las rutas para que el programa fuese funcional en cualquier ordenador.


