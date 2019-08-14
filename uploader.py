import cloudinary
import cloudinary.uploader
import yaml

CLOUD_NAME = yaml.load(open('endpoints.yml'), Loader=yaml.FullLoader)['CLOUD_NAME']
API_KEY = yaml.load(open('endpoints.yml'), Loader=yaml.FullLoader)['API_KEY']
API_SECRET = yaml.load(open('endpoints.yml'), Loader=yaml.FullLoader)['API_SECRET']

loudinary.config(
    cloud_name = CLOUD_NAME,  
    api_key = API_KEY,  
    api_secret = API_SECRET
)

def upload(file, method):
    res = cloudinary.uploader.upload(file, folder=method)
    return res['url']