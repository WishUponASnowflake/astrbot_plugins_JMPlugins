import json
import os

from jmcomic import JmOption, JmSearchPage, create_option_by_file

# 更新配置文件路径
config_path = "./data/plugins/astrbot_plugins_JMPlugins/module.json"
# config_path="./module.json"
# option_url = "./option.yml"
def get_last_album_id():
    """
    读取配置文件中的last_album_id值
    Returns:
        str: last_album_id的值，如果不存在或文件不存在则返回None
    """
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        # 如果文件不存在，创建一个空的配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 从dynamic_config中获取last_album_id
            dynamic_config = config.get('dynamic_config', {})
            return dynamic_config.get('last_album_id', None)
    except (json.JSONDecodeError, FileNotFoundError):
        # 如果文件损坏或无法读取，返回None
        return None

def set_last_album_id(album_id):
    """
    设置配置文件中的last_album_id值
    Args:
        album_id (str): 要设置的album_id值
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 如果文件不存在，创建一个默认配置
    if not os.path.exists(config_path):
        config = {
            "static_config": {},
            "dynamic_config": {
                "last_album_id": album_id
            }
        }
    else:
        # 读取现有配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            config = {
                "static_config": {},
                "dynamic_config": {
                    "last_album_id": album_id
                }
            }
        
        # 确保dynamic_config存在
        if "dynamic_config" not in config:
            config["dynamic_config"] = {}
        
        # 更新last_album_id
        config["dynamic_config"]["last_album_id"] = album_id
    
    # 写入文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_query_key():
    """
    获取配置文件中的query_key值
    Returns:
        str: query_key的值，如果不存在或文件不存在则返回空字符串
    """
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        return ""
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 从static_config中获取query_key
            static_config = config.get('static_config', {})
            return static_config.get('query_key', "")
    except (json.JSONDecodeError, FileNotFoundError):
        # 如果文件损坏或无法读取，返回空字符串
        return ""

def set_query_key(query_key):
    """
    设置配置文件中的query_key值
    Args:
        query_key (str): 要设置的query_key值
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 如果文件不存在，创建一个默认配置
    if not os.path.exists(config_path):
        config = {
            "static_config": {
                "query_key": query_key
            },
            "dynamic_config": {}
        }
    else:
        # 读取现有配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            config = {
                "static_config": {
                    "query_key": query_key
                },
                "dynamic_config": {}
            }
        
        # 确保static_config存在
        if "static_config" not in config:
            config["static_config"] = {}
        
        # 更新query_key
        config["static_config"]["query_key"] = query_key
    
    # 写入文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def search_title_and_pic(download_path, option,max_count=15):
    """
    搜索标题和图片
    """
    # 如果没有提供key，则使用配置文件中的query_key
    key = get_query_key()
    # 如果配置文件中也没有key，则使用默认值
    if not key:
        key = "ブルーアーカイブ"
    
    try:
        client = JmOption.copy_option(option).new_jm_client()
        album: JmSearchPage = client.search_site(search_query=key, page=1)
        empty_tag = 0
    except:
        empty_tag = 1

    int_filterid=int(get_last_album_id())

    result_album_id = []
    result_album_title = []
    result_tag=[]
    for album_id, title in album:
        # print(f"{album_id} {title}")
        if int(album_id) < int_filterid:
            continue
        result_album_id.append(album_id)
        result_album_title.append(title)

    # 下载封面，按照albumid顺序下载
    if download_path is None:
        folder_path ='./data/plugins/astrbot_plugins_JMPlugins/pic/'
    else:
        folder_path = download_path
    count = len(result_album_id)

    print(f"找到{count}个结果，正在下载封面,最多下载{max_count}个封面")
    count = min(max_count, count)
    # print(count)


    for i in range(count):
        try:
            page = client.search_site(search_query=result_album_id[i])
            album_detail = page.single_album
        except:
            result_tag.append(" ")
            continue
        result_tag.append(album_detail.tags)

        photo = album_detail.getindex(0)
        photo01 = client.get_photo_detail(photo.photo_id, False)

        image = photo01[0]
        if os.path.exists(os.path.join(folder_path, f'{i}.jpg')):
            os.remove(os.path.join(folder_path, f'{i}.jpg'))
        client.download_by_image_detail(image, os.path.join(folder_path, f'{i}.jpg'))
        # print(os.path.join(folder_path, f'{i}.jpg'))

    # 添加防挡
    for i in range(count):
        image_path = os.path.join(folder_path, f'{i}.jpg')
        if os.path.exists(image_path):
            from PIL import Image as ProcessImage
            original_image = ProcessImage.open(image_path)
            # 获取原始图片的宽度和高度
            width, height = original_image.size
            # 创建一张新的空白图片，大小为原图的宽度和五倍高度
            new_image = ProcessImage.new('RGB', (width, height * 5 + 200), color=(255, 255, 255))
            # 将原图粘贴到新图片的下半部分
            new_image.paste(original_image, (0, height * 4))
            # 保存最终结果
            new_image.save(image_path)

    # 更新last_album_id
    set_last_album_id(result_album_id[0])


    return result_album_id,result_album_title,result_tag


# if __name__ == '__main__':
#     search_title_and_pic("./pic/",option,5)
#
#
#     # print(get_last_album_id())
#     # set_last_album_id('1230010')
#     # print(get_last_album_id())
#     # print(get_query_key())
#     pass