# Systemas 

- Debian 12
- Python 3.11.2
- pip 23.0.1 
- systemd 252 (252.22-1~deb12u1)

____#######################################____

# Install lib
 - pip install -r requirements.txt

___######################################___
# Systemd Config

 - Asigne  la ruta de la lib Scrapy en el archivo rates.timer

 - Asigne la ruta de  archivo extraccion.py en el archivo rates.timer

 - Ubicacion del servicio
  * Coloque el archivo rates.time en la ruta
    path = /etc/systemd/system/
    (En debian esta es la ruta, en otro S.O. puede variar)
 
 - Ejecute en el promt la los siguientes comandos:
   * sudo systemctl enable extraccion.timer
   * sudo systemctl start extraccion.timer
  
  
_____###################################_____
# Test
 - En caso de que lo quiera probar,
 luego de instalar las dependencias
 ejecute el comando:
    
    scrapy runspider extraccion.py
