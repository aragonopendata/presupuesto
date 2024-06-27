#!/bin/bash

# Configuration
SOURCE_DATA=/data/ckan_ficheros/opendata/general
APP=/apps/presupuestos-aragon
CACHE=/tmp/presupuesto

# Development
# SOURCE_DATA=/Users/David/src/presupuestos-aragon/source_data
# APP=/Users/David/src/presupuestos-aragon
# CACHE=/Users/David/src/presupuestos-aragon/cache

cd $APP

# Convenient variables
COUNTY_DATA=$APP/theme-aragon/data/comarca/latest
TOWN_DATA=$APP/theme-aragon/data/municipio/latest

# Make sure target folders exist
if test ! -d $COUNTY_DATA; then mkdir $COUNTY_DATA; fi
if test ! -d $TOWN_DATA; then mkdir $TOWN_DATA; fi

# Check if more recent data exists, for counties
echo "Comprobando los datos de comarcas..."
if test ! -e $COUNTY_DATA/clasificacion_economica.csv -o $SOURCE_DATA/clasificacion-economica-comarcas-2014-en-adelante.csv -nt $COUNTY_DATA/clasificacion_economica.csv 
then
  echo "Hay datos más recientes. Copiando ficheros..."
  cp $SOURCE_DATA/clasificacion-funcional-comarcas-2014-en-adelante.csv $COUNTY_DATA/clasificacion_funcional.csv
  cp $SOURCE_DATA/clasificacion-economica-comarcas-2014-en-adelante.csv $COUNTY_DATA/clasificacion_economica.csv
  cp $SOURCE_DATA/noxbrl-comarcas-2014-en-adelante.csv $COUNTY_DATA/no_xbrl.csv

  echo "Cargando datos de comarcas..."
  python manage.py load_budget_data comarca latest

  echo "Borrando la caché..."
  rm -rf $CACHE/*

else
  echo "No hay datos recientes, nada que hacer."

fi

echo
echo

# Check if more recent data exists, for towns
echo "Comprobando los datos de municipios..."
if test ! -e $TOWN_DATA/clasificacion_economica.csv -o $SOURCE_DATA/clasificacion-economica-municipios-2014-en-adelante.csv -nt $TOWN_DATA/clasificacion_economica.csv 
then
  echo "Hay datos más recientes. Copiando ficheros..."
  cp $SOURCE_DATA/clasificacion-funcional-municipios-2014-en-adelante.csv $TOWN_DATA/clasificacion_funcional.csv
  cp $SOURCE_DATA/clasificacion-economica-municipios-2014-en-adelante.csv $TOWN_DATA/clasificacion_economica.csv
  cp $SOURCE_DATA/noxbrl-municipios-2014-en-adelante.csv $TOWN_DATA/no_xbrl.csv

  echo "Cargando datos de municipios..."
  python manage.py load_budget_data municipio latest

  echo "Borrando la caché..."
  rm -rf $CACHE/*

else
  echo "No hay datos recientes, nada que hacer."

fi
