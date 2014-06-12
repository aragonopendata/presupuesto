### Instalando en local

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
