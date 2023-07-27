import discord
import requests
import asyncio
import json
from datetime import datetime
import os

# Configura el token de tu bot de Discord
TOKEN = 

# URL de la API 
API_URL = 'https://api.bluelytics.com.ar/v2/latest'

# Nombre del archivo para almacenar los IDs de mensajes
MESSAGE_IDS_FILE = 'message_ids.json'

# Función para obtener los datos de la API 
def obtener_datos_economicos():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print('Error al obtener los datos.')
        return None

# Función para cargar los IDs de mensajes desde el archivo JSON
def cargar_ids_de_mensajes():
    try:
        with open(MESSAGE_IDS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Función para guardar los IDs de mensajes en el archivo JSON
def guardar_ids_de_mensajes(message_ids):
    with open(MESSAGE_IDS_FILE, 'w') as file:
        json.dump(message_ids, file)

# Función para enviar datos en formato Embed a los canales especificados
async def enviar_datos_periodicamente():
    await bot.wait_until_ready()

    message_ids = cargar_ids_de_mensajes()

    while not bot.is_closed():
        datos = obtener_datos_economicos()

        if datos:
            for channel_id, message_id in message_ids.items():
                channel = bot.get_channel(int(channel_id))
                if channel:
                    # Datos para dolar blue
                    blue_data = datos.get('blue', {})
                    blue_embed = discord.Embed(title='Datos del dolar 🦥 (Blue)', color=discord.Color.blue())
                    blue_embed.add_field(name='Compra', value=blue_data.get('value_buy', 'No disponible'))
                    blue_embed.add_field(name='Promedio', value=blue_data.get('value_avg', 'No disponible'))
                    blue_embed.add_field(name='Venta', value=blue_data.get('value_sell', 'No disponible'))
                    blue_embed.set_footer(text=f'Última actualización: {datetime.now()}')

                    # Datos para oficial
                    oficial_data = datos.get('oficial', {})
                    oficial_embed = discord.Embed(title='Datos del dolar 🦥 (Oficial)', color=discord.Color.blue())
                    oficial_embed.add_field(name='Compra', value=oficial_data.get('value_buy', 'No disponible'))
                    oficial_embed.add_field(name='Promedio', value=oficial_data.get('value_avg', 'No disponible'))
                    oficial_embed.add_field(name='Venta', value=oficial_data.get('value_sell', 'No disponible'))
                    oficial_embed.set_footer(text=f'Última actualización: {datetime.now()}')

                    try:
                        if message_id is None or any(id is None for id in message_id):
                            mensaje_blue = await channel.send(embed=blue_embed)
                            mensaje_oficial = await channel.send(embed=oficial_embed)
                            message_ids[str(channel.id)] = [mensaje_blue.id, mensaje_oficial.id]
                            print(f'Datos enviados a {channel}.')

                        else:
                            mensaje_blue_id, mensaje_oficial_id = message_id
                            mensaje_blue = await channel.fetch_message(mensaje_blue_id)
                            mensaje_oficial = await channel.fetch_message(mensaje_oficial_id)
                            await mensaje_blue.edit(embed=blue_embed)
                            await mensaje_oficial.edit(embed=oficial_embed)
                            print(f'Embeds actualizados en {channel}.')

                    except discord.HTTPException as e:
                        print(f'Error al enviar o actualizar el mensaje en {channel}: {e}')

            guardar_ids_de_mensajes(message_ids)
            # Espera 45 minutos antes de enviar la siguiente actualización
            await asyncio.sleep(2 * 60)

# Crea y ejecuta el bot
bot = discord.Client()
bot.loop.create_task(enviar_datos_periodicamente())
bot.run(TOKEN)
