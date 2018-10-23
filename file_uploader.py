from base64 import standard_b64encode
from datetime import datetime, timezone
from hashlib import sha256
from jose import jws 
from requests import post
from time import time
from uuid import uuid4
from sys import exc_info

from logger import get_sub_logger
from nacl_fop import decrypt

#- from config.config import device_id, hmac_secret_key_b64_cipher, fop_jose_id
from config.config import device_id, hmac_secret_key_b64_cipher, fop_jose_id

logger = get_sub_logger(__name__) 

# Make the JWT claim set
def claim_info(file_hash, time_stamp, camera_id):

    #- TBD: Time delivers seconds since unix epoch. Not all systems have the same epoch start date.  There
    #- may be a better way to time stamp the claims.
    issue_time = int(time())

    # See RFC 7519
    return {'iss':device_id,                 #Issuer -> This mvp is the issuer. Use it's secret key to authenticate.
            'aud':fop_jose_id,               #Audience -> identifies the cloud provider that will receive this claim.
            'exp':issue_time + 60,           #Expiration Time
            'sub':camera_id,                 #Subject -> This mvp's camera is the subject
            'nbf':issue_time - 60,           #Not Before Time
            'iat':issue_time,                #Issued At
            'jti':str(uuid4()),              #JWT ID -> Don't accept duplicates by jti
            'file_dt':time_stamp,
            'file_hash':file_hash}
    
def get_file_hash(path_name):

    m = sha256()
    with open(path_name, 'rb') as f:
        for line in f:
            m.update(line)
            
    return standard_b64encode(m.digest()).decode('utf-8')

def get_jws(image_datetime, path_name, camera_id):

    return jws.sign(claim_info(get_file_hash(path_name), image_datetime.timestamp(), camera_id), 
                    decrypt(hmac_secret_key_b64_cipher),
                    algorithm='HS256')

def upload_camera_image(image_datetime, path_name, url, camera_id):

    try:
        with open(path_name, 'rb') as f:
            r = post('{}'.format(url), 
                     data={'auth_method':'JWS', 'auth_data':get_jws(image_datetime, path_name, camera_id)}, 
                     files={'file':f}) 

        result = r.content.decode('utf-8')
        if result == 'ok':
            logger.info('Image uploaded.')
        else:
            logger.error('Image upload error, server response -> {}'.format(result))
    except:
        logger.error('Image upload failed {}, {}'.format(exc_info()[0], exc_info()[1]))
