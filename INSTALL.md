### Instalando en local

Para instalar la aplicación en local es necesario seguir los siguientes pasos:

* Instalar los componentes utilizados por la aplicación. Actualmente, la aplicación no es compatible con versiones de Django superiores a 1.6 por usar el argumento [deprecado][4] `mimetype`, por lo que usaremos una versión anterior:

        $ pip install django=="1.5"
        $ pip install Coffin Django Jinja2 Pygments psycopg2 xlwt django_jasmine django_compressor
        
* Borrar base de datos:

        $ dropdb -h localhost presupuestos

* Crear la base de datos:

        $ createdb -h localhost presupuestos

* Copiar `local_settings.py-example` a `local_settings.py` y modificar las credenciales de la base de datos.

* Crear el esquema de la base de datos y cargar los datos básicos:

        $ python manage.py syncdb

        $ python manage.py load_glossary
        $ python manage.py load_entities
        $ python manage.py load_stats
        $ python manage.py load_budget 2014

* Cargar los datos de al menos un par de comarcas:

        $ python manage.py load_budget_data comarca 2014Q1

* Arrancar el servidor

        $ python manage.py runserver

Para más información, consulta la [documentación técnica del proyecto](docs/Documentación Técnica.pdf).

[4]: https://docs.djangoproject.com/en/1.7/internals/deprecation/#deprecation-removed-in-1-7


### Configurando el buscador

Por defecto la aplicación usa el método estándar de búsqueda de texto de Postgres. Es posible crear métodos de búsqueda adaptados a un idioma concreto, de forma que -por ejemplo- Postgres ignore los acentos a la hora de buscar resultados. Si deseamos configurar la búsqueda para funcionar en español, creamos primero una nueva configuración de búsqueda, como se explica en la [documentación de Postgres](http://www.postgresql.org/docs/9.1/static/textsearch-configuration.html):

    $ psql presupuestos_dev

    > CREATE EXTENSION unaccent;

    > CREATE TEXT SEARCH CONFIGURATION unaccent_spa ( COPY = pg_catalog.spanish );

    > ALTER TEXT SEARCH CONFIGURATION unaccent_spa
        ALTER MAPPING FOR hword, hword_part, word
        WITH unaccent, spanish_stem;

Mientras hacemos pruebas en `psql` podemos configurar el método de búsqueda por defecto:

    > SET default_text_search_config = 'unaccent_spa';

Pero para usarlo de manera regular debemos configurar la aplicación, vía `local_settings.py`:

    'SEARCH_CONFIG': 'unaccent_spa'


### Adaptando el aspecto visual

La aplicación soporta el concepto de 'themes' capaces de modificar el aspecto visual de la web: tanto recursos estáticos (imágenes, hojas de estilo...) como las plantillas que generan el contenido de la web. El directorio `theme-dvmi` es un buen ejemplo de cómo debe organizarse el contenido de un theme.

El theme a usar se configura mediante la variable `THEME`, que es referenciada en diversos puntos de `settings.py` para instalar los directorios del theme (plantillas y recursos estáticos) justo antes de los de la aplicación principal.
