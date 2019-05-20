import os, requests, time
from xml.etree import ElementTree
from playsound import playsound

try: input = raw_input
except NameError: pass

access_token = ""

def get_token():
    global access_token
    fetch_token_url = "https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        'Ocp-Apim-Subscription-Key': "4c80a4fb678f438eb068f0e22fbf076e"
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)

def save_audio(text):
    timestr = time.strftime("%Y%m%d-%H%M")
    base_url = 'https://westus.tts.speech.microsoft.com/'
    path = 'cognitiveservices/v1'
    constructed_url = base_url + path
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
        'User-Agent': 'YOUR_RESOURCE_NAME'
    }
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
    voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)')
    voice.text = text
    body = ElementTree.tostring(xml_body)

    response = requests.post(constructed_url, headers=headers, data=body)
    print("working: "+text)
    if response.status_code == 200:
        filename = 'sample-' + timestr + '.wav'
        with open(filename, 'wb') as audio:
            audio.write(response.content)
        playsound(filename)
        print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")

# get_token()
# save_audio("hey dhruv")
# get_token()
# save_audio("hey mayank")
