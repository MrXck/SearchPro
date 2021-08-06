from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch

es = Elasticsearch()

app = Flask(__name__)
app.debug = True


@app.route('/get_data', methods=['post'])
def get_data():
    key_word = request.form.get('key_word')
    page_num = request.form.get('page_num', None)
    type = request.form.get('type')
    print(request.form.to_dict())
    if page_num == '1':
        start = 0
    else:
        start = (int(page_num) - 1) * 10
    body = {
        'query': {
            'match_phrase': {
                'key_word': key_word
            }
        },
        "highlight": {
            "pre_tags": "<b style='color:red;'>",
            "post_tags": "</b>",
            "fields": {
                "key_word": {}
            }
        },
        'from': start,
        'size': 10,
    }
    data = {
        'code': 1,
        'msg': '查询不到数据',
        'data': {}
    }
    result = es.search(index=type, doc_type='doc', body=body)
    print(result['hits']['total'])
    if len(result.get('hits').get('hits')) > 0:
        data['code'] = 0
        data['msg'] = '成功获取数据'
        data['data'] = result
        return jsonify(data)
    return jsonify(data)


@app.route('/get_jianyi', methods=['post'])
def get_jianyi():
    key_word = request.form.get('key_word')
    print(request.form.to_dict())
    body = {
        "suggest": {
            "text": key_word,
            "my_s1": {
                "completion": {
                    "field": "key_word1"
                }
            },
            "my_s2": {
                "phrase": {
                    "field": "key_word1"
                }
            },
            "my_s3": {
                "term": {
                    "field": "key_word1"
                }
            }
        }
    }
    data = {
        'code': 1,
        'msg': '查询不到数据',
        'data': {}
    }
    result = es.search(index='_all', doc_type='doc', body=body)
    result['suggest']['result_list'] = []
    result['suggest']['my_s'] = [{"options": ''}]
    if result['suggest']['my_s1']:
        for i in result['suggest']['my_s1'][0]['options']:
            result['suggest']['result_list'].append(i['text'])
    if result['suggest']['my_s2']:
        for i in result['suggest']['my_s2'][0]['options']:
            result['suggest']['result_list'].append(i['text'])
    if result['suggest']['my_s3']:
        for i in result['suggest']['my_s3'][0]['options']:
            result['suggest']['result_list'].append(i['text'])
    print(result['suggest']['result_list'])
    result['suggest']['my_s'][0]['options'] = list(set(result['suggest']['result_list']))
    if len(result['suggest']['my_s'][0]['options']) > 0:
        data['code'] = 0
        data['msg'] = '成功获取数据'
        data['data'] = result
        return jsonify(data)
    return jsonify(data)


@app.route('/search')
def search():
    return render_template('search_page.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9555)


"""
    # num = result['suggest']['my_s']
    # if len(num) < 1:
    #     body = {
    #         "suggest": {
    #             "text": key_word,
    #             "my_s": {
    #                 "phrase": {
    #                     "field": "key_word1",
    #                 }
    #             }
    #         },
    #         'from': 0,
    #         'size': 10,
    #     }
    #     result = es.search(index='_all', doc_type='doc', body=body)
    #     num = result['suggest']['my_s']
    #     if len(num) < 1:
    #         body = {
    #             "suggest": {
    #                 "text": key_word,
    #                 "my_s": {
    #                     "term": {
    #                         "field": "key_word1",
    #                     }
    #                 }
    #             },
    #             'from': 0,
    #             'size': 10,
    #         }
    #         result = es.search(index='_all', doc_type='doc', body=body)
"""
