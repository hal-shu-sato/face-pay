# -*- coding: utf-8 -*-
import json
import boto3
from typing import Union, Tuple
from datetime import datetime
import botocore.exceptions
import base64
client = boto3.client('lambda')
DB_ACCESS_LAMBDA = 'addUserToDB'

REKOGNITION_CLIENT = boto3.client('rekognition')
COLLECTION_ID = 'collection-face-pay'
s3 = boto3.resource('s3')      # ③S3オブジェクトを取得
MAX_FACES = 4096

# リクエストボディに必須の値(name)とその型(type)の定義
REQUIRED_KEYS: list = [{'name': 'image_base64str', 'type': (str,)}]
OPTIONAL_KEYS: list = [{'name': 'uuid', 'type': (str,)}]
def load_json(str_json: str) -> Tuple[bool, dict]:
    """
    JSON文字列をPythonで処理できる形にする
    """
    print('[DEBUG]load_json()')
    if str_json is None:
        return False, self.make_response(400, '[FAILED]Data required')
    # Lambdaテスト時にdict型で入ってくるためif分岐
    if isinstance(str_json, str):
        try:
            return True, json.loads(str_json)
        except json.JSONDecodeError:
            print('[DEBUG]json decode error')
            return False, self.make_response(400, '[FAILED]json decode error')
    else:
        return True, str_json
import boto3
class RecognizeFaces():
     def __init__(self):
          self.rekognition_client = REKOGNITION_CLIENT
          self.collection_id = COLLECTION_ID
          self.bucket_name = ''
          self.max_faces = MAX_FACES
          self.required_keys = REQUIRED_KEYS
          self.optional_keys = OPTIONAL_KEYS

     def make_timestamp(self) -> str: 
          """
          タイムスタンプを作成する
          """
          date_now = datetime.now()
          return str(date_now.strftime('%Y-%m-%d %H:%M:%S'))

     def create_response(self, data: dict) -> dict:
          """
          Rekognition結果を解析し、Response Bodyのデータを作成する
          """
          print('[DEBUG]create_response()')
          payloads: dict = {}
          payloads['timestamp'] = self.make_timestamp()
          payloads.update(data)
          return self.make_response(200, '[SUCCEEDED]Rekognition done', payloads)

     def decode_base64_to_binary(self, image_base64str: str) -> bytes:
          """
          base64のデータをバイナリデータに変換する
          """
          print('[DEBUG]decode_base64_to_binary()')
          # 画像データから不要な値を抜き出す(コンマがない場合は不要な値がないとし、全文字列を利用)
          image_base64str = image_base64str[image_base64str.find(',') + 1 :]
          return base64.b64decode(image_base64str)

     def search_face(self, image_binary: bytes, threshold: float = None) -> dict:
          """
          画像とマッチする人物を特定する
          """
          print('[DEBUG]search_face()')
          try:
               search_result = self.rekognition_client.search_faces_by_image(
                    CollectionId=self.collection_id,
                    Image={
                         'Bytes': image_binary
                    },
                    MaxFaces=self.max_faces,
                    FaceMatchThreshold=threshold
               )
               return self.create_response(search_result)

          # 画像内に顔を認識出来ない場合
          except botocore.exceptions.InvalidParameterException as error:
               print('[DEBUG]: {}'.format(error))
               return self.make_response(421, '画像内に人物の顔を認識出来ませんでした')
          
          # 画像サイズが制限オーバーの場合
          except botocore.exceptions.ImageTooLargeException as error:
               print('[DEBUG]: {}'.format(error))
               return self.make_response(422, '画像のサイズが大きすぎます（制限:15MB）')
          
          # 画像フォーマットが異なる場合
          except botocore.exceptions.InvalidImageFormatException as error:
               print('[DEBUG]: {}'.format(error))
               return self.make_response(423, '画像のフォーマットが異なります（制限:PNGあるいはJPEG形式）')
          
          # その他エラーに対処
          except Exception as error:
               print('[DEBUG]: {}'.format(error))
               error_code = error.response['Error']['Code']
               if (error_code == 'InvalidParameterException'):
                    return self.make_response(421, '画像内に人物の顔を認識出来ませんでした')
               elif (error_code == 'ImageTooLargeException'):
                    return self.make_response(422, '画像のサイズが大きすぎます（制限:15MB）')
               elif (error_code == 'InvalidImageFormatException'):
                    return self.make_response(423, '画像のフォーマットが異なります（制限:PNGあるいはJPEG形式）')
               else:
                    return self.make_response(500, '[FAILED]{}'.format(error))
               
     def check_validation(self, body: dict) -> Union[None, dict]:
          """
          バリデーションチェックをする関数
          """
          print('[DEBUG]check_validation()')
          if not body:
               return self.make_response(400, '[FAILED]Data required')
          if not isinstance(body, dict):
               return self.make_response(400, '[FAILED]Invalid body type')
          
          errors: list = []
          for key_info in self.required_keys:
               key_name: str = key_info['name']
               key_type: tuple = key_info['type']
               if not key_name in body.keys():
                    errors.append('key "{}" not found'.format(key_name))
               elif body[key_name] == '':
                    errors.append('no value found for "{}"'.format(key_name))
               elif type(body[key_name]) not in key_type:
                    errors.append('invalid value type: "{}"'.format(key_name))
          for key_info in self.optional_keys:
               key_name = key_info['name']
               key_type = key_info['type']
               if key_name in body.keys():
                    if type(body[key_name]) not in tuple(key_type):
                         errors.append('invalid value type: "{}"'.format(key_name))
          if errors:
               return self.make_response(400, '[FAILED]' + ', '.join(errors))
          else: 
               return None

     def load_json(self, str_json: str) -> Tuple[bool, dict]:
          """
          JSON文字列をPythonで処理できる形にする
          """
          print('[DEBUG]load_json()')
          if str_json is None:
               return False, self.make_response(400, '[FAILED]Data required')
          # Lambdaテスト時にdict型で入ってくるためif分岐
          if isinstance(str_json, str):
               try:
                    return True, json.loads(str_json)
               except json.JSONDecodeError:
                    print('[DEBUG]json decode error')
                    return False, self.make_response(400, '[FAILED]json decode error')
          else:
               return True, str_json

     def make_response(self, status_code: int, msg: str, payloads: dict = None) -> dict:
          """
          レスポンスを作成する
          """
          print('[DEBUG]make_response()')
          if payloads:
               body = json.dumps({'msg': msg, 'payloads': payloads})
          else:
               body = json.dumps({'msg': msg})
          return {
               'statusCode': status_code,
               'headers': {"Access-Control-Allow-Origin" : "*"},
               'body': body,
          }
    
     def add_faces_to_collection(self,uuid):
        bucket = 'face-pay-bucket'
        collection_id = self.collection_id
        client = self.rekognition_client

        response = client.index_faces(CollectionId=collection_id,
                                    Image={'S3Object': {'Bucket': bucket, 'Name': uuid}},
                                    ExternalImageId=uuid,
                                    MaxFaces=1,
                                    QualityFilter="AUTO",
                                    DetectionAttributes=['ALL'])

        print('Results for ' + uuid)
        print('Faces indexed:')
        for faceRecord in response['FaceRecords']:
            print('  Face ID: ' + faceRecord['Face']['FaceId'])
            print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

        print('Faces not indexed:')
        for unindexedFace in response['UnindexedFaces']:
            print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
            print(' Reasons:')
            for reason in unindexedFace['Reasons']:
                print('   ' + reason)
        print('[DEBUG]add_faces_to_collection')
        return len(response['FaceRecords'])

     def add_face_to_s3(self,uuid, image_data):
          print("[DEBUG]:add_face_to_s3")
          s3 = boto3.resource('s3')
          bucket = s3.Bucket('face-pay-bucket')
          print("[DEBUG]:getted bucket")
          print("[DEBUG]:image_data", image_data)
          # 画像をS3にアップロード
          response = bucket.put_object(
               Body=image_data,
               Key=uuid
          )
          
          print("[DEBUG]:put_object")
          
          # タグを追加
          s3_client = boto3.client('s3')
          s3_client.put_object_tagging(
               Bucket='face-pay-bucket',
               Key=uuid,
               Tagging={
                    'TagSet': [
                         {
                              'Key': uuid,
                              'Value': uuid
                         }
                    ]
               }
          )
          print('[DEBUG]add_face_to_s3 with UUID tag')


#　初期化
register_post = RecognizeFaces()

def lambda_handler(event, _) -> dict:
    """
    /registerに対するPOSTをトリガーに実行
    """
    try:
        # リクエストボディの中の文字列型JSONデータをPythonで扱える形に変換する
        result, body = register_post.load_json(event['body'])
        
        if not result:
            return body
        # リクエストボディから送られた画像データをバイナリに変換しRekognitionが受け取れる形にする
        
        image_binary = register_post.decode_base64_to_binary(body['image_base64str'])
        print("[DEBUG]: decode success")
        _uuid = body['uuid']
        # register
        print("[uuid]",_uuid)
        register_post.add_face_to_s3(_uuid,image_binary)
        print("[DEBUG]: add_face_to_s3 success")
        register_post.add_faces_to_collection(_uuid)
        print("[DEBUG]: add_face_to_collection success")
        import uuid
        name = str(uuid.uuid4())

        db_query = json.dumps({"body":{
            'uuid': _uuid, 
            'name': name, 
        }})
        # notify
        db_response = client.invoke(
            FunctionName=DB_ACCESS_LAMBDA,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=db_query
        )
        print('[DEBUG] db_lambda invoked')
        db_payload = json.loads(db_response['Payload'].read())
        print('[db_payload]:',db_payload)
            
        _, db_body = load_json(db_payload)
        print('[db_body]:',db_body)
        status = db_body.get('statusCode')
        if status == 200:
            message = {'msg':db_body.get('message')}
            return register_post.make_response(200,'[SUCEED]Your face has registered!', {})

    except Exception as error:
        print('[DEBUG]500:{}'.format(error))
        # エラーメッセージとリクエストのbodyを含めたレスポンスを返す
        error_response = {
            'error_message': str(error),
            'request_body': uuid if 'body' in locals() else None
        }
        return register_post.make_response(500, '[FAILED]An error occurred', error_response)