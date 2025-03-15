import asyncio
from googletrans import Translator, constants
from moduls.mod_comfy import *
from PIL import Image, ImageDraw, ImageFont


class ModStory:

    def __init__(self):
        self.data = None

    def generate(self, story):
        """
            Обходим каждую сцену scene:
             - переводим если нет перевода prompt
             - отправляем промпт на генерацию фото
             - ответ от генератора фото сохраняем к сцене
             - возвращаем массив
        :param story:
        :return:
        """
        mod_comfy = ModCOMFY()
        translator = Translator()
        # Запускаем модуль для генерации истории
        # 1. Обходим все из story.scenes и формируем ПРОМПТЫ заменяя вставки []
        for scene in story.get('scenes', []):
            if 'result' not in scene:
                if 'prompt' in scene:
                    translation = scene['prompt']
                else:
                    description = scene['description']
                    for person in story.get('persons', []):
                        person_name = person['name']
                        if person_name in description:
                            description = description.replace(f"[{person_name}]", f"{person_name} ("+person['description']+")")

                    translation = asyncio.run(self.TranslateText(description, src="ru", dest="en"))
                    scene['prompt'] = translation

                # 2. Отправляем ПРОМПТ в генератор картинок
                result = mod_comfy.workflow_start(translation)
                # 3. Сохраняем результат в историю
                scene['result'] = result
                print("Отправили промпт сцены: "+scene['name'])
            else:
                print("Ранее отправляли промпт сцены: " + scene['name'])
        return story

    def check_result(self, story, dir_path):
        """
        Проверяем результаты генерации картинок
        :return:
        """
        mod_comfy = ModCOMFY()
        for scene in story.get('scenes', []):
            if 'photo' not in scene:
                if 'result' in scene:
                    result = scene['result']
                    photo = mod_comfy.run_comfy_get_result(result['prompt_id'], dir_path)
                    if photo != '':
                        scene['photo'] = photo
                else:
                    print(scene['name'] + ": Нет результата отправки сцены на генерацию")
            else:
                print(scene['name'] + ": Уже получили фото")
        return story

    def phototext(self, story, dir_path):
        """
        Создаем для каждой сцены итоговую фотографию
        :param story:
        :param dir_path:
        :return:
        """
        for scene in story.get('scenes', []):
            if 'photo' in scene:
                self.scene_create(scene, dir_path)
            else:
                print(scene['name'] + ": Нет фото")

    def scene_create(self, scene, dir_path):
        """
        Создаем итоговую сцену
        :param scene:
        :param dir_path:
        :return:
        """
        # TODO: дочитать https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
        name = scene["name"]
        text = scene["text"]
        photo_path = dir_path+"/imgs/"+scene["photo"]

        # Открываем изображение
        img = Image.open(photo_path)
        width, height = img.size

        # Создаем объект для рисования
        draw = ImageDraw.Draw(img)

        # Выбираем шрифт и размер
        font = ImageFont.truetype(dir_path+"/fonts/arial.ttf", 30)

        # Получаем размеры текста
        #text_width, text_height = font.getsize(text)
        text_width = font.getlength(text)+20
        text_height = int(font.size * 1.2)

        # Создаем белый полупрозрачный прямоугольник для фона.
        bg_rect = (0, height - text_height - 10, width, height)
        draw.rectangle(bg_rect, fill=(255, 255, 255, 50))

        # Размещаем текст поверх прямоугольника.
        draw.text(((width - text_width) / 2, height - text_height - 5), text, font=font, fill=(0, 0, 0))

        # Сохраним итоговое изображение
        img.save(f"{dir_path}/result/scene_{name}.jpg")


    def load_json(self, filepath):
        with open(filepath) as f:
            self.data = json.load(f)
        return self.data

    def save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def update_value(self, field, value):
        if field not in self.data:
            self.data[field] = {}
        self.data[field]['value'] = value

    async def TranslateText(self, text, src, dest):
        async with Translator() as translator:
            result = await translator.translate(text, src=src, dest=dest)
            return result.text