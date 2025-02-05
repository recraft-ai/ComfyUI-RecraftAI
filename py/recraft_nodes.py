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


STYLE_LIST = [
    '',
    'any',
    'realistic_image',
    'digital_illustration'
]
SUBSTYLE_LIST = [
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
]
IMAGE_SIZE_LIST = [
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
]
SEED_CONFIGURATION = ('INT', {
    'default': 0,
    'min': 0,
    'max': 2147483647,
    'step': 1,
    'display': 'number',
    'lazy': True
})


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


def _make_image_data(tensor, is_mask=False):
    tensor_np = tensor[0].numpy()
    if tensor_np.dtype == numpy.float32 or tensor_np.dtype == numpy.float64:
        tensor_np = (tensor_np * 255).clip(0, 255).astype(numpy.uint8)

    if is_mask:
        # we do not force the mask to be binary, but we do threshold it
        tensor_np = numpy.where(tensor_np >= 127.5, 255, 0).astype(numpy.uint8)

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

    def __process_image(self, operation, image_data, mask_data=None, params=None, random_seed=None):
        if params is None:
            params = {}
        if random_seed is not None:
            params['random_seed'] = random_seed

        with io.BytesIO(image_data) as image_fp:
            if mask_data is None:
                response = requests.post(
                    self._BASE_URL + f'/images/{operation}',
                    headers={'Authorization': f'Bearer {self._token}'},
                    data=params,
                    files={'image': image_fp},
                )
            else:
                with io.BytesIO(mask_data) as mask_fp:
                    response = requests.post(
                        self._BASE_URL + f'/images/{operation}',
                        headers={'Authorization': f'Bearer {self._token}'},
                        data=params,
                        files={'image': image_fp, 'mask': mask_fp},
                    )

        data = response.json()
        
        if 'code' in data:
            raise ValueError(data.get('message', 'empty error message'))

        if 'image' in data:
            return data['image']['url']
        else:
            return data['data'][0]['url']

    def image_to_image(self, image_data, params, random_seed=None):
        return self.__process_image('imageToImage', image_data, params=params, random_seed=random_seed)

    def remove_background(self, image_data, random_seed=None):
        return self.__process_image('removeBackground', image_data, random_seed=random_seed)

    def creative_upscale(self, image_data, random_seed=None):
        return self.__process_image('creativeUpscale', image_data, random_seed=random_seed)

    def crisp_upscale(self, image_data, random_seed=None):
        return self.__process_image('crispUpscale', image_data, random_seed=random_seed)
    
    def replace_background(self, image_data, params, random_seed=None):
        return self.__process_image('replaceBackground', image_data, params=params, random_seed=random_seed)
    
    def inpaint(self, image_data, mask_data, params, random_seed=None):
        return self.__process_image('inpaint', image_data, mask_data=mask_data, params=params, random_seed=random_seed)


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
                'style': (STYLE_LIST,),
                'substyle': (SUBSTYLE_LIST,),
                'image_size': (IMAGE_SIZE_LIST,),
                'model': ([
                    '',
                    'recraftv3',
                    'recraft20b',
                ],),
                'seed': SEED_CONFIGURATION,
            },
        }

    '''
    Generate an image given a text prompt
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


class ImageToImageTransformer:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'image_to_image'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
                'prompt': ('STRING', {'multiline': True, 'default': ''}),
                'strength': ('FLOAT', {'default': 0.5, 'min': 0.0, 'max': 1.0, 'step': 0.01}),
            },
            'optional': {
                'style': (STYLE_LIST,),
                'substyle': (SUBSTYLE_LIST,),
                'seed': SEED_CONFIGURATION,
            },
        }

    '''
    Transform an input image into an output image given a text prompt
    '''
    def image_to_image(self, client, image, prompt, strength, style, substyle, seed):
        if prompt == '':
            raise ValueError('Prompt is required')

        image_url = client.image_to_image(
            _make_image_data(image),
            {
                'prompt': prompt,
                'strength': strength,
                'style': style or None,
                'substyle': substyle or None,
            },
            random_seed=seed,
        )
        print('Image To Image finished', image_url)

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
                'seed': SEED_CONFIGURATION,
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


class CrispUpscaler:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'crisp_upscale'
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
    Crisp upscale of the given image
    '''
    def crisp_upscale(self, client, image, seed):
        image_url = client.crisp_upscale(_make_image_data(image), random_seed=seed)
        print('Crisp upscale finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class CreativeUpscaler:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'creative_upscale'
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
                'seed': SEED_CONFIGURATION,
            },
        }

    '''
    Creative upscale of the given image
    '''
    def creative_upscale(self, client, image, seed):
        image_url = client.creative_upscale(_make_image_data(image), random_seed=seed)
        print('Creative upscale finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class BackgroundReplacer:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'replace_background'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
                'prompt': ('STRING', {'multiline': True, 'default': ''}),
            },
            'optional': {
                'style': (STYLE_LIST,),
                'substyle': (SUBSTYLE_LIST,),
                'seed': SEED_CONFIGURATION,
            },
        }

    '''
    Replace image background based on a given prompt
    '''
    def replace_background(self, client, image, prompt, style, substyle, seed):
        if prompt == '':
            raise ValueError('Prompt is required')

        image_url = client.replace_background(
            _make_image_data(image),
            {
                'prompt': prompt,
                'style': style or None,
                'substyle': substyle or None,
            },
            random_seed=seed,
        )
        print('Replace background finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)


class Inpainter:
    CATEGORY = 'RecraftAI'
    FUNCTION = 'inpaint'
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            'required': {
                'client': ('RECRAFTCLIENT', {'forceInput': True}),
                'image': ('IMAGE', {'forceInput': True}),
                'mask': ('MASK', {'forceInput': True}),
                'prompt': ('STRING', {'multiline': True, 'default': ''}),
            },
            'optional': {
                'style': (STYLE_LIST,),
                'substyle': (SUBSTYLE_LIST,),
                'seed': SEED_CONFIGURATION,
            },
        }

    '''
    Inpaint an image given mask and prompt
    '''
    def inpaint(self, client, image, mask, prompt, style, substyle, seed):
        if prompt == '':
            raise ValueError('Prompt is required')

        image_url = client.inpaint(
            _make_image_data(image),
            _make_image_data(mask, is_mask=True),
            {
                'prompt': prompt,
                'style': style or None,
                'substyle': substyle or None,
            },
            random_seed=seed,
        )
        print('Inpaint finished', image_url)

        image_data = _fetch_image(image_url)
        tensor = _make_tensor(image_data)
        return (tensor,)
