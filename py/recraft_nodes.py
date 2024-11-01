import configparser
import io
import os

import PIL
import numpy
import torch
import requests
import torchvision.transforms.functional as transforms

import folder_paths


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config_path = os.path.join(parent_dir, 'config.ini')


config = configparser.ConfigParser()
config.read(config_path)


try:
    recraft_api_token = config['API']['RECRAFT_API_TOKEN']
    if recraft_api_token != '':
        os.environ['RECRAFT_API_TOKEN'] = recraft_api_token
    else:
        print('Warning: RECRAFT_API_TOKEN is empty')
except KeyError:
    print('Error: unable to find RECRAFT_API_TOKEN in config.ini')


def _fetch_image(url):
    return requests.get(url, stream=True).content


def _make_tensor(image_data):
    image = PIL.Image.open(io.BytesIO(image_data))
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    image_np = numpy.array(image).astype(numpy.float32) / 255.0
    return torch.from_numpy(image_np)[None,]


class RecraftClient:
    _BASE_URL = 'https://external.api.recraft.ai/v1'

    def __init__(self, token):
        self._token = token

    def generate_image(self, prompt, model=None, image_size=None, style=None, substyle=None):
        response = requests.post(
            self._BASE_URL + '/images/generations',
            headers={'Authorization': f'Bearer {self._token}'},
            json={
                'prompt': prompt,
                'model': model or None,
                'style': style or None,
                'substyle': substyle or None,
                'image_size': image_size or None,
            }
        )
        data = response.json()
        if 'code' in data:
            raise ValueError(data.get('message', 'empty error message'))
        return data['data'][0]['url']


class Client:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'make'
    RETURN_TYPES = ('RECRAFTCLIENT',)
    RETURN_NAMES = ('client',)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'api_token': (
                    'STRING',
                    {
                        'default': '',
                    },
                )
            },
        }

    '''
    Create a RecraftAI client with the given API token
    '''
    def make(self, api_token):
        api_token = api_token if api_token != '' else os.environ.get('RECRAFT_API_TOKEN', '')
        if api_token == '':
            raise ValueError('API token is required')

        client = RecraftClient(api_token)
        return (client,)


class ImageGenerator:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'generate'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image_url',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'prompt': ('STRING', {'multiline': True, 'default': ''}),
            },
            'optional': {
                'style': (['', 'any', 'realistic_image', 'digital_illustration'],),
                'substyle': ([
                    '',
                    'b_and_w',
                    'hard_flash',
                    'hdr',
                    'natural_light',
                    'studio_portrait',
                    'enterprise',
                    'motion_blur',
                    'pixel_art',
                    'hand_drawn',
                    'grain',
                    'infantile_sketch',
                    '2d_art_poster',
                    'handmade_3d',
                    'hand_drawn_outline',
                    'engraving_color',
                    '2d_art_poster_2',
                ],),
                'image_size': ([
                    '',
                    '1024x1024',
                    '1365x1024',
                    '1024x1365',
                    '1536x1024',
                    '1024x1536',
                    '1820x1024',
                    '1024x1820',
                    '1024x2048',
                    '2048x1024',
                    '1434x1024',
                    '1024x1434',
                    '1024x1280',
                    '1280x1024',
                    '1024x1707',
                    '1707x1024',
                ],),
                'model': ([
                    '',
                    'recraftv3',
                    'recraft20b',
                ],),
            },
        }


    '''
    Generate an image given a prompt
    '''
    def generate(self, client, prompt, style, substyle, image_size, model):
        if prompt == '':
            raise ValueError('Prompt is required')

        image_url = client.generate_image(
            prompt,
            image_size=image_size,
            style=style,
            substyle=substyle,
        )
        image_data = _fetch_image(image_url)
        return (_make_tensor(image_data),)
