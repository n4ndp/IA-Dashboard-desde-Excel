vamos a hacer lo siguiente:
- actualmente mi backend no esta bien implementado, y por eso hay problemas con el frontend, vamos a definir los endpoints de mi backend correctamente, separar servicios correctamente, para luego, pasar a hacer las paginas de mi frontend, es decir, actualmente, siento que todo esta mal y desordenado.

ayudame a pensar lo siguiente:
todos los endpoints que tengo, cual es su entrada y su salida de la ruta, y su utilidad.

estaba pensando, por ejemplo, la pagina base en el frontend es: http://localhost:5173, y en localstorage o sesion storage podria guardar el nombre, y si el nombre no existe o no hay: ya sabemos que la pagina http://localhost:5173/ te muestra "bienvenido" y esas cosas (lo puedes confirmar revisando el codigo), pero si el nombre si existe, es decir, si ya he puesto mi nombre, me dirige a "http://localhost:5173/proyects", siento que para manejar mejor los valores, seria asi: http://localhost:5173/u/{aqui el id del usuario}/p", ya no proyects, solo "p", "u" haciendo referencia al usuario, p al proyecto.

creo que de esa forma se me facilitarian muchas cosas, por otro lado, al entrar a un proyecto, mi pagina tendria la url asi: "http://localhost:5173/u/{aqui el id del usuario}/p/{aqui el id del proyecto}"

entonces, ayudame a definir todos los endpoints utiles y rutas utiles para poder hacer todo correctamente y optimo, y util
