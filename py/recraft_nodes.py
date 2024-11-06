import configparser
import io
import os

from PIL import Image
import numpy
import torch
import requests


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
    with requests.get(url, stream=True) as req:
        return req.content


def _make_tensor(image_data):
    with Image.open(io.BytesIO(image_data)) as image:
        image_np = numpy.array(image).astype(numpy.float32) / 255.0
        tensor = torch.from_numpy(image_np)[None,]
        return tensor


def _make_image_data(tensor):
    tensor_np = tensor[0].numpy()
    if tensor_np.dtype == numpy.float32 or tensor_np.dtype == numpy.float64:
        tensor_np = (tensor_np * 255).clip(0, 255).astype(numpy.uint8)

    image = Image.fromarray(tensor_np)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    return image_data


class RecraftClient:
    _BASE_URL = 'https://external.api.recraft.ai/v1'

    def __init__(self, token):
        self._token = token

    def generate_image(self, prompt, model=None, image_size=None, style=None, substyle=None, random_seed=None):
        response = requests.post(
            self._BASE_URL + '/images/generations',
            headers={'Authorization': f'Bearer {self._token}'},
            json={
                'prompt': prompt,
                'model': model or None,
                'style': style or None,
                'substyle': substyle or None,
                'size': image_size or None,
                'random_seed': random_seed or None,
            }
        )
        data = response.json()
        if 'code' in data:
            raise ValueError(data.get('message', 'empty error message'))
        return data['data'][0]['url']

    def __process_image(self, operation, image_data, random_seed=None):
        with io.BytesIO(image_data) as fp:
            response = requests.post(
                self._BASE_URL + f'/images/{operation}',
                headers={'Authorization': f'Bearer {self._token}'},
                json={'random_seed': random_seed or None},
                files={'file': fp},
            )

        data = response.json()
        if 'code' in data:
            raise ValueError(data.get('message', 'empty error message'))
        return data['image']['url']

    def remove_background(self, image_data, random_seed=None):
        return self.__process_image('removeBackground', image_data, random_seed=random_seed)

    def generative_upscale(self, image_data, random_seed=None):
        return self.__process_image('generativeUpscale', image_data, random_seed=random_seed)

    def clarity_upscale(self, image_data, random_seed=None):
        return self.__process_image('clarityUpscale', image_data, random_seed=random_seed)


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
    RETURN_NAMES = ('image',)
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
                    '1024x1280',
                    '1024x1365',
                    '1024x1434',
                    '1024x1536',
                    '1024x1707',
                    '1024x1820',
                    '1024x2048',
                    '1280x1024',
                    '1365x1024',
                    '1434x1024',
                    '1536x1024',
                    '1707x1024',
                    '1820x1024',
                    '2048x1024',
                ],),
                'model': ([
                    '',
                    'recraftv3',
                    'recraft20b',
                ],),
                'seed': ('INT', {
                    'default': 0,
                    'min': 0,
                    'max': 2147483647,
                    'step': 1,
                    'display': 'number',
                    'lazy': True
                }),
            },
        }

    '''
    Generate an image given a prompt
    '''
    def generate(self, client, prompt, style, substyle, image_size, model, seed):
        if prompt == '':
            raise ValueError('Prompt is required')

        image_url = client.generate_image(
            prompt,
            image_size=image_size,
            style=style,
            substyle=substyle,
            model=model,
            random_seed=seed,
        )
        print('Generated image', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class BackgroundRemover:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'remove_background'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
            },
            'optional': {
                'seed': ('INT', {
                    'default': 0,
                    'min': 0,
                    'max': 2147483647,
                    'step': 1,
                    'display': 'number',
                }),
            },
        }

    '''
    Remove background of the given image
    '''
    def remove_background(self, client, image, seed):
        image_url = client.remove_background(_make_image_data(image), random_seed=seed)
        print('Removed background', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class ClarityUpscaler:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'clarity_upscale'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
            },
            'optional': {
                'seed': ('INT', {
                    'default': 0,
                    'min': 0,
                    'max': 2147483647,
                    'step': 1,
                    'display': 'number',
                }),
            },
        }

    '''
    Clarity upscale of the given image
    '''
    def clarity_upscale(self, client, image, seed):
        image_url = client.clarity_upscale(_make_image_data(image), random_seed=seed)
        print('Clarity upscale finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class GenerativeUpscaler:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'generative_upscale'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
            },
            'optional': {
                'seed': ('INT', {
                    'default': 0,
                    'min': 0,
                    'max': 2147483647,
                    'step': 1,
                    'display': 'number',
                }),
            },
        }

    '''
    Generative upscale of the given image
    '''
    def generative_upscale(self, client, image, seed):
        image_url = client.generative_upscale(_make_image_data(image), random_seed=seed)
        print('Generative upscale finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)
