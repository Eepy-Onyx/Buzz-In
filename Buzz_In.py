
#Script to run a buzz-in poll on Twitch and OBS, make sure to set the OBS_Websockets_Password to your password found in your OBS settings and TwitchAuth to your Twitch Authentication Token (With at least permissions to send messages) before running this script.

import os
import time
import socket
import random
import obsws_python as obs
import select

buzzedin=[]
seconds=int(input("How long do you want this to last?\n"))
topic=input("\nWhat's the topic of this vote?\n")
print("\nPoll running!\n\n")
# === Twitch IRC Settings ===
if True:
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = 'Eepy_Onyx'
    token = os.environ['TwitchAuth']
    channel = '#eepy_onyx'

    # === Twitch IRC Connection ===
sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
sock.send(f"JOIN {channel}\n".encode('utf-8'))
print("[Twitch] Connected and joined channel")

#OBS settings
host="localhost"
port=4455
password=os.environ["OBS_Websocket_Password"]
#Connecting
ws = obs.ReqClient(host=host,port=port,password=password)
print("[OBS] Connected to OBS Webhooks")

#Functions
def set_text_source_content(scene_name: str, source_name: str, new_text: str):
    """
    Updates the text of a text (GDI+) source in OBS, specifying the scene.

    Args:
        scene_name (str): The name of the scene containing the text source.
        source_name (str): The name of the text source in the scene.
        new_text (str): The new text to display in the text source.
    """
    try:
        # Get list of scene items for the specified scene
        item_list = ws.get_scene_item_list(scene_name)

        # Find the source item in the scene
        scene_item = None
        for item in item_list.scene_items:
            if item['sourceName'] == source_name:
                scene_item = item
                break

        if not scene_item:
            print(f"[OBS] Source '{source_name}' not found in scene '{scene_name}'.")
            return

        # Get current settings for the text source
        settings = ws.get_input_settings(source_name).input_settings

        # Update the 'text' field
        settings["text"] = new_text

        # Apply the updated settings to the specific source
        ws.set_input_settings(source_name, settings, overlay=False)

        print(f"[OBS] Text source '{source_name}' in scene '{scene_name}' updated with new text.")

    except Exception as e:
        print(f"[ERROR] Failed to update text source: {e}")


def toggle_visibility(scene_name: str, source_names: list, visible: bool):
    """
    Toggle visibility of multiple sources in a given scene.

    Args:
    scene_name (str): Name of the scene containing the sources.
    source_names (list): List of source (scene item) names to toggle.
    visible (bool): True to show, False to hide.
    """
    try:
        # Get list of scene items in the scene
        item_list = ws.get_scene_item_list(scene_name)

        # Debug: print the type and content of the item_list
        print(f"[DEBUG] Type of item_list: {type(item_list)}")
        print(f"[DEBUG] item_list contents: {item_list}")

        # Iterate over each source name in the list
        for source_name in source_names:
            # Find the scene item ID for the source
            scene_item_id = None
            for item in item_list.scene_items:  # item_list.scene_items should be a list of dicts
                if item['sourceName'] == source_name:  # Dictionary-style access
                    scene_item_id = item['sceneItemId']  # Dictionary-style access
                    break

            if scene_item_id is None:
                print(f"[OBS] Source '{source_name}' not found in scene '{scene_name}'.")
                continue  # Skip to the next source if not found

            # Set visibility for this source
            ws.set_scene_item_enabled(scene_name, scene_item_id, visible)  # Correct argument order
            print(f"[OBS] Set visibility of '{source_name}' to {visible} in scene '{scene_name}'.")

    except Exception as e:
        print(f"[ERROR] Failed to toggle visibility: {e}")
name=['Test']

def send_message(message):
    sock.send(f"PRIVMSG #eepy_onyx : {message}\r\n".encode('utf-8'))


#Body
set_text_source_content('Gam','Test',f'!buzzin active for\n{seconds} seconds!')
toggle_visibility('Gam',name,True)
send_message(f"Buzz in active for {seconds} seconds! Do '!buzzin' followed by your message for a chance to be chosen! Topic: {topic}!")

start_time=time.time()
while (time.time()-start_time) < seconds:
    ready,_,_= select.select([sock],[],[],1)
    if ready:
        response = sock.recv(2048).decode('utf-8', errors='ignore')

        if response.startswith('PING'):
            sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))

        elif "PRIVMSG" in response:
            username = response.split('!', 1)[0][1:]
            message = response.split('PRIVMSG', 1)[1].split(':', 1)[1].strip() 
            if '!buzzin ' in message.lower():
                wo=(f"{username} buzzed in with '{message}'")
                buzzedin.append(wo)
                print(wo)


send_message("!buzzin disabled! Picking a random answer!")     
toggle_visibility('Gam',name,False)

if buzzedin!=[]:
    ans=random.choice(buzzedin)
    print(ans)
else:
    print("\n\n\nNo one buzzed in!")
i=input('\nPress enter to close, type anything to view all answers\n')

if i!='':
    print('\n\n\n',buzzedin)
    input('Press enter to close')