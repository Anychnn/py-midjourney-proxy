# 定义XML转字典的函数
def trans_xml_to_dict(data_xml):
    # soup = BeautifulSoup(data_xml, features='xml')
    soup = BeautifulSoup(data_xml, "html.parser")

    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


# 定义字典转XML的函数
def trans_dict_to_xml(data_dict):
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    # return '<xml version="1.0" encoding="UTF-8" >{}</xml>'.format(''.join(data_xml))  # 返回XML
    # 返回XML，并转成utf-8，解决中文的问题
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')
