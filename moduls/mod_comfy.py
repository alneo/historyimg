import requests
from dotenv import load_dotenv
import os
import json
import uuid
import websocket
import urllib.parse

#https://comfyui-guides.runcomfy.com/ultimate-comfyui-how-tos-a-runcomfy-guide/working-with-comfyui-backend-api
# 1. Вызываем workflow_start('Текст промпта')
# 2. Результат вызова сохраянем для получения фото
# 3. Скачиваем фото run_comfy_get_result(result.get('prompt_id'))
# print(result)
# {'prompt_id': '9530cfe1-86fc-4897-bbf6-9ee8e081daf5', 'number': 41, 'node_errors': {}}
# print('run_comfy_check_status:')
# run_comfy_check_status()
# print('run_comfy_get_result:' + result.get('prompt_id'))
# run_comfy_get_result(result.get('prompt_id'))

class ModCOMFY:

    def __init__(self):
        load_dotenv()
        self.COMFY_WS = os.getenv('COMFY_WS')
        self.COMFY_URL = os.getenv('COMFY_URL')
        self.COMFY_API_KEY = os.getenv('COMFY_API_KEY')
        self.WORKFLOW_ID = os.getenv('WORKFLOW_ID')
        self.CLIENT_ID = str(uuid.uuid4())
        self.WORKFLOW_JSON = 'workflows/flux_dev_checkpoint_example.json'

        self.workflow_json = None

    def workflow_start(self, prompt_text):
        json = self.load_json(self.WORKFLOW_JSON)
        json['6']['inputs']['text'] = prompt_text
        result = self.run_comfy_json(json)
        return result

    def load_json(self, filepath):
        with open(filepath) as f:
            self.workflow_json = json.load(f)
        return self.workflow_json


    def run_comfy_json(self, data):
        """
        Запускает workflow в Comfy AI из JSON файла.
        Возвращает {
            'prompt_id': '9530cfe1-86fc-4897-bbf6-9ee8e081daf5',
            'number': 41,
            'node_errors': {}
        }
        """

        url = f"{self.COMFY_URL}/prompt"
        headers = {
            "Authorization": f"Bearer {self.COMFY_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = {
            "prompt": data,
            "client_id": self.CLIENT_ID
        }

        try:
            response = requests.post(url, json=prompt, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Ошибка при запуске json: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса run_comfy_json: {e}")
            return None


    def run_comfy_check_status(self):
        try:
            ws = websocket.WebSocket()
            #print("ws://{}/ws?clientId={}".format(COMFY_WS, CLIENT_ID))
            ws.connect("ws://{}/ws?clientId={}".format(self.COMFY_WS, self.CLIENT_ID))
            while True:
                out = ws.recv()
                print(out)
                #{
                # "type": "crystools.monitor",
                # "data": {
                #   "cpu_utilization": -1,
                #   "ram_total": -1,
                #   "ram_used": -1,
                #   "ram_used_percent": -1,
                #   "hdd_total": -1,
                #   "hdd_used": -1,
                #   "hdd_used_percent": -1,
                #   "device_type": "cuda",
                #   "gpus": [
                #       {
                #           "gpu_utilization": -1,
                #           "gpu_temperature": -1,
                #           "vram_total": -1,
                #           "vram_used": -1,
                #           "vram_used_percent": -1
                #       }
                #   ]
                # }
                #}

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса run_comfy_check_status: {e}")
            return None


    def run_comfy_get_result(self, prompt_id, dir="./storys/first"):
        """
        Получение результатов работы по prompt_id и сохранение в dir
        :param prompt_id:
        :param dir:
        :return:
        """
        url = f"{self.COMFY_URL}"+"/history/{}".format(prompt_id)
        headers = {}
        photo = ""
        try:
            response = requests.get(url, headers=headers)
            data = response.json().get(prompt_id)

            # video_result = data.get('outputs').get('90').get('gifs')[0]
            # raw_video = get_video(video_result.get('filename'), video_result.get('subfolder'), video_result.get('format'))
            #
            # with open(video_result.get('filename'), 'wb') as f:
            #     f.write(raw_video)
            for node_id, node_output in data.get('outputs').items():
                if 'images' in node_output:
                    for image in node_output['images']:
                        raw_image = self.run_comfy_get_image(image.get('filename'), image.get('subfolder'), image.get('type'))
                        photo = image.get('filename')
                        with open(f"{dir}/{image.get('filename')}", "wb") as f:
                            f.write(raw_image)

                if 'gifs' in node_output:
                    for video in node_output['gifs']:
                        raw_video = self.run_comfy_get_video(video.get('filename'), video.get('subfolder'), video.get('format'))
                        with open(f"{dir}/{video.get('filename')}", "wb") as f:
                            f.write(raw_video)

                if 'openpose_json' in node_output:
                    pass
            return photo
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса run_comfy_get_result: {e}")
            return None

    def run_comfy_get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_value = urllib.parse.urlencode(data)
        url = f"{self.COMFY_URL}"+"/api/view?{}".format(url_value)
        response = requests.get(url)
        return response.content


    def run_comfy_get_video(self, filename, subfolder, _format):
        data = {"filename": filename, "subfolder": subfolder, "format": _format}
        url_value = urllib.parse.urlencode(data)
        url = f"{self.COMFY_URL}"+"/view?{}".format(url_value)
        response = requests.get(url)
        return response.content