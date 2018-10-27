from os import getcwd
from datetime import datetime
#- from time import sleep
#- from subprocess import check_call, CalledProcessError, run, PIPE, STDOUT
from subprocess import CalledProcessError, run, PIPE, STDOUT
#- from sys import path, exc_info
from sys import exc_info
#- from shutil import copyfile

from file_uploader import upload_camera_image
from logger import get_top_level_logger

from config.config import camera_id, picture_directory, picture_trigger, upload_url

logger = get_top_level_logger()

def snap(file_location) -> 'file_path':

    logger.info('Creating new camera image')

    camera_shell_command = 'fswebcam -r 2592x1944 --no-banner --timestamp "%d-%m-%Y %H:%M:%S (%Z)"'\
                          + ' --set Brightness=40 --verbose  --save {}'.format(getcwd() + file_location)

    logger.debug('Preparing to run shell command: {}'.format(camera_shell_command))

    try:
        # Take the picture
        picture_results = run(camera_shell_command, stdout=PIPE, stderr=PIPE, shell=True, check=False)

        if picture_results.returncode == 0:
                
            if len(picture_results.stderr) != 0:
                logger.debug('---stderr: {}: '.format(picture_results.stderr.decode('ascii')))

            logger.debug('fsweb command success. See the following lines for more info:')
            logger.debug('---return code: {} ...'.format(picture_results.returncode))
            logger.debug('---args: {} ...'.format(picture_results.args))
            logger.debug('---stdout: {}'.format(picture_results.stdout.decode('ascii')))

            return file_location

        else:
           logger.error('fsweb command failed. See following lines for more info:')
           logger.error('---return code: {}'.format(picture_results.returncode))
           logger.error('---stderr: {}'.format(picture_results.stderr.decode('ascii')))
           logger.error('---args: {}'.format(picture_results.args))
           logger.error('---stdout: {}'.format(picture_results.stdout.decode('ascii')))
           return None

    except CalledProcessError as e:
        logger.error('fswebcam call failed with the following results: {}: {}'.format(\
                           exc_info()[0], exc_info()[1]))
        return None
    except:
        logger.error('Camera error: {}: {}'.format(exc_info()[0], exc_info()[1]))
        return None


def start():

    logger.info('Starting camera controller.')

    #+ state = get_state()

    now = datetime.now()

    file_location = picture_directory + '{}.jpg'.format(now.strftime('%Y-%m-%d_%H%M'))
    logger.info('will write new picture to {}'.format(file_location))

    # create a new picture and place it in the local file location
    snap(file_location)

    # if the picture_trigger pattern is such as to indicate a picture upload is desired
    # then upload the picture to the fop cloud.
    if picture_trigger == 'always' or\
       picture_trigger == now.strftime('%H:%M'):

        upload_camera_image(now, file_location, upload_url, camera_id)

    #TODO - provide a picture delete function to delete old pictures in the picture_directory

    logger.info('Exiting camera controller.')
