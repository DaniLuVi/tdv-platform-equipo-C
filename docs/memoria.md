# Memoria del proyecto

## 1. Introducción y conecpto del juego

- Descripción general:

El nombre de nuestro videojuego es: Stella & Galaxy

Es un videojuego de plataformas cooperativo, en el que los dos personajes principales deberán ir superando los distintos niveles en los que cada personaje deberá de llegar a un lugar, podrá tocar o no ciertas zonas y habilitar/deshabilitar cosas del nivel mediante palancas.

Para escoger realizar este juego, nos inspiramos en el juego de Fireboy & Watergirl, siguiendo luego nuestras propias decisiones para el diseño.

- Objetivos del proyecto:

Para la realización del videojuego se ha utilizado lenguaje Python, empleando el paradigma imperativo y el paradigma orientado a objetos (POO). Además, se ha implementado la biblioteca Arcade que se requería para la práctica, con la versión 3.3.3. 

Para el desarrollo del código hemos usado Visual Studio Code, para el diseño de niveles usamos la aplicación Tile Map Editor, y también hemos usado otras herramientas para crear nuestros propios personajes.

El objetivo a intentar superar era el ser capaces de poder crear varios niveles en los que la cooperación entre los dos personajes fuera divertida, no fuera ni fuy fácil ni tampoco demasiado difícil y ser capaces de diseñar distintas mecánicas que no hicieran el juego monótono.

## 2. Arquitectura del software y estructura del código

- Diseño de vistas:

Para el correcto movimiento entre las distintas vistas del juego hemos ido estructurando una ventana principal que se creaba al principio, y realizamos un flujo correcto para el intercambio de las vistas de forma eficaz.

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

Se hace uso de la herencia para los personajes, Sprites y vistas de Arcade, y para los distintos niveles del juego (con una clase Nivel general que define cosas que son comunes para todos los niveles). Se implementa una clase abstracta Personaje (que hereda de arcade.Sprite) de la cual nacen las subclases Fireboy y Watergirl, polimorfismo que permite gestionar de manera independiente las reglas de supervivencia de cada elemento (inmunidad a lava o agua). De la misma forma, se diseñó una clase base Nivel(arcade.View) que centraliza la lógica común de captación de teclado, actualización de motores físicos y renderizado de la cámara, permitiendo que las clases específicas de cada nivel hereden toda esta infraestructura y solo tengan que encargarse de inicializar su propio mapa TMX.

## 3. Sistema de guardado y cargado de datos

Para hacer un buen guardado del progreso de las partidas hemos utilizado una estructura en formato JSON que almacenase el estado en el que se encuentran los niveles (no superado, superado y bloqueado), además de un identificador de la partida que era guardada. 

Hemos decidido poner un límite máximo de 10 partidas guardadas, por el hecho de que la forma de visualizarlo en la vista del cargado de partidas no pudiera acabar estando muy cargado de botones.

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

Para el cargado de partidas posterior que ocurre en la vista SeleccionPartida, son mostradas todas las partidas guardadas en distintos botones que se pueden organizar en dos columnas. Al pulsar en cualquiera de esos botones, se carga la vista Mapa con el mapa de niveles en el que se muestre el progreso almacenado de forma efectiva con las imágenes del estado de cada nivel.

Para evitar la saturación visual, la interfaz distribuye dinámicamente los botones mediante contenedores UIBoxLayout. El algoritmo lee los índices de las partidas del JSON mediante un bucle enumerado: las primeras 5 partidas se inyectan en una columna vertical izquierda y las 5 restantes en una columna derecha, manteniendo el diseño perfectamente equilibrado y simétrico en el centro de la pantalla.

## 4. Dificultades encontradas
