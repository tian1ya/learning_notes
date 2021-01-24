import requests
from concurrent.futures import ThreadPoolExecutor

def task(url):
    return requests.get(url).status_code

if __name__=="__main__":
    pool = ThreadPoolExecutor(max_workers=5)

    urls = ['http://www.baidu.com', 'http://www.163.com', 'http://www.taobao.com']
    result = pool.map(task, urls)
    # 输出结果
    for item in result:
        print(item)

    print("=========================================")

    result = []
    pool = ThreadPoolExecutor(max_workers=5)

    # 使用submit 提交任务到线程池
    result.append(pool.submit(task, 'http://www.baidu.com',))
    result.append(pool.submit(task, 'http://www.163.com',))
    result.append(pool.submit(task, 'http://www.taobao.com',))

    # 输出结果
    for i in result:
        print(i.result())
