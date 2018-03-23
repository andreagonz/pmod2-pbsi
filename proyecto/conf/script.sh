#!/bin/bash

OPTS=`getopt -o dCgbupircUIePmxfzMv:EA --long datos,cron,usuario-grupos,usuarios-bloqueados,usuarios-activos,procesos,interfaces,puertos,conexiones-establecidas,conexiones-udp,iptables,estadisticas,particiones,memoria,cpu,archivos-sockets,gzip:,vhosts,mods,apache-errorlog,apache-accesslog -- "$@"`
eval set -- "$OPTS"

if [ $? != 0 ] ; then echo "Error" >&2 ; exit 1 ; fi

while true; do
    case "$1" in
        -d | --datos)
            echo Distribución: `cat /etc/issue | cut -f1-3 -d' '` ; #Distribucion.
            echo Arquitectura: `uname -m`;                          #Arquitectura.
            echo Nombre de equipo: `uname -n`;                      #Nombre del equipo.
            echo Nombre de dominio: `domainname` ;                  #Dominio.
            shift
            ;;
        -C | --cron)
            echo -e "Tareas de cron:\n"
            echo "Sistema:"
            grep "^[^#;]" /etc/crontab 
            for user in $(cut -f1 -d: /etc/passwd); do
                ct=`sudo crontab -u $user -l | grep "^[^#;]"`
                if [ ! -z "$ct" ]; then
                    echo -e "\nUsuario $user:"
                    sudo crontab -u $user -l | grep "^[^#;]"
                fi
            done
            shift ;;
        -g | --usuario-grupos)
            echo -e "Usuario: Grupos\n"
            cut -d":" -f1 /etc/passwd | xargs groups | sed 's/ : /: /'
            shift ;;
        -b | --usuarios-bloqueados)
            echo -e "Usuarios bloqueados\n"
            cut -d":" -f1 /etc/passwd | while read usuario; do
                l=`sudo passwd -S $usuario | cut -d' ' -f2`
                if [ $l == 'L' ] || [ $l == 'LK' ]; then
                    echo $usuario
                fi
            done
            shift
            ;;
        -u | --usuarios-activos)
            echo -e "Usuarios activos\n"
            w -s
            shift ;;
        -p | --procesos)
            ps -Ao pid,uid,uname,%cpu,%mem,cmd
            shift ;;
        -i | --interfaces)
            echo -e "Interfaz IP/Máscara Gateway\n"
            ip -o -4 addr show | tr -s "\t" " " | cut -f2,4 -d" " | while read line; do
                int=`echo $line | cut -d' ' -f1`
                line=`echo $line | tr '/' '|'`
                route -n | grep $int | tr -s ' ' | cut -d ' ' -f2 | sed "s/\(.*\)/$line \1/" | tr '|' '/'
            done
            shift
            ;;
        -r | --puertos )
            echo -e "Puertos en escucha\n"
            sudo netstat -tupan | grep LISTEN
            shift
            ;;
        -c | --conexiones-establecidas)
            echo -e "Conexiones TCP establecidas\n"
            sudo netstat -tupan | grep ESTABLISHED
            shift
            ;;
        -U | --conexiones-udp)
            echo -e "Conexiones UDP\n"
            sudo netstat -upan
            shift
            ;;
        -I | --iptables)
            echo -e "Reglas de iptables\n"
            echo -e "\nFILTER:\n"
            sudo iptables -t filter -vL            
            echo -e "\n\nNAT:\n"
            sudo iptables -t nat -vL           
            echo -e "\n\nMANGLE:\n"
            sudo iptables -t mangle -vL
            echo -e "\n\nRAW:\n"
            sudo iptables -t raw -vL
            echo -e "\n\nSECURITY:\n"
            sudo iptables -t security -vL
            shift
            ;;
        -e | --estadisticas)
            echo -e "Estadísticas\n"
            netstat -s;
            shift ;;                                    
        -P | --particiones)
            echo -e "Particiones\n"
            df -h
            shift ;;
        -m | --memoria)
            echo -e "Memoria RAM\n"
            free -h
            shift
            ;;
        -x | --cpu)
            echo -e "CPU\n"
            mpstat
            n=$(mpstat | grep %idle | tr -s ' ' | tr ' ' '\n' | awk '/%idle/ {print NR}')
            libre=$(mpstat | grep all | tr -s ' ' | cut -d' ' -f$n)
            usado=$(perl -E "print(100 - $libre)")
            echo -e "\nTotal usado: $usado%"
            echo "Total libre: $libre%"
            shift
            ;;
        -f | --archivos-sockets)
            sudo lsof
            shift ;;
        -z | --gzip)
            archivo=`sed 's/\([^[:alnum:]/._-]\)/\\\1/g' <<< "$2"`
            sudo gzip -cd $archivo | tac
            shift
            ;;
        -M | --mods)
            apache2ctl -M
            shift
            ;;
        -v | --vhosts)
            apache2ctl -D DUMP_VHOSTS
            shift
            ;;
        -E | --apache-errorlog)
            servroot=`apache2ctl -S | grep ServerRoot | cut -d' ' -f2 | tr -d '"'`
            errorlog=`apache2ctl -S | grep ErrorLog | cut -d' ' -f3 | tr -d '"'`
            source $servroot/envvars            
            ls -d $servroot/sites-enabled/* | while read linea; do
                echo $errorlog
                e=`grep ErrorLog $linea | egrep -v "[\s]*#.*"`
                if [ ! -z "$e" ]; then
                    e=$(echo $e | sed "s|\${APACHE_LOG_DIR}|$APACHE_LOG_DIR|g" | tr '\t' ' ' | tr -s ' ' | cut -d' ' -f2)
                    if [[ $e == /* ]]; then
                        echo $e
                    else
                        echo $servroot/$e
                    fi                    
                fi
            done | sort | uniq
            shift
            ;;
        -A | --apache-accesslog)
            servroot=`apachectl -S | grep ServerRoot | cut -d' ' -f2 | tr -d '"'`
            source $servroot/envvars
            ls -d $servroot/sites-enabled/* | while read linea; do
                echo $APACHE_LOG_DIR/access.log
                e=`grep "CustomLog" $linea | egrep -v "[\s]*#.*"`
                if [ ! -z "$e" ]; then
                    e=$(echo $e | sed "s|\${APACHE_LOG_DIR}|$APACHE_LOG_DIR|g" | tr '\t' ' ' | tr -s ' ' | cut -d' ' -f2)
                    if [[ $e == /* ]]; then
                        echo $e
                    else
                        echo $servroot/$e
                    fi
                fi
            done | sort | uniq
            shift
            ;;        
        -- ) shift; break ;;
        * ) break ;;
    esac
done
