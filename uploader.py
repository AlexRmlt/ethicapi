import cloudinary
import cloudinary.uploader

CLOUD_NAME = 'ethicreport'
API_KEY = '692249525549676'
API_SECRET = '6Xa1qMPmAoba0rMhYCm8b0whtHs'

cloudinary.config(
    cloud_name = CLOUD_NAME,  
    api_key = API_KEY,  
    api_secret = API_SECRET
)

def upload(file, method):
    res = cloudinary.uploader.upload(file, folder=method)
    return res['url']