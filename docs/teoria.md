UNIDAD 1: Programación Orientada a Objetos.
¿Por qué se dice orientado a objetos? Porque el software se organiza como una colección
de objetos que incorporan tanto estructuras de datos como comportamientos
(procedimientos). Notar que esto contrasta con la programación estructurada, en la cual las
estructuras de datos y el comportamiento son independientes.
OBJETO: Un objeto tiene estado, comportamiento e identidad; la estructura y el
comportamiento de objetos similares están definidos en su clase común; los términos
instancia y objeto son intercambiables.
CLASE: Una clase es un conjunto de objetos que comparten una estructura común y un
comportamiento común. Las clases proveen una forma de empaquetar datos y
funcionalidad juntos. Al crear una nueva clase, se crea un nuevo tipo de objeto, permitiendo
crear nuevas instancias de ese tipo.
● INSTANCIA: Cada clase describe una posibilidad infinita de un conjunto individual de
objetos. Cada objeto que pertenezca a una clase es una instancia de la clase.
● IDENTIDAD: La identidad es aquella propiedad de un objeto que lo distingue de
todos los demás objetos. En otras palabras, dos objetos distintos son diferentes
aunque todos los valores de sus atributos sean idénticos.
Cuando un objeto se transforma en una realización de software, consta de: una
interfaz, una estructura de datos privada y unos procesos llamados operaciones o
métodos que son los únicos que pueden transformar legítimamente la estructura de
datos.
● ATRIBUTOS DE CLASE: Un atributo es una forma de conectar objetos. Hay dos
tipos de atributos:
○ de instancia: se definen utilizando self.
○ de clase: se definen sin utilizar self.
RELACIONES ENTRE CLASES Y OBJETOS:
● ASOCIACIÓN: Relación estructural que describe un conjunto de enlaces, donde un
enlace es una conexión entre objetos; relación semántica entre dos o más

clasificadores que implica la conexión entre sus instancias. En la “asociación” de un
objeto con otro se siguen las siguientes relaciones:
○ El objeto asociado (miembro) no está relacionado con el objeto (clase).
○ El objeto asociado (miembro) puede pertenecer a más de un objeto (clase) a
la vez.
○ El ciclo de vida del objeto asociado (miembro) no está gestionado por el
objeto (clase).
○ El objeto asociado (miembro) puede o no conocer la existencia del objeto
(clase).
● AGREGACIÓN: En una agregación, el objeto (clase) y la parte (miembro) deben
tener las siguientes relaciones:
○ La parte es parte del objeto.
○ La parte puede pertenecer a más de un objeto a la vez.
○ La existencia de la parte no está manejada por el objeto.
○ La parte no sabe sobre la existencia del objeto que lo agrega.

● COMPOSICIÓN: Forma de agregación con fuerte coincidencia y un tiempo de vida
coincidente entre las partes y el todo; las partes con una multiplicidad no fija pueden
ser creadas después del propio compuesto, pero una vez creadas viven y mueren
con él; tales partes también pueden ser eliminadas explícitamente antes de la
eliminación del compuesto. Para decir que la relación es una composición, el objeto
(clase) y la parte (miembro) deben tener las siguientes relaciones:

○ La parte es parte del objeto.
○ La parte sólo puede pertenecer a un objeto a la vez.
○ La existencia de la parte está manejada por el objeto.
○ La parte no sabe sobre la existencia del objeto.
● HERENCIA: Mecanismo por el que elementos más específicos incorporan la
estructura y comportamiento de elementos más generales. Es una relación entre
clases del tipo “es un(a)”. Por ejemplo: Una manzana es una fruta. Una estudiante
es una persona.

● DEPENDENCIA: La dependencia es la más simple de las relaciones entre clases de
objetos.

○ Se da cuando un objeto requiere de las funcionalidades de otro objeto para
completar una tarea.
○ Los objetos no están relacionados.
○ No forma parte de los miembros del objeto (clase).
PROPERTY: Cuando se desea acceder a atributos a través de una propiedad en Python, se
acuerda indicarlas en los diagramas UML con un pequeño texto indicador a la izquierda del
atributo entre comillas angulares (<< >> ó « ») que indique “ get ” si la propiedad cumple la
función de getter, o “ get/set ” si la propiedad cumple el rol de getter y setter.
ATRIBUTOS DE INSTANCIA Y ESTÁTICOS: Cuando se desea indicar el uso de atributos
de instancia (instance) simplemente se coloca el nombre del atributo y, opcionalmente, su
tipo. En cambio, cuando se desea indicar el uso de atributos estáticos (static), o con alcance
de clase (o simplemente “de clase”), se indica el nombre del atributo subrayado. Lo mismo
aplica a los métodos estáticos: se deben subrayar.

UNIDAD 2: Análisis y diseño orientado a objetos.
MODELOS Y METODOLOGÍAS:
MODELO DE OBJETOS: El modelo de objetos surgió como respuesta a la crisis del
software y su complejidad. El diseño orientado a objetos enfatiza la creación de programas
más cercanos a la forma en que las personas piensan sobre el mundo real. Permite trabajar
en un nivel de abstracción más alto, facilitando la gestión de la complejidad en el desarrollo
de software.
ELEMENTOS DEL MODELO DE OBJETOS:
● FUNDAMENTALES:
○ ABSTRACCIÓN: Una abstracción denota las características esenciales de un
objeto que lo distinguen de todos los demás tipos de objetos y proporciona
así barreras conceptuales nítidamente definidas respecto a la perspectiva del
observador. Las clases y objetos deberían estar al nivel de abstracción
adecuado: ni demasiado alto ni demasiado bajo.

○ ENCAPSULAMIENTO: El encapsulamiento es el proceso de almacenar en
un mismo compartimento los elementos de una abstracción que constituyen
su estructura y comportamiento; sirve para separar la interfaz contractual de
una abstracción y su implementación. El encapsulamiento oculta los detalles
de la implementación de un objeto
○ MODULARIDAD: Acto de fragmentar un programa en componentes
individuales para reducir su complejidad, o crear una serie de fronteras bien
definidas y documentadas dentro del programa. Estas fronteras son claves
para entender el programa.
■ El objetivo fundamental es el de reducir el costo de desarrollo y
prueba del software al permitir que los módulos se diseñen y revisen
independientemente.
■ La estructura de cada módulo debería ser lo suficientemente simple
como para ser comprendida en su totalidad.
■ Debería ser posible cambiar la implementación de sus módulos sin
saber nada de la implantación de otros módulos y sin afectar el
comportamiento de estos.
■ La facilidad de realizar un cambio en el diseño debería guardar
relación con la probabilidad de que este requerimiento se produzca.
Podemos definir la modularidad como la propiedad que tiene un sistema que
ha sido descompuesto en un conjunto de módulos cohesivos y débilmente
acoplados.
○ JERARQUÍA: Las Jerarquías son una clasificación u ordenación de
abstracciones. Las jerarquías en la OO pueden ser:
■ Jerarquía de clases o herencia , es una estructura de clases
relacionadas.
■ Jerarquía de partes o composición de objetos. Un objeto está
constituido por una instancia o más de otros objetos.
● SECUNDARIOS:
○ TIPIFICACIÓN: Los tipos son las puestas en vigor de la clase de objetos, de
modo que los objetos de tipos distintos no pueden intercambiarse o, si

pueden hacerlo, sólo lo harán en formas muy restringidas. Se define a tipo
como una caracterización precisa de propiedades estructurales o de
comportamiento que comparten una serie de entidades.
○ CONCURRENCIA: La concurrencia es la propiedad que distingue un objeto
activo de uno que no está activo.
○ PERSISTENCIA: Es la capacidad de un objeto por la que su existencia
trasciende en el tiempo (es decir el objeto continúa existiendo después de
que su creador deja de existir) y/o el espacio (es decir, la posición del objeto
varía con respecto al espacio de direcciones en el que fue creado).
ANÁLISIS Y DISEÑO ORIENTADO A OBJETOS:
Es una etapa en el desarrollo de software donde se analiza el problema y se trata de
encontrar una solución que se expresa utilizando objetos que interactúan entre sí. Estos
objetos forman parte del dominio o de la descripción o requerimientos del problema. En esta
etapa no escribimos código.
● Las clases deben diseñarse de manera que sean fáciles de comprender, desarrollar,
mantener y reutilizar.
● La utilización de un lenguaje orientado a objetos no garantiza que el software
desarrollado sea orientado a objetos.
El diseño orientado a objetos se utiliza para modelar un problema en términos de objetos
que interactúan entre sí. Los objetos deberían representar cosas físicas, conceptos, y
entidades de software, etc.
Una clase es una descripción de un grupo de objetos con propiedades comunes (atributos),
comportamiento común (operaciones), relaciones comunes con otros objetos

(colaboraciones), y semántica común. Se enfatizan las características relevantes y se
suprimen otras características.
● Las clases concretas , son las clases comunes que tienen implementación completa
y se pueden crear instancias de ella.
● Las clases abstractas no tienen una implementación completa. No se puede
construir instancias de esta clase.
● En la herencia se reúnen propiedades y comportamientos comunes al conjunto de
clases. La clase Madre, Base o Superclase es más general. Las clases Hijas,
Derivadas o Subclases, heredan las propiedades y comportamientos, y también las
pueden redefinir.
Un objeto es una instancia de una clase.
METODOLOGÍA CRC:
En la metodología CRC se captura el modelo de objetos como clases, responsabilidades,
colaboración y la relación entre subclases y superclases.
● La metodología provee una guía para aplicar en las primeras etapas de un diseño.
Es un enfoque informal, para trabajo en grupos, con énfasis en juego de roles.
● El elemento principal en la documentación y pruebas en esta metodología es la
Tarjeta CRC. Cada clase se representa en una tarjeta (7x14 cm):

● La creación de las tarjetas es el aspecto más importante en la técnica de las tarjetas
CRC, no las tarjetas en sí mismas:
1. Identificar posibles clases:
■ Los sustantivos o frases sustantivas son buenos indicadores de
posibles clases.

■ Los verbos o frases verbales son buenos indicadores de posibles
responsabilidades.
2. Crear una tarjeta por cada clase.
3. Realizar una previsión de posibles escenarios de uso:
■ Comenzar con un funcionamiento “ideal” y luego pasar a casos
excepcionales.
4. Ensayar escenarios:
■ Recorriendo el escenario el grupo simula lo que el sistema debe
hacer jugando su rol e interactuando con cada uno de los otros.
● Los escenarios son ejemplos detallados de funciones del sistema. Describen qué
ocurre en el sistema desde una vista de alto nivel. La simulación para el escenario
debe ser dinámica y antropomórfica. Pueden existir escenarios relacionados.
● Las tarjetas de clase son clases estáticas. Cuando las tarjetas se ponen en juego
representan objetos dinámicos.
● El Método CRC es iterativo. Una vez identificadas las clases y creadas las tarjetas
CRC, deberían refinarse trabajando sobre varios escenarios de uso
● El Método CRC ofrece los siguientes beneficios:
○ Portabilidad: las tarjetas CRC pueden ser usadas para resolver cualquier
problema.
○ Prototipado: los participantes experimentan de primera mano cómo
funcionará el sistema.
○ Promueve el pensamiento orientado a objetos: es un método efectivo para
reforzar conceptos de orientación a objetos.
○ Permite identificar huecos en los requerimientos: utilizando escenarios,
requerimientos incompletos pueden ser identificados y solucionados.
● El producto final del Método CRC es un primer borrador del diseño final. Es probable
que la estructura de clases resultante necesite mayor refinamiento para asegurarse
que el diseño es extensible y posee clases reutilizables en otras aplicaciones

DIAGRAMAS DE ROLE & PLAY: Se utilizan para documentar la interacción entre objetos
durante la ejecución de un escenario.
● Los objetos en el RPD son instancias de las clases modeladas por tarjetas CRC.
● Los objetos en un RPD son representados por tarjetas de objetos.
● Una tarjeta de objetos muestra el nombre, clase y propiedades relevantes para el
escenario en análisis.

● La interacción entre objetos se documenta como líneas de conexión entre los
objetos que se comunican.
● Responsabilidades : Es conocimiento que la clase tiene y servicios que provee. En
el momento de interpretar los escenarios el analista debe poder conocer y
desarrollar las responsabilidades de las clases.
● Colaboradores: Un colaborador es una clase cuyos servicios son necesarios para
cumplir una responsabilidad.
METODOLOGÍA UML:
UML significa Lenguaje de unificado de modelado. Es un estándar para generar un modelo
gráfico de un sistema. Cuenta con una gran variedad de diagramas:
● Diagramas de clases.

● Diagramas de secuencia.
● Diagramas de casos de uso.
INTRODUCCIÓN A LAS PRUEBAS UNITARIAS:
La entropía del software es la tendencia que tiene el código a deteriorarse. Cada vez que
se cambia el código base, la entropía del software tiende a aumentar. Se le denomina

regresión a aquella situación en la que una característica de un software deja de funcionar
como se pretendía luego de cierto evento,
usualmente, una modificación de código.
Las pruebas de software ayudan a revertir la
tendencia de aumento de la entropía. Son una
herramienta que provee seguridad contra la mayoría
de las regresiones. Las pruebas ayudan a asegurar
que las funcionalidades existentes se conserven. La
desventaja que incorporan las pruebas es que
requieren un esfuerzo inicial adicional, a veces
significativo.
Se debe considerar tanto el valor de la prueba como su costo de mantenimiento. El
componente de costo está determinado por la cantidad de tiempo dedicado a actividades:
● Refactorización de la prueba cuando se refactoriza el código subyacente.
● Ejecutar la prueba en cada cambio de código.
● Manejo de falsas alarmas provocadas por la prueba.
● Pasar tiempo leyendo la prueba cuando intenta comprender cómo se comporta el
código subyacente.
Como el código de pruebas es un código que garantiza la correctitud de determinadas
porciones del código base, se suelen usar métricas de coberturas para establecer qué
porcentaje del código base se está probando. Una métrica de cobertura muestra cuánto
código fuente ejecuta un banco de pruebas con un indicador que va de 0 a 100%.

𝐶𝑜𝑏𝑒𝑟𝑡𝑢𝑟𝑎 𝑑𝑒 𝑐ó𝑑𝑖𝑔𝑜 = 𝑁ú𝑚𝑒𝑟𝑜^ 𝑁𝑑𝑒ú^ 𝑚𝑙í𝑛𝑒𝑟𝑒𝑜𝑎 𝑠𝑡^ 𝑜𝑑𝑡𝑒𝑎^ 𝑐𝑙 ó𝑑𝑑𝑒𝑖 𝑔𝑙í𝑛𝑜^ 𝑒𝑒𝑎𝑗𝑒𝑠𝑐𝑢𝑡𝑎𝑑𝑎𝑠

𝐶𝑜𝑏𝑒𝑟𝑡𝑢𝑟𝑎 𝑑𝑒 𝑟𝑎𝑚𝑎𝑠 = 𝑁ú𝑚𝑒𝑟𝑜^ 𝑑𝑁𝑒ú^ 𝑙𝑚í𝑛𝑒𝑒𝑟𝑎𝑜𝑠 𝑡^ 𝑑𝑜𝑒𝑡𝑎^ 𝑟𝑙𝑎 𝑑𝑚𝑒𝑎 𝑟𝑠𝑎^ 𝑎𝑚𝑡𝑎𝑟𝑠𝑎𝑣𝑒𝑠𝑎𝑑𝑎𝑠

Una prueba unitaria es una prueba automatizada que verifica un pequeño fragmento de
código (también conocido como unidad), lo hace rápido y lo hace de manera aislada.
El código que se prueba suele denominarse SUT o MUT. Se dice MUT cuando es un
método bajo prueba. En cambio se utiliza SUT, cuando la prueba se refiere a una clase.
Para estructurar una prueba unitaria existen varios métodos: el patrón AAA , se refiere a
separar cada prueba en tres partes Arreglar, Actuar, Aseverar.

● En la sección Arrange, se coloca el SUT y todas sus dependencias en el estado
deseado.
● En la sección Act, se llaman a los métodos en el SUT, se pasan las dependencias
preparadas y se captura la salida (si es que hay).
● En la sección Assert, se verifican los resultados.
La Biblioteca Estándar de Python provee la biblioteca unittest para soporte de pruebas
unitarias. Proporciona una clase base, TestCase, que se utiliza para crear nuevos casos de
uso. Esta clase proporciona varios métodos de aserción para comprobar y reportar fallos.

Coverage.py es una herramienta para medir la cobertura de código de programas hechos
en Python. El comando para instalar es: pip install coverage. El comando para hacer
cobertura de código con unittest es: coverage run -m unittest discover. Este comando se
ejecuta en la carpeta del proyecto y espera que el directorio y los archivos de prueba tengan
un nombre con “test_”. Descubre todos estos archivos, ejecuta las pruebas y genera un
reporte en un archivo con nombre “.coverage”, que puede ser volcado a la consola también
con el mismo programa coverage, mediante la ejecución: coverage report -m.
POLIMORFISMO:
El polimorfismo permite que un mismo mensaje a un objeto, pueda tener diferentes maneras
de responder. Lo que permite incorporar nuevos comportamientos sin modificar el código.

Permite escribir programas de manera general manipulando clases existentes y otras aún
por especificar. Es una característica esencial de los lenguajes orientados a objetos.
INVERSIÓN DE DEPENDENCIA: Los módulos de alto nivel no deben depender de módulos
de bajo nivel. Ambos deben depender de abstracciones.
Las abstracciones no deben depender de los detalles. Los detalles deben depender de las
abstracciones.
PRINCIPIOS SOLID:
S : Principio de Responsabilidad Única. Una clase debería tener solo una razón para
cambiar.
O : Principio de Abierto-Cerrado. Para poder cambiar los sistemas de manera sencilla, es
mejor poder extender (abierto para la extensión) añadiendo código y evitar cambiar el
código (cerrado para el cambio).
L : Principio de Sustitución de Liskov. Las interfaces deben adherirse a un contrato que les
permita ser sustituidas. Los subtipos deben ser sustituibles por sus tipos bases.
I : Principio de Segregación de Interfaces. Evitar depender de cosas que no se utilizan.
D : Principio de Inversión de Dependencias. El código que implementa políticas de alto nivel
no debería depender del código que implementa detalles de bajo nivel.
DUCK TYPING: Un estilo de programación que no revisa el tipo del objeto para determinar
si tiene la interfaz correcta; en vez de ello, el método o atributo es simplemente llamado o
usado.
Enfatiza las interfaces en vez de los tipos específicos. Un código bien diseñado puede tener
mayor flexibilidad permitiendo la sustitución polimórfica.
El “tipado de pato” evita usar pruebas llamando a type() o isinstance().

UNIDAD 3: Biblioteca estándar.
Una biblioteca es una colección de procedimientos, funciones, clases u otros elementos de
un programa de computadora que se encuentran disponibles para escribir programas.
Generalmente, los elementos de una biblioteca están agrupados en categorías que definen
su funcionalidad como módulos numéricos, interfaces gráficas, acceso a archivos, etc.
En una biblioteca estándar el equipo de desarrollo se esfuerza por incorporar las
características básicas necesarias para un amplio abanico de programas.
Deben tener un tamaño equilibrado. Si la biblioteca estándar de un lenguaje de
programación es demasiado grande podría incluir código que nunca se utiliza durante el
desarrollo y, si se exporta a los programas desarrollados, generará paquetes grandes en el
despliegue. Por el contrario, si es demasiado pequeña, podría originar problemas de
desarrollo porque en cada desarrollo nuevo se generaría la necesidad de incluir código
individualizado de tareas típicas.
BIBLIOTECA ESTÁNDAR DE PYTHON: La biblioteca estándar se distribuye con Python y
también permite algunos componentes opcionales. Es muy amplia y contiene módulos
incorporados:
● Escritos en C: brindan acceso a funcionalidades del SO (entrada/salida de archivos).
● Escritos en Python: proveen soluciones estandarizadas para problemas comunes
durante el desarrollo de programas.

PYPI: The Python Package Index (PyPI) is a repository of software for the Python
programming language.

FUNCIONES Y CONSTANTES INTEGRADAS: La biblioteca estándar incorpora una serie
de funciones integradas (built-in functions) siempre disponibles. También existe una serie de
constantes integradas (built-in constants): False, True, None, etc.

TIPOS INTEGRADOS: https://docs.python.org/es/3/library/stdtypes.html
Los principales tipos de datos son:
● Numéricos (int, float, complex).
● Secuencias (list, tuple, range, str).
○ Objetos para secuencias binarias: byte (Inmutables. Sólo admiten caracteres
ASCII de 0 a 127), bytearray (Mutables. Idem byte), memoryview.

● Mapas (dict). Un objeto de tipo mapping relaciona valores (que deben ser hashable)
con objetos de cualquier tipo. Los mapas son objetos mutables.
● Clases, instancias y excepciones.
PROTOCOLO DE ITERACIÓN: Python soporta el concepto de iteradores (para iterar) sobre
contenedores. Estos son usados por las clases definidas por el usuario para soportar
iteración. Las secuencias siempre soportan la iteración.
OBJETO ITERABLE: Un objeto se considera iterable ya sea si se trata de una secuencia
físicamente almacenada en memoria o de un objeto que produce un resultado a la vez en el
contexto de una herramienta de iteración como el bucle for. Es decir, los objetos iterables
pueden ser secuencias físicas o secuencias virtuales computadas a demanda.
En Python, los objetos iterables son capaces de retornar un iterador cuando se emplea la
función integrada iter(). A su vez, un iterador es capaz de responder al mensaje invocado
por la función integrada next() como se verá en los ejemplos siguientes.
El bucle for opera sobre cualquier objeto iterable:

En Python, se considera un iterador a cualquier objeto con un método next que
avance al siguiente resultado de la iteración, el cual lance una excepción StopIteration al
final de la serie de resultados. Algunos objetos iterables, son también iteradores.
Una forma alternativa de escribir un bucle for con un bucle while:

Ejemplo de una clase propia que satisfaga el protocolo de iteración:
● Emplea comprehensions para crear.

● Emplea la palabra reservada yield para crear.
UNIDAD 4: Manejo de excepciones.
ERRORES EN PYTHON: En Python se plantean al menos dos tipos de errores:
● Errores de sintaxis:

● Excepciones: Son errores detectados en la ejecución. Pueden estar integrados en la
Biblioteca Estándar o definidos por el usuario.
GESTIÓN DE EXCEPCIONES EN PYTHON:

a. Se ejecuta la cláusula try.
b. Si no ocurre ninguna excepción, la cláusula except se omite y la ejecución de try finaliza.
c. Si ocurre una excepción durante la ejecución de la cláusula try, se omite el resto de la
cláusula. Luego, si su tipo coincide con la excepción nombrada después de la palabra clave
except, se ejecuta la cláusula except, y luego la ejecución continúa después del bloque
try/except.
d. Si ocurre una excepción que no coincide con la indicada en la cláusula except se pasa a
los try más externos; si no se encuentra un gestor, se genera una unhandled exception
(excepción no gestionada) y la ejecución se interrumpe con un mensaje indicativo.
● Un bloque try puede manejar más de una excepción.

● Una clase en una cláusula except es compatible con una excepción si es de la
misma clase o de una clase derivada de la misma.
● Todas las clases de excepción heredan de BaseException. Las clases de excepción
definidas por el usuario heredan, generalmente, de Exception:
● El bloque try admite la palabra reservada else. Es útil para el código que debe
ejecutarse si la cláusula try no lanza una excepción. El uso de la cláusula else es
mejor que agregar código adicional en la cláusula try, porque evita capturar
accidentalmente una excepción que no fue generada por el código que está
protegido por la declaración try ... except.
LANZAMIENTO DE EXCEPCIONES: Se utiliza la palabra reservada raise. Permite forzar a
que ocurra una excepción específica:

El único argumento de raise indica la excepción a generarse. Debe ser una instancia o una
clase de excepción. Si es una clase de excepción, se hace implícitamente una instancia
llamando a su constructor sin argumentos.
ENCADENAMIENTO DE EXCEPCIONES: La palabra reservada raise admite la palabra
from , que habilita el encadenamiento de excepciones. Esto puede resultar útil cuando está
transformando excepciones.

ACCIONES DE LIMPIEZA: La declaración try tiene la cláusula opcional finally cuyo
propósito es definir acciones de limpieza que serán ejecutadas bajo ciertas circunstancias.
finally siempre se ejecuta. La excepción TypeError lanzada al dividir dos cadenas de texto
no es gestionado por la cláusula except y por lo tanto es relanzada luego de que se ejecuta
la cláusula finally.
¿QUÉ ES UN ERROR?: En una función f una falla es un error si impide que f tenga éxito en
su ejecución. Hay tres situaciones principales en la que se puede producir un error y en los
que se los debería manejar:
● Una condición que impide que f cumpla una precondición de otra función que debe
llamarse.
● Una condición que impide que la función f establezca una de sus propias
postcondiciones. Si la función tiene un valor de retorno, producir un objeto de valor
de retorno válido es una postcondición.
● Una condición que impide que la función restablezca un invariante que es
responsable de mantener. Este es un tipo especial de postcondición que se aplica
particularmente a los funciones miembro; una postcondición esencial de toda función
miembro no privada es que debe restablecer los invariantes de su clase.
GARANTÍAS DE SEGURIDAD: En cada función, brinde el mejor nivel de garantía de
seguridad que pueda, que no penalice a quienes llaman y no lo necesitan, pero que siempre
brinde, al menos, la garantía básica.
● Garantía básica: Es una promesa que en el caso de que una función arroje una
excepción el sistema se encontrará en un estado legal, correcto o válido. No hay

garantía sobre el estado del sistema en sí, los valores podrán cambiar, se podrían
perder algunos datos. Es una garantía débil.
● Garantía fuerte o sólida: Una función que se ejecuta bajo esta garantía, luego de
finalizar deja al sistema en uno de dos posibles estados:
○ Completa con éxito la tarea y lleva al sistema de un estado válido a otro
estado válido.
○ No hace nada y deja en el mismo estado que estaba justo antes de llamar a
la función.
● Garantía de no-falla o no lanzar excepción: Asegura que la tarea requerida
siempre se lleva a cabo. No hay lanzamiento de excepciones.

UNIDAD 5: Graficación.
SISTEMA DE REPRESENTACIÓN DE PRIMITIVAS Y TRANSFORMACIONES:
● Las primitivas y las transformaciones se representan de forma unificada en un
sistema de coordenadas homogéneas.
● Las primitivas se representan con vértices definidos en un vector.
○ Un vector es homogéneo si al menos uno de sus elementos no es cero.
○ Las primitivas pueden ser: un punto, una línea o cualquier polígono irregular
convexo.
● Las transformaciones se representan con matrices. Las más comunes son escala,
rotación y traslación.
RENDERIZADO MVP (model, view, projection): Se tienen los vértices de los polígonos en 𝑣.
● M (model) es la matriz de modelo, que transforma los vértices v, preparando el
escenario.

● V (view) es la matriz de vista, ubica al observador en un determinado punto.
● P (projection) es la matriz de proyección, determina los planos de recorte y la forma
en la que se ve la figura final Los vértices al ser procesados por este mecanismo,
responden a la siguiente operación matricial:
(𝑃×𝑉×𝑀)×𝑣=𝑣 ́
Viewport: determina qué parte de la superficie de dibujo de la ventana estará disponible
para mostrar el gráfico. Sirve si, por ejemplo, se desea emplear la mitad de la ventana para
un canvas de dibujo y el resto para otro fin.
ANIMACIÓN CON MATPLOTLIB: La forma de realizar animaciones con matplotlib es usar
las clases que provee para tal fin. Las animaciones pueden ser iniciadas, pausadas o
incluso almacenadas en un archivo de video a partir del mismo objeto animation. Cada
animación creada debe mantenerse viva mientras se quiera que funcione la animación. De
lo contrario será eliminada por el recolector de basura.

● fig: Figure. Objeto figura utilizado para obtener los eventos necesarios: dibujar,
cambiar de tamaño.
● func: callable. La función que debe llamarse en cada cuadro. Su primer argumento
es el siguiente valor en cuadros. Cualquier otro parámetro debe pasarse con fargs.
● interval: int. Retardo entre cada cuadro en milisegundos.
El módulo Matplotlib es el estándar de facto para visualización científica con Python. Ofrece
una interfaz simple e intuitiva (pyplot) y provee una arquitectura orientada a objetos para
operar sobre figuras.
ANATOMÍA DE UNA FIGURA: Una figura de matplotlib posee una jerarquía de elementos.
Estos se crean sin intervención del usuario.

● Figure (figura): Es un contenedor de
todos los elementos de un gráfico. El elemento
más importante de una figura es ella misma. Se
crea cuando se invoca el método que lleva el
mismo nombre. Al crear una figura se puede
especificar:
○ Tamaño (size).
○ Relación de aspecto (aspect).
○ Color de fondo (facecolor).
● Axes (ejes): Es el segundo elemento más importante de una figura. Corresponde al
área donde serán graficados los datos dentro de la figura. También se denomina
“subplot”. Se puede tener uno o varios ejes en una figura Están limitados por 4
bordes (left, top, right y bottom) denominados “spines”. Cada spine puede ser
decorado con “ticks” y “labels”.
● Axis : Cada borde decorado de los ejes (“spines”) se denominan eje en singular
(axis) Hay un eje horizontal (xaxis) y uno vertical (yaxis).
● Spines : Son las líneas que conectan las marcas (ticks) y que hacen notar los límites
del área de datos de la figura. Pueden colocarse en posiciones arbitrarias y pueden
ser visibles o invisibles.
● Artist : Todo en la figura, incluida Figure, Axes y los objetos Axis, son “artistas”. Esto
incluye objetos de tipo texto, objetos línea 2D, etc. Cuando una figura se renderiza (o
representa gráficamente) todos los artistas pueden dibujar (draw(renderer)) en el
“lienzo” (canvas). Un artista puede estar en un único objeto axes (el área de datos).
● Graphic primitives : Un gráfico siempre está compuesto de artistas (patches), líneas
(lines) y textos (texts).
○ Un “patch” es un artista 2D con color de relleno (facecolor) y color de borde
(edgecolor), enlace. Las áreas pueden ser muy pequeñas o grandes. Tienen
un abanico de formas disponibles: círculos, rectángulos, polígonos, etc.
○ Las líneas pueden tener diferentes grosores y trazados.

○ El texto puede emplear cualquier fuente disponible en el sistema y también
puede utilizar el motor latex para renderizar expresiones matemáticas.
● Zorder : Es una “profundidad virtual” para las primitivas. Indica un orden relativo
atrás/adelante.
● Backends : Existe un backend por defecto cuando se invoca a “plt.show()”. Es una
combinación de 2 elementos:
○ Un motor gráfico (renderizador o render) responsable del dibujo actual.
○ Una interfaz de usuario opcional que le permite interaccionar con la figura.
Matplotlib provee una API en la que el usuario puede controlar la creación de elementos.
“plt.plot(...)” es un atajo que indica a matplotlib que se desea graficar en el último eje que se
haya creado, ya sea en forma explícita o implícita

RENDERIZADO RASTER VS RENDERIZADO VECTORIAL:
SISTEMA DE COORDENADAS: En cada Figura existen 2 sistemas de coordenadas
cartesianas que coexisten. De uno existe una única instancia y del otro puede haber varias
instancias.

● Uno se relaciona a la figura (FC,
Figure-Coordinates).
● Los otros se relacionan con cada gráfico (plot o
axes) individual (DC, Data-Coordinates).
Cada uno de estos sistemas de coordenadas existen en
dos versiones:
● Versión normalizada (NxC).
● Versión nativa (xC).
Es posible convertir coordenadas de un sistema a otro a través de funciones que provee
matplotlib.
MANEJO DE COLOR: Colores en una computadora:
● Modelo de color → tupla de 3 o 4 números (RGB, HSV, HLS, CMYK, etc.)
● Espacio de color → qué colores pueden ser representados (Adobe RGB, sRGB, etc.)
El estándar para computadoras es el espacio de color sRGB ("s" de standard). Este espacio
de color utiliza un modelo de color aditivo basado en el modelo RGB. Para obtener un color
determinado, se deben mezclar diferentes cantidades de luz roja, verde y azul.
Para que matplot seleccione el ciclo de colores:

El mapeo de colores corresponde a la asignación de valores a colores, utilizando un mapa
de colores que define, para cada valor, el color correspondiente. Existen diferentes tipos de
mapas de colores para diferentes casos de uso en función de los datos.

UNIDAD 6: Interfaces de usuario.
Formas básicas de interactuar con el usuario:

ENTORNO DE COMANDOS:
● Ventajas:
○ Provee una interfaz simple basada en texto.
○ Control más preciso de la aplicación.
○ Permite confeccionar scripts para automatizar tareas habituales.
● Desventajas:
○ Suele ser poco intuitivo.
○ Es más difícil de aprender.
HERRAMIENTAS:
● ARGPARSE: Esta herramienta está incorporada en la biblioteca estándar. Sirve para
procesar argumentos que se pasan a un script de Python. El programa define qué
argumentos requiere y argparse determina cómo analizarlos desde el “sys.argv”.

El módulo argparse también genera automáticamente mensajes de ayuda, de uso y
muestra errores cuando los usuarios dan parámetros incorrectos al programa.
● CONSOLE-MENU: Provee funcionalidades a través de la interacción con clases
para:
○ Crear un menú.
○ Agregar un item a un menú.
○ Agregar una función a una llamada entrada de menú.
○ Crear submenús.
TKINTER: Forma parte de la biblioteca estándar. Se basa en una jerarquía de widgets.

INTERFACES GRÁFICAS CON QT: Utiliza el motor de interfaces gráficas de Qt. Puede
basarse en widgets o QML. Hay dos herramientas para interaccionar con Qt, PySide
(pyside2 y pyside6) y PyQt (pyqt4 y pyqt5). Posee un sistema de manejo de eventos muy
potente que puede ser separado en hilos de ejecución, permitiendo una multitarea muy
efectiva.

UNIDAD 7: Algoritmos computacionales y numéricos.
ALGORITMOS COMPUTACIONALES:
FUNCIÓN RECURSIVA: es una función que se llama a sí misma. Se reserva espacio para
almacenar el nuevo conjunto completo de las nuevas variables. Por lo tanto, se utiliza
asignación dinámica -tiempo de ejecución- de memoria.
El registro de activación corresponde a memoria principal asignada dinámicamente para
alojar variables locales asociadas a la ejecución de la llamada a una función.
La pila del sistema corresponde a la parte de la memoria principal utilizada para organizar
de manera jerárquica los diferentes registros de activación conforme las funciones se
invocan. Cuando una función se invoca, su registro de activación se almacena en la pila, y
solo cuando su ejecución finaliza el registro de activación de dicha función se elimina de la
pila. La pila crece y decrece constantemente en tiempo de ejecución.
Por lo tanto, existen variables con valores presentes y pendientes. La profundidad de la
recursión debe ser finita y, además, pequeña.
● Recursividad directa: La función se llama directamente a sí misma.

● Recursividad indirecta: La función llama a otra función y esta a su vez llama a la
primera.
Se suele decir que la recursividad es mucho menos eficiente que las formas iterativas. Esto
no es necesariamente cierto, y depende de la experiencia del programador/a. Una
implementación recursiva que traduce una definición inductiva de forma directa
(ingenuamente), puede no ser la mejor manera de resolver el problema. Esquemas donde
hay solo una llamada a la función recursiva al final de la composición se denominan
recursión de cola y se podrían implementar iterativamente o bien con una implementación
recursiva más astuta.
Existen dos estrategias para resolver problemas con uso de la recursividad:
● DIVIDIR PARA VENCER: La estrategia o paradigma de “dividir para vencer” consiste
en: dividir la entrada en subproblemas, conquistar los subproblemas recursivamente
y combinar las soluciones de los subproblemas en una solución para el problema
original.
● BÚSQUEDA EXHAUSTIVA: Encontrar solución a problemas sin seguir una regla
específica de cálculo, sino por ensayo y error. Es útil donde hay muchas
posibilidades iniciales, pero quedan pocas tras aplicar reglas posteriores.
Descomposición del tanteo: Tareas parciales que se puedan expresar
recursivamente, se explora un número finito de subtareas.
MONTÍCULO BINARIO:
https://docs.google.com/document/d/16BPKwPNMJKsvT_Woh8k3nxoRjNp3Mw393DCibFYr
75w/edit?tab=t.0#heading=h.l0ihr1i19z6g
Estructura de datos. Se puede esquematizar como un árbol, pero para su almacenamiento
se puede usar una lista. La complejidad para agregar es: 𝑂 𝑙𝑜𝑔(𝑛). Hay dos variantes:
● Montículo mínimo (Min Heap).
● Montículo máximo (Max Heap).

La idea es mantener un árbol completo llenando de izquierda a derecha el nivel inferior. Si p
es la posición en la lista, para cada nodo p:

● Descendiente izquierdo: 2p
● Descendiente derecho: 2p + 1
Agregar o insertar un nuevo elemento o ítem al montículo requiere mantener la estructura.
Se agrega el item al final de la lista y luego se realiza una infiltración:

ALGORITMOS NUMÉRICOS:
Los números reales se representan con el formato punto flotante (IEEE 754).
● El exponente se obtiene restando 127 a la representación binaria natural.
● La mantisa (o fracción) se almacena en los 24 bits, el 23 equivale a ½,el 22 a ¼, etc.
El bit 24 no se almacena ya que siempre vale 1, por lo tanto la mantisa está entre 1 y

REPRESENTACIÓN NUMÉRICA: El error de redondeo aparece cuando la representación
es insuficiente para expresar el valor exacto del número real.

Épsilon de máquina : Es un intervalo. Es la diferencia entre 1 y el menor número, mayor
que 1, pero distinguible de 1.

RAÍCES EN ECUACIONES NO LINEALES: Los métodos para encontrar raíces a partir de
una estimación inicial, buscan la raíz (mejoran la precisión) en una ecuación no lineal.
● BISECCIÓN: La idea es encontrar en qué parte del intervalo está la raíz. Error en el

método de la bisección: ε𝑛= |𝑥^12 −𝑛𝑥^0 |
○ Detecta singularidades.
○ Sólo necesita evaluar la función en dos puntos.
○ Es más lento que otros métodos.
○ No usa toda la información de la función.
○ No usa información de las derivadas.
○ No detecta ceros en mín. o máx. locales.
○ No detecta un número par de ceros.
● NEWTON - RAPHSON: Obtención a través de un análisis geométrico. Obtención
analítica a partir de la serie de Taylor. Ecuación de recurrencia: 𝑥𝑛+ 1 =𝑥𝑛− 𝑓𝑓 ́((𝑥𝑥𝑛𝑛))
○ Aplicable a raíces complejas.
○ Necesita una buena aproximación inicial.
○ Problemas con los mín. y máx. locales.
○ Necesita calcular la derivada.
○ Necesita que la función sea continua.
INTERPOLACIÓN: Interpolamos mediante la combinación lineal de funciones conocidas.
La suma, resta, multiplicación, derivada e integral de polinomios dan como resultado otro
polinomio. El polinomio de interpolación es único.
● Método de Lagrange.
● Método de Newton.
FENÓMENO DE RUNGE:

INTERPOLACIÓN POR TRAMOS (splines): Es útil para generar una curva interpolante
suave cuando hay un gran número de datos. Se utilizan polinomios de orden 3 o 4, que
cumplen un conjunto de restricciones de continuidad:
● El punto final (nodo) de un tramo es el inicial del siguiente y su valor es el mismo.
● Las derivadas de 1er y 2do orden tienen el mismo valor en los nodos. Así, no habrá
“quiebres” (o discontinuidades) en las uniones de los tramos.

DIFERENCIACIÓN NUMÉRICA: Se tienen datos o bien una función para derivar
numéricamente. Se puede interpolar con un polinomio y luego derivar.
● Diferenciación usando interpolación:

Construimos el polinomio de Lagrange.
Calculamos coeficientes.
Derivamos polinomio interpolante.
● Diferenciación usando diferencias finitas:
INTEGRACIÓN NUMÉRICA: Usamos estas técnicas cuando tenemos datos y necesitamos
conocer el valor del integral. Cuando integramos numéricamente debemos discretizar las
funciones que forman parte del integrando

● Función de Bessel: 𝐽𝑛(𝑧)=^1 ππ∫ 0 𝑐𝑜𝑠(𝑧 𝑠𝑒𝑛(θ)−𝑛θ) 𝑑θ
● Función error: 𝑒𝑟𝑓(𝑥)=^2 π∫ 0 𝑥𝑒−𝑡^2 𝑑𝑡
NEWTON - COTES: Se interpola los datos o la función a integrar. Calculamos la integral
sobre el polinomio interpolante, por ejemplo:
● Si el polinomio es de orden 1: Regla del Trapecio.

El error está dado por: 𝐸≃− 112 ℎ^3 𝑓 ́ ́(𝑥) , con 𝑥= 𝑥^0 + 2 𝑥^1
● Si el polinomio es de orden 2: ⅓ de Simpson : Interpolamos con orden 2 y
aproximamos la integral.
El error es: 𝐸≃− ℎ 950 𝑓𝑖𝑣(𝑥 1 )
● Si el polinomio es de orden 4: Regla de Milne.
𝑥 0
𝑥 4
∫𝑓(𝑥)𝑑𝑥≈^43 ℎ[ 2 𝑓(𝑥 1 )−𝑓(𝑥 2 )+ 2 𝑓(𝑥 3 )]
Newton - Cotes: fórmulas abierta y cerrada.
● Abierta: no incluye los extremos de integración.
● Cerrada: incluye los extremos de integración.
CUADRATURA DE GAUSS - LEGENDRE: Se utilizan polinomios de Legendre para
resolver. Se debe realizar una transformación de coordenadas.

MÉTODOS DE INTEGRACIÓN DE MONTE CARLO: Se basan en un muestreo aleatorio en
el dominio de la función. Los métodos pueden ser:

● Crudo o Puro.
● Muestreo estratificado.
● Rechazo Aceptancia.
● Muestreo ponderado.
MODELO SIR: