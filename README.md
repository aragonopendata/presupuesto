
<img src="http://presupuesto.aragon.es/static/assets/logo-gobierno-aragon.png" height="28px" /><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>![Logo Aragón Open Data](aragon/static/assets/logoAragonOpenData.png)

##Presupuestos de Aragón

Este repositorio contiene el código de la aplicación de visualización de [Presupuestos del Gobierno de Aragón][1], desarrollada como parte del proyecto [Aragón Open Data][3].

### Introducción
El objetivo de la primera fase del proyecto consistió en ofrecer una visualización de los Presupuestos Generales de Aragón suficientemente intuitiva como para ser comprendida por personas sin experiencia previa en política presupuestaria, pero a la vez suficientemente detallada para permitir a aquellas personas interesadas y expertas en este asunto profundizar más de una manera ágil y efectiva. Así, esa primera fase muestra la realidad del presupuesto en su conjunto, cubriendo tanto el lado de los ingresos como el de los gastos, y tanto las cantidades presupuestadas como las finalmente ejecutadas (cuando la información esté disponible). El objetivo de la segunda fase ha sido extender la transparencia de los presupuestos de la comunidad autónoma a niveles inferiores: municipios y comarcas.

Las principales funcionalidades de la aplicación son:

 * Visualización de gastos e ingresos presupuestados, de forma jerárquica y según las cuatro clasificaciones usadas en los presupuestos: funcional (para qué se gasta), económica (en qué se gasta, o cómo se ingresa), financiación (origen y tipo de los fondos) y orgánica/institucional (quién gasta/ingresa).

 * Mostrar la información de los programas presupuestarios al máximo nivel de desglose existente, el nivel de partida.

 * Mostrar la evolución de los presupuestos desde 2006.

 * Permitir la búsqueda de texto libre en el conjunto de los presupuestos para encontrar cualquier dato de forma sencilla

Para más información, consulta las memorias del proyecto para las fases [uno](docs/Memoria Fase 1.pdf) y [dos](docs/Memoria Fase 2.pdf).

[1]: http://presupuesto.aragon.es
[3]: http://opendata.aragon.es/

### Instalando en local

Para instalar la aplicación en local es necesario seguir los siguientes pasos:

* Crear `project/settings.py` a partir del fichero `project/settings.py-example` suministrado, actualizando los detalles de la base de datos a utilizar.

* Instalar los componentes utilizados por la aplicación:

        $ pip install Coffin Django Jinja2 Pygments psycopg2 xlwt
        
* Borrar base de datos:
        $ dropdb -h localhost presupuestos

* Crear la base de datos:

        $ createdb -h localhost presupuestos
        $ python manage.py syncdb

* Cargar los datos básicos:

        $ python manage.py load_glossary
        $ python manage.py load_entities
        $ python manage.py load_stats
        $ python manage.py load_budget 2014

* Cargar los datos de al menos un par de comarcas:

        $ python manage.py load_budget_data comarca 2014Q1

* Arrancar el servidor

        $ python manage.py runserver

Para más información, consulta la [documentación técnica del proyecto](docs/Documentación Técnica.pdf).

###Licencia

El código de esta aplicación está publicado bajo la licencia abierta [EUPL 1.1][2] (European Union Public License 1.1), lo que significa que puedes reutilizarlo, modificarlo y adaptarlo a tus necesidades de forma totalmente libre. Eso sí, nos encantaría que, si utilizas el código, añadieras un reconocimiento a Open Data Aragón en tu proyecto e incluyeras nuestro logo.

![Logo Aragón Open Data](aragon/static/assets/logoAragonOpenData.png)

[2]: https://joinup.ec.europa.eu/software/page/eupl