import boto3
import pytube

def download_and_upload(link,title):
    '''
    Returns: Url to download the file
    Usage: Download the video file and store it in the local system 
           and upload in the s3
    '''
    yt = pytube.YouTube(link)
    stream = yt.streams.first()
    stream.download()
    print("Download finished")
    video_name = stream.default_filename

    access_key = 'YOUR AWS ACCESS KEY'
    secret_key = 'YOUR AWS SECRET KEY'
    region = 'YOUR REGION NAME'
    client = boto3.client(
                service_name='s3',
                verify=False,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
    data = open(video_name, 'rb')
    try:        
        client.head_object(Key = title, Bucket = 'YOUR BUCKET NAME')
        url = client.generate_presigned_url('get_object', Params = {'Bucket':'skaas-dev-test', 'Key':title})
        return url
    except:
        client.put_object(Key = title, Body=data, Bucket='YOUR BUCKET NAME')
        url = client.generate_presigned_url('get_object', Params = {'Bucket':'skaas-dev-test', 'Key':title})
        return url

