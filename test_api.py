import requests
import json

# 测试登录获取token
def test_login():
    url = 'http://127.0.0.1:5000/api/auth/login'
    headers = {'Content-Type': 'application/json'}
    data = {'username': 'test', 'password': '123456'}
    
    response = requests.post(url, headers=headers, json=data)
    print('Login Response:', response.status_code)
    print('Login Data:', response.json())
    
    # 打印完整的响应结构
    print('\nFull Login Response:')
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        # 尝试不同的路径获取token
        if 'data' in response.json() and 'access_token' in response.json()['data']:
            return response.json()['data']['access_token']
        elif 'access_token' in response.json():
            return response.json()['access_token']
    return None

# 测试创建文章
def test_create_post(token):
    url = 'http://127.0.0.1:5000/api/posts/add'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {'title': '测试文章', 'content': '这是一篇测试文章内容'}
    
    print('\nTesting create post with token:', token)
    print('Authorization Header:', headers['Authorization'])
    response = requests.post(url, headers=headers, json=data)
    print('Create Post Response:', response.status_code)
    print('Create Post Data:', response.json())
    print('Create Post Headers:', dict(response.headers))

if __name__ == '__main__':
    token = test_login()
    if token:
        test_create_post(token)
