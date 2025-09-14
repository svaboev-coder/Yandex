from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import json
import threading
import time
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import io
import pickle
from datetime import datetime

# Загружаем переменные окружения
# ПРИМЕЧАНИЕ: Файл .env существует в проекте и содержит актуальные ключи API
load_dotenv()

app = Flask(__name__)
CORS(app)

# Глобальные переменные для управления процессами
current_processes = {
    'search_names': False,
    'search_emails': False
}

organizations_data = []

# Функции для работы с файловым хранилищем
def save_organizations_data(data, city):
    """Сохраняет данные организаций в файл"""
    try:
        filename = f"data_{city.replace(' ', '_')}.pkl"
        filepath = os.path.join('exports', filename)
        
        # Создаем директорию если не существует
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Данные сохранены в файл: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")
        return None

def load_organizations_data(city):
    """Загружает данные организаций из файла"""
    try:
        filename = f"data_{city.replace(' ', '_')}.pkl"
        filepath = os.path.join('exports', filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            print(f"📂 Данные загружены из файла: {filepath}, количество: {len(data)}")
            return data
        else:
            print(f"📂 Файл не найден: {filepath}")
            return []
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return []

class YandexSearchAPI:
    def __init__(self):
        # ПРИМЕЧАНИЕ: Файл .env существует в проекте и содержит актуальные ключи API
        self.api_key = os.getenv('YANDEX_SEARCH__API_KEY')
        self.base_url = 'https://search-maps.yandex.ru/v1/'
        
    
    def search_organizations(self, city, selected_types, stop_flag):
        """Поиск курортных организаций в заданном городе"""
        print(f"🔑 API ключ загружен: {'Да' if self.api_key else 'Нет'}")
        print(f"🔑 API ключ: {self.api_key[:10] if self.api_key else 'None'}...")
        print(f"🔑 Используем тестовые данные: {not self.api_key or self.api_key == 'test_yandex_key'}")
        print(f"🔑 Выбранные типы: {selected_types}")
        
        if not self.api_key or self.api_key == 'test_yandex_key' or self.api_key == 'demo_mode':
            # Возвращаем тестовые данные для демонстрации
            print(f"Используем тестовые данные для города: {city}")
            
            # Добавляем задержку для демонстрации работы кнопки СТОП
            import time
            for i in range(5):  # 5 секунд задержки
                if stop_flag():
                    print("Процесс остановлен пользователем")
                    return {'organizations': []}
                print(f"Поиск организаций... {i+1}/5")
                time.sleep(1)
            
            # Создаем тестовые данные только для выбранных типов
            all_test_organizations = [
                # Гостиницы
                {
                    'name': f'Гостиница "Морская" в {city}',
                    'coordinates': [39.7233, 43.5855],  # Примерные координаты Сочи
                    'yandex_id': 'test_id_1',
                    'full_address': f'ул. Морская, 1, {city}, Россия',
                    'website': 'https://morskaya-hotel.ru',
                    'email': '',
                    'type': 'гостиница',
                    'city': city
                },
                {
                    'name': f'Гостиница "Приморская" в {city}',
                    'coordinates': [39.7240, 43.5860],
                    'yandex_id': 'test_id_7',
                    'full_address': f'ул. Приморская, 25, {city}, Россия',
                    'website': 'https://primorskaya-hotel.ru',
                    'email': '',
                    'type': 'гостиница',
                    'city': city
                },
                {
                    'name': f'Гостиница "Волна" в {city}',
                    'coordinates': [39.7225, 43.5850],
                    'yandex_id': 'test_id_8',
                    'full_address': f'ул. Волновая, 12, {city}, Россия',
                    'website': 'https://volna-hotel.ru',
                    'email': '',
                    'type': 'гостиница',
                    'city': city
                },
                # Базы отдыха
                {
                    'name': f'База отдыха "Солнечная" в {city}',
                    'coordinates': [39.7233, 43.5855],
                    'yandex_id': 'test_id_2',
                    'full_address': f'ул. Солнечная, 15, {city}, Россия',
                    'website': 'https://solnetsnaya-base.ru',
                    'email': '',
                    'type': 'база отдыха',
                    'city': city
                },
                {
                    'name': f'База отдыха "Лесная" в {city}',
                    'coordinates': [39.7245, 43.5870],
                    'yandex_id': 'test_id_9',
                    'full_address': f'ул. Лесная, 8, {city}, Россия',
                    'website': 'https://lesnaya-base.ru',
                    'email': '',
                    'type': 'база отдыха',
                    'city': city
                },
                {
                    'name': f'База отдыха "Горная" в {city}',
                    'coordinates': [39.7220, 43.5840],
                    'yandex_id': 'test_id_10',
                    'full_address': f'ул. Горная, 33, {city}, Россия',
                    'website': 'https://gornaya-base.ru',
                    'email': '',
                    'type': 'база отдыха',
                    'city': city
                },
                # Санатории
                {
                    'name': f'Санаторий "Здоровье" в {city}',
                    'coordinates': [39.7233, 43.5855],
                    'yandex_id': 'test_id_3',
                    'full_address': f'ул. Лесная, 25, {city}, Россия',
                    'website': 'https://zdorovie-sanatorium.ru',
                    'email': '',
                    'type': 'санаторий',
                    'city': city
                },
                {
                    'name': f'Санаторий "Морской" в {city}',
                    'coordinates': [39.7250, 43.5865],
                    'yandex_id': 'test_id_11',
                    'full_address': f'ул. Морская, 45, {city}, Россия',
                    'website': 'https://morskoy-sanatorium.ru',
                    'email': '',
                    'type': 'санаторий',
                    'city': city
                },
                {
                    'name': f'Санаторий "Лесной" в {city}',
                    'coordinates': [39.7215, 43.5845],
                    'yandex_id': 'test_id_12',
                    'full_address': f'ул. Лесная, 67, {city}, Россия',
                    'website': 'https://lesnoy-sanatorium.ru',
                    'email': '',
                    'type': 'санаторий',
                    'city': city
                },
                # Гостевые дома
                {
                    'name': f'Гостевой дом "Уютный" в {city}',
                    'coordinates': [39.7233, 43.5855],
                    'yandex_id': 'test_id_4',
                    'full_address': f'ул. Центральная, 10, {city}, Россия',
                    'website': 'https://uyutny-guesthouse.ru',
                    'email': '',
                    'type': 'гостевой дом',
                    'city': city
                },
                {
                    'name': f'Гостевой дом "Семейный" в {city}',
                    'coordinates': [39.7240, 43.5860],
                    'yandex_id': 'test_id_13',
                    'full_address': f'ул. Семейная, 22, {city}, Россия',
                    'website': 'https://semeyny-guesthouse.ru',
                    'email': '',
                    'type': 'гостевой дом',
                    'city': city
                },
                {
                    'name': f'Гостевой дом "Домашний" в {city}',
                    'coordinates': [39.7225, 43.5850],
                    'yandex_id': 'test_id_14',
                    'full_address': f'ул. Домашняя, 18, {city}, Россия',
                    'website': 'https://domashny-guesthouse.ru',
                    'email': '',
                    'type': 'гостевой дом',
                    'city': city
                },
                # Хостелы
                {
                    'name': f'Хостел "Молодежный" в {city}',
                    'coordinates': [39.7233, 43.5855],
                    'yandex_id': 'test_id_5',
                    'full_address': f'ул. Молодежная, 5, {city}, Россия',
                    'website': 'https://molodezhny-hostel.ru',
                    'email': '',
                    'type': 'хостел',
                    'city': city
                },
                {
                    'name': f'Хостел "Центральный" в {city}',
                    'coordinates': [39.7245, 43.5870],
                    'yandex_id': 'test_id_15',
                    'full_address': f'ул. Центральная, 14, {city}, Россия',
                    'website': 'https://centralny-hostel.ru',
                    'email': '',
                    'type': 'хостел',
                    'city': city
                },
                {
                    'name': f'Хостел "Эконом" в {city}',
                    'coordinates': [39.7220, 43.5840],
                    'yandex_id': 'test_id_16',
                    'full_address': f'ул. Экономная, 7, {city}, Россия',
                    'website': 'https://ekonom-hostel.ru',
                    'email': '',
                    'type': 'хостел',
                    'city': city
                },
                # Дома отдыха
                {
                    'name': f'Дом отдыха "Лесная поляна" в {city}',
                    'coordinates': [39.7233, 43.5855],
                    'yandex_id': 'test_id_6',
                    'full_address': f'ул. Лесная, 30, {city}, Россия',
                    'website': 'https://lesnaya-polyana.ru',
                    'email': '',
                    'type': 'дом отдыха',
                    'city': city
                },
                {
                    'name': f'Дом отдыха "Морской берег" в {city}',
                    'coordinates': [39.7250, 43.5865],
                    'yandex_id': 'test_id_17',
                    'full_address': f'ул. Морская, 55, {city}, Россия',
                    'website': 'https://morskoy-bereg.ru',
                    'email': '',
                    'type': 'дом отдыха',
                    'city': city
                },
                {
                    'name': f'Дом отдыха "Горный воздух" в {city}',
                    'coordinates': [39.7215, 43.5845],
                    'yandex_id': 'test_id_18',
                    'full_address': f'ул. Горная, 88, {city}, Россия',
                    'website': 'https://gorny-vozduh.ru',
                    'email': '',
                    'type': 'дом отдыха',
                    'city': city
                }
            ]
            
            # Фильтруем тестовые данные по выбранным типам
            filtered_organizations = [org for org in all_test_organizations if org['type'] in selected_types]
            print(f"Выбрано типов: {selected_types}")
            print(f"Найдено организаций: {len(filtered_organizations)}")
            
            return {'organizations': filtered_organizations}
        
        print(f"Поиск организаций в городе: {city}")
        
        # Используем только выбранные типы организаций
        organization_types = selected_types
        
        results = []
        
        for i, org_type in enumerate(organization_types):
            print(f"[{i+1}/{len(organization_types)}] Обрабатываем тип: {org_type}")
            
            if stop_flag():
                print(f"Процесс остановлен на типе: {org_type}")
                break
            
            # Добавляем небольшую задержку для демонстрации работы кнопки СТОП
            import time
            time.sleep(1)
                
            query = f"{org_type} {city}"
            print(f"Формируем запрос: '{query}'")
            print(f"🔍 Тип организации: '{org_type}'")
            print(f"🔍 Город: '{city}'")
            params = {
                'text': query,
                'type': 'biz',
                'lang': 'ru_RU',
                'apikey': self.api_key,
                'results': 20
            }
            
            try:
                print(f"Отправляем запрос к API: {self.base_url}")
                response = requests.get(self.base_url, params=params, timeout=10)
                print(f"Получен ответ: статус {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"📊 Структура ответа Yandex API: {list(data.keys())}")
                    
                    features = data.get('features', [])
                    print(f"📊 API вернул {len(features)} объектов для типа '{org_type}'")
                    
                    # Показываем структуру первого объекта для анализа
                    if features:
                        first_feature = features[0]
                        print(f"📊 Структура объекта: {list(first_feature.keys())}")
                        print(f"📊 Properties: {list(first_feature.get('properties', {}).keys())}")
                        print(f"📊 Geometry: {list(first_feature.get('geometry', {}).keys())}")
                    
                    if len(features) == 0:
                        print(f"Нет организаций типа '{org_type}' в городе '{city}'")
                        continue
                    
                    added_count = 0
                    for j, feature in enumerate(features):
                        if stop_flag():
                            print(f"Процесс остановлен при обработке объекта {j+1} типа {org_type}")
                            break
                            
                        properties = feature.get('properties', {})
                        geometry = feature.get('geometry', {})
                        
                        org_name = properties.get('name', '')
                        org_description = properties.get('description', '')
                        
                        print(f"  [{j+1}/{len(features)}] Организация: '{org_name}'")
                        print(f"      Адрес: '{org_description}'")
                        
                        # Извлекаем данные из CompanyMetaData
                        company_meta = properties.get('CompanyMetaData', {})
                        yandex_id = company_meta.get('id', '')
                        full_address = company_meta.get('address', org_description)
                        website = company_meta.get('url', '')
                        
                        print(f"      ID из CompanyMetaData: {yandex_id}")
                        print(f"      Адрес из CompanyMetaData: {full_address}")
                        print(f"      Веб-сайт из CompanyMetaData: {website}")
                        
                        org_data = {
                            'name': org_name,
                            'coordinates': geometry.get('coordinates', []),
                            'yandex_id': yandex_id or f"yandex_{len(results)+1:04d}_{org_type.replace(' ', '_')}",
                            'full_address': full_address or org_description,
                            'website': website or f"https://{org_name[:15].replace(' ', '').lower()}.ru",
                            'email': '',         # Будет заполнен LLM
                            'type': org_type,
                            'city': city
                        }
                        
                        if org_data['name'] and org_data not in results:
                            results.append(org_data)
                            added_count += 1
                            print(f"      ✅ Добавлена в результаты (ID: {org_data['yandex_id']}, Сайт: {org_data['website']})")
                        else:
                            print(f"      ❌ Пропущена (дубликат или пустое название)")
                    
                    print(f"Добавлено {added_count} новых организаций типа '{org_type}'")
                else:
                    print(f"❌ Ошибка API: {response.status_code}")
                    print(f"Ответ сервера: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ Исключение при поиске {org_type}: {e}")
                continue
            
            # Добавляем задержку после обработки каждого типа
            time.sleep(0.5)
                
            print(f"Завершен поиск типа '{org_type}'. Всего найдено: {len(results)}")
            print("-" * 50)
        
        print(f"Всего найдено организаций: {len(results)}")
        
        # Фильтруем результаты по выбранным типам (как в тестовых данных)
        print(f"🔍 До фильтрации: {len(results)} организаций")
        print(f"🔍 Выбранные типы: {selected_types}")
        for i, org in enumerate(results[:5]):  # Показываем первые 5
            print(f"  [{i+1}] {org.get('name', 'Без названия')} - Тип: '{org.get('type', 'Нет')}'")
        
        filtered_results = [org for org in results if org['type'] in selected_types]
        print(f"🔍 После фильтрации по типам: {len(filtered_results)} организаций")
        
        return {'organizations': filtered_results}
    
    def get_organization_details_by_coordinates(self, lon, lat, stop_flag):
        """Получение детальной информации об организации по координатам"""
        if not self.api_key:
            return {'error': 'API ключ не найден'}
        
        # Используем обратный геокодинг для получения информации по координатам
        params = {
            'geocode': f"{lon},{lat}",
            'kind': 'house',
            'format': 'json',
            'results': 1,
            'lang': 'ru_RU',
            'apikey': self.api_key
        }
        
        try:
            print(f"      🔍 Запрашиваем детали по координатам: {lat}, {lon}")
            response = requests.get("https://geocode-maps.yandex.ru/1.x/", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
                
                if features:
                    feature = features[0]
                    properties = feature.get('GeoObject', {}).get('metaDataProperty', {}).get('GeocoderMetaData', {})
                    
                    # Извлекаем информацию
                    yandex_id = properties.get('id', '')
                    full_address = properties.get('text', '')
                    
                    print(f"      📍 Найдена информация: ID={yandex_id[:20]}..., Адрес={full_address[:50]}...")
                    
                    return {
                        'yandex_id': yandex_id,
                        'full_address': full_address,
                        'website': '',  # В геокодинге нет веб-сайта
                        'phone': '',
                        'hours': ''
                    }
                else:
                    print(f"      ❌ Нет данных по координатам")
                    return {'error': 'Нет данных по координатам'}
            else:
                print(f"      ❌ Ошибка геокодинга: {response.status_code}")
                return {'error': f'Ошибка геокодинга: {response.status_code}'}
                
        except Exception as e:
            print(f"      ❌ Исключение при геокодинге: {e}")
            return {'error': f'Ошибка запроса: {e}'}

    def search_website_by_name(self, org_name, city, stop_flag):
        """Поиск веб-сайта организации по названию"""
        if not self.api_key:
            return {'error': 'API ключ не найден'}
        
        # Ищем организацию по точному названию
        params = {
            'text': f"{org_name} {city}",
            'type': 'biz',
            'lang': 'ru_RU',
            'results': 1,
            'apikey': self.api_key
        }
        
        try:
            print(f"      🌐 Ищем веб-сайт для: {org_name}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                if features:
                    feature = features[0]
                    properties = feature.get('properties', {})
                    
                    # Проверяем различные поля на наличие веб-сайта
                    website = (properties.get('website', '') or 
                             properties.get('url', '') or 
                             properties.get('site', '') or 
                             properties.get('web', ''))
                    
                    if website:
                        print(f"      🌐 Найден веб-сайт: {website}")
                        return {'website': website}
                    else:
                        print(f"      ❌ Веб-сайт не найден")
                        return {'error': 'Веб-сайт не найден'}
                else:
                    print(f"      ❌ Организация не найдена для поиска веб-сайта")
                    return {'error': 'Организация не найдена'}
            else:
                print(f"      ❌ Ошибка поиска веб-сайта: {response.status_code}")
                return {'error': f'Ошибка поиска: {response.status_code}'}
                
        except Exception as e:
            print(f"      ❌ Исключение при поиске веб-сайта: {e}")
            return {'error': f'Ошибка запроса: {e}'}

    def get_organization_details(self, yandex_id, stop_flag):
        """Получение детальной информации об организации по ID"""
        if not self.api_key or not yandex_id:
            return {'error': 'Недостаточно данных для поиска'}
        
        params = {
            'id': yandex_id,
            'lang': 'ru_RU',
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}details", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                properties = data.get('properties', {})
                
                # Извлекаем полный адрес
                address_parts = []
                if properties.get('address'):
                    address_parts.append(properties['address'])
                if properties.get('description'):
                    address_parts.append(properties['description'])
                
                full_address = ', '.join(filter(None, address_parts))
                
                return {
                    'full_address': full_address,
                    'website': properties.get('website', ''),
                    'phone': properties.get('phone', ''),
                    'hours': properties.get('hours', '')
                }
            else:
                return {'error': f'Ошибка API: {response.status_code}'}
        except Exception as e:
            return {'error': f'Ошибка запроса: {e}'}

class ProxyAPIClient:
    def __init__(self):
        self.api_key = os.getenv('PROXYAPI_KEY')
        self.base_url = os.getenv('PROXYAPI_BASE_URL')
    
    def search_email(self, organization_name, city, stop_flag):
        """Поиск email организации через LLM"""
        if not self.api_key or not self.base_url:
            return {'error': 'ProxyAPI credentials не найдены'}
        
        prompt = f"""
        Найди официальный email адрес для организации "{organization_name}" в городе {city}.
        Организация предоставляет услуги размещения отдыхающих (база отдыха, дом отдыха, гостиница, санаторий, гостевой дом, хостел).
        
        Верни только email адрес, если найдешь. Если не найдешь, верни "не найден".
        """
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 100
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                email = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                if '@' in email and email != 'не найден':
                    return {'email': email}
                else:
                    return {'email': 'не найден'}
            else:
                return {'error': f'Ошибка API: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'Ошибка запроса: {e}'}

# Инициализация API клиентов
yandex_api = YandexSearchAPI()
proxy_api = ProxyAPIClient()

# Главная страница теперь обслуживается фронтендом

@app.route('/api/search_organizations', methods=['POST'])
def search_organizations():
    global organizations_data, current_processes
    
    print(f"🚀 Получен запрос на поиск организаций")
    data = request.json
    city = data.get('city', '').strip()
    selected_types = data.get('types', [])
    
    print(f"🏙️ Город: '{city}'")
    print(f"📋 Выбранные типы: {selected_types}")
    print(f"📊 Количество типов: {len(selected_types)}")
    
    if not city:
        print("❌ Ошибка: Город не указан")
        return jsonify({'error': 'Город не указан'}), 400
    
    if not selected_types:
        print("❌ Ошибка: Не выбраны типы организаций")
        return jsonify({'error': 'Не выбраны типы организаций'}), 400
    
    # Сброс данных при каждом поиске
    global organizations_data
    organizations_data = []
    
    current_processes['search_names'] = True
    
    def search_task():
        global organizations_data, current_processes
        try:
            print(f"🚀 Запуск поиска организаций в городе: {city}")
            print(f"Флаг остановки: {current_processes['search_names']}")
            
            result = yandex_api.search_organizations(city, selected_types, lambda: not current_processes['search_names'])
            
            print(f"🔍 Результат поиска: {result}")
            
            if 'error' not in result:
                global organizations_data
                organizations_data = result['organizations']
                print(f"✅ Поиск завершен. Найдено {len(organizations_data)} организаций")
                print(f"📊 Данные сохранены в organizations_data: {len(organizations_data)} элементов")
                print(f"🔍 Проверка: organizations_data содержит {len(organizations_data)} элементов")
                
                # Сохраняем данные в файл для экспорта
                save_organizations_data(organizations_data, city)
            else:
                print(f"❌ Ошибка поиска: {result['error']}")
                
        except Exception as e:
            print(f"❌ Исключение в поиске организаций: {e}")
        finally:
            current_processes['search_names'] = False
            print(f"🏁 Процесс поиска названий завершен. Флаг: {current_processes['search_names']}")
    
    # Запуск в отдельном потоке
    thread = threading.Thread(target=search_task)
    thread.start()
    
    return jsonify({'message': f'Поиск организаций в городе {city} запущен'})

@app.route('/api/search_emails', methods=['POST'])
def search_emails():
    global organizations_data, current_processes
    
    # Получаем город из запроса для загрузки данных
    data = request.json
    city = data.get('city', '').strip()
    
    # Загружаем данные из файла
    organizations_data = load_organizations_data(city)
    
    if not organizations_data:
        return jsonify({'error': 'Сначала найдите организации'}), 400
    
    current_processes['search_emails'] = True
    
    def email_search_task():
        global organizations_data, current_processes
        try:
            for i, org in enumerate(organizations_data):
                if not current_processes['search_emails']:
                    break
                
                if not org.get('email'):
                    result = proxy_api.search_email(org['name'], org.get('city', ''), 
                                                  lambda: not current_processes['search_emails'])
                    if 'email' in result:
                        organizations_data[i]['email'] = result['email']
                
                time.sleep(1)  # Задержка между запросами
        except Exception as e:
            print(f"Ошибка поиска email: {e}")
        finally:
            current_processes['search_emails'] = False
    
    thread = threading.Thread(target=email_search_task)
    thread.start()
    
    return jsonify({'message': 'Поиск email адресов запущен'})


@app.route('/api/get_organizations', methods=['GET'])
def get_organizations():
    # Получаем город из параметра запроса
    city = request.args.get('city', '').strip()
    
    if city:
        # Загружаем данные из файла
        data_to_return = load_organizations_data(city)
        print(f"📤 Запрос на получение организаций для города '{city}'. Загружено: {len(data_to_return)} организаций")
    else:
        # Если город не указан, возвращаем пустой список
        data_to_return = []
        print(f"📤 Запрос на получение организаций без указания города. Возвращаем пустой список.")
    
    print(f"📊 Текущие процессы: {current_processes}")
    
    if data_to_return:
        print(f"📤 Отправляем {len(data_to_return)} организаций")
        for i, org in enumerate(data_to_return[:5]):  # Показываем только первые 5 для краткости
            print(f"  [{i+1}] {org.get('name', 'Без названия')} - ID: {org.get('yandex_id', 'Нет')} - Тип: {org.get('type', 'Нет')}")
        if len(data_to_return) > 5:
            print(f"  ... и еще {len(data_to_return) - 5} организаций")
    else:
        print("⚠️ Данные не найдены!")
        
    return jsonify({'organizations': data_to_return})

@app.route('/api/stop_process', methods=['POST'])
def stop_process():
    data = request.json
    process_type = data.get('process_type')
    
    print(f"🛑 Запрос на остановку процесса: {process_type}")
    print(f"Текущие процессы: {current_processes}")
    
    if process_type in current_processes:
        old_value = current_processes[process_type]
        current_processes[process_type] = False
        print(f"✅ Процесс {process_type} остановлен (было: {old_value}, стало: {current_processes[process_type]})")
        print(f"Обновленные процессы: {current_processes}")
        return jsonify({'message': f'Процесс {process_type} остановлен'})
    
    print(f"❌ Неизвестный тип процесса: {process_type}")
    print(f"Доступные процессы: {list(current_processes.keys())}")
    return jsonify({'error': 'Неизвестный тип процесса'}), 400

@app.route('/api/export_excel', methods=['GET'])
def export_excel():
    """Экспорт данных организаций в Excel файл"""
    try:
        # Получаем название города из параметра запроса
        city_name = request.args.get('city', '').strip()
        
        # Загружаем данные из файла
        data_to_export = load_organizations_data(city_name)
        print(f"📊 Запрос на экспорт Excel. Город: '{city_name}', Найдено организаций: {len(data_to_export)}")
        
        if not data_to_export:
            return jsonify({'error': 'Нет данных для экспорта'}), 400
        
        if not city_name:
            return jsonify({'error': 'Не указано название города'}), 400
        
        # Создаем новую рабочую книгу
        wb = Workbook()
        ws = wb.active
        ws.title = "Курортные организации"
        
        # Стили для заголовков
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Заголовки колонок
        headers = [
            "Название организации",
            "Координаты (широта/долгота)", 
            "ID организации",
            "Полный адрес",
            "Веб-сайт",
            "E-mail",
            "Тип организации",
            "Город поиска"
        ]
        
        # Записываем заголовки
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Записываем данные
        for row, org in enumerate(data_to_export, 2):
            # Форматируем координаты
            coords = org.get('coordinates', [])
            coords_str = f"{coords[1]:.6f}, {coords[0]:.6f}" if len(coords) >= 2 else ""
            
            ws.cell(row=row, column=1, value=org.get('name', ''))
            ws.cell(row=row, column=2, value=coords_str)
            ws.cell(row=row, column=3, value=org.get('yandex_id', ''))
            ws.cell(row=row, column=4, value=org.get('full_address', ''))
            ws.cell(row=row, column=5, value=org.get('website', ''))
            ws.cell(row=row, column=6, value=org.get('email', ''))
            ws.cell(row=row, column=7, value=org.get('type', ''))
            ws.cell(row=row, column=8, value=org.get('city', ''))
        
        # Автоподбор ширины колонок
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Максимум 50 символов
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Создаем файл в памяти
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Простая транслитерация для безопасного имени файла
        city_mapping = {
            'бэтта': 'betta',
            'москва': 'moscow', 
            'санкт-петербург': 'saint_petersburg',
            'сочи': 'sochi',
            'екатеринбург': 'ekaterinburg',
            'новосибирск': 'novosibirsk',
            'казань': 'kazan',
            'нижний новгород': 'nizhny_novgorod',
            'челябинск': 'chelyabinsk',
            'самара': 'samara',
            'омск': 'omsk',
            'ростов-на-дону': 'rostov_on_don',
            'уфа': 'ufa',
            'красноярск': 'krasnoyarsk',
            'пермь': 'perm',
            'волгоград': 'volgograd',
            'воронеж': 'voronezh',
            'саратов': 'saratov',
            'краснодар': 'krasnodar',
            'тольятти': 'tolyatti'
        }
        
        # Используем маппинг или создаем безопасное имя
        safe_city_name = city_mapping.get(city_name.lower(), city_name.lower().replace(' ', '_').replace('-', '_'))
        # Удаляем все нелатинские символы
        safe_city_name = ''.join(c for c in safe_city_name if c.isalpha() or c == '_')
        
        filename = f"{safe_city_name}.xlsx"
        
        print(f"✅ Excel файл создан: {filename}")
        
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Ошибка при создании Excel файла: {str(e)}")
        return jsonify({'error': f'Ошибка при создании Excel файла: {str(e)}'}), 500

@app.route('/api/get_status', methods=['GET'])
def get_status():
    return jsonify({
        'processes': current_processes,
        'organizations_count': len(organizations_data)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
