from dotenv import load_dotenv
import os
from moduls.mod_story import ModStory

fstory_dir = 'storys/first'
fstory_path = fstory_dir+'/story.json'
mod_story = ModStory()
# 1. Загружаем файл истории
story = mod_story.load_json('storys/first/story.json')
# 2. Отправляем каждую сцену на генерацию фоток
story = mod_story.generate(story)
# 3. Сохраняем обновленный массив в файл
mod_story.save_json(fstory_path, story)
# 4. Проверяем готовность фото TODO надо проверить готова ли фото в цикле?
story = mod_story.check_result(story, fstory_dir+'/imgs')
# 5. Сохраняем обновленный массив в файл
mod_story.save_json(fstory_path, story)
# 6. Создаем фотоколлаж
mod_story.phototext(story, fstory_dir)






# print('run_comfy_json:')
# result = run_comfy_json(json)
# #print(result)
# #{'prompt_id': '9530cfe1-86fc-4897-bbf6-9ee8e081daf5', 'number': 41, 'node_errors': {}}
# #print('run_comfy_check_status:')
# #run_comfy_check_status()
# print('run_comfy_get_result:'+result.get('prompt_id'))
# run_comfy_get_result(result.get('prompt_id'))
