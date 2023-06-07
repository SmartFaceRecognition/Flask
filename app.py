from flask import Flask, render_template, request
import redis
import json
import boto3
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 레디스 연결
rd = redis.StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'],
                       password=app.config['REDIS_PASSWORD'])

# AWS S3 연결
s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS_KEY'],
                  aws_secret_access_key=app.config['AWS_SECRET_KEY'])

# S3 버킷 이름 설정
bucket_name = app.config['BUCKET_NAME']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    position = request.form.get('position')
    photo = request.files.get('photo')

    data = {
        'name': name,
        'position': position
    }

    json_data = json.dumps(data)

    next_id = rd.incr('next_id')

    # S3에 사진 업로드
    if photo:
        # S3에 업로드할 파일명 설정
        filename = f'{next_id}.jpg'

        # S3에 사진 업로드
        s3.upload_fileobj(photo, bucket_name, filename)

        # 링크 저장
        link = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{filename}"
        data['url'] = link

    rd.set(str(next_id), json.dumps(data))

    return f'{name}, {position} 정보가 제출되었습니다.'


if __name__ == '__main__':
    app.run(debug=True)
