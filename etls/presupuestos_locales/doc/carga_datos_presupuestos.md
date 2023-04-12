# Carga de datos de presupuestos

## Descripción
La aplicación de presupuestos de Aragón utiliza unos scripts llamados “loaders” para cargar los datos de presupuestos en la base de datos.   
Estos loaders son ejecutados mediante comandos desde consola, por lo que primero será necesario colocar los ficheros en sus directorios correspondientes.

## Tareas
1. Creación de los directorios  
        a. Se deberá crear en la siguiente ruta, un directorio que tenga por nombre el año del presupuesto de los municipios a cargar:  
`/data/apps/presupuesto/theme-aragon/data/municipio/`  
        b. Se deberá crear en la siguiente ruta, un directorio que tenga por nombre el año del presupuesto de las comarcas a cargar:    
`/data/apps/presupuesto/theme-aragon/data/comarca/`  

2. Subida de ficheros de carga 
        a. Subir a cada uno de los directorios creados anteriormente los ficheros correspondientes a municipio y comarca respectivamente:  
            i. `clasificacion_economica.csv`  
            ii. `clasificacion_funcional.csv`  
            iii. `no_xbrl.csv`  
   > Los ficheros proceden de la ejecución de los jobs Talend situados en la máquina de salto.  
   > Consultar credenciales de las máquinas en: '[AOD]_Passwords.xlsx', pestaña 'Otros', 'MÁQUINA DE SALTO PRESUPUESTOS (1 y 2)'.   
3. Carga de presupuestos de municipios y comarcas  
        a. Ir a la ruta de la aplicación:  
        ```
        cd /data/apps/presupuesto/
        ```  
        b. Ejecutar las siguientes instrucciones:  
        ```
        python manage.py load_budget_data municipio [año]
        ```  
        y  
        ```
        python manage.py load_budget_data comarca [año]
        ```  
   > Donde `[año]` corresponde al nombre del directorio que creamos para municipios.  
        
4. Borrar caché  
        Tal vez sea necesario borrar el caché de la página para que se actualicen los resultados:  
        ```
        rm -r /tmp/presupuestos/
        ```

