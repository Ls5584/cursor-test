from flask import Flask, render_template, request, jsonify, send_file
import base64
import io
import jieba
from wordcloud import WordCloud
from collections import Counter
import re
import string

app = Flask(__name__)

# 停用词列表
STOPWORDS = set([
    # 标点符号
    '，', '。', '！', '？', '、', '；', '：', '"', '"', ''', ''', '（', '）', 
    '【', '】', '《', '》', '〈', '〉', '…', '—', '～', '@', '#', '￥', '%',
    # 英文标点
    *list(string.punctuation),
    # 常见语气词和虚词
    '啊', '哎', '哎呀', '哎哟', '唉', '嗯', '呢', '吧', '啦', '呀', '哦', '噢',
    '的', '了', '着', '呢', '吧', '啊', '啦', '呀', '哦', '噢', '嘛', '吗',
    '都', '就', '而', '而且', '但是', '但', '却', '呢', '吧', '啊', '啦', 
    '这', '那', '这个', '那个', '这些', '那些',
    '什么', '谁', '哪', '哪个', '哪些', '怎么', '怎么样', '怎样', '为什么',
    '是', '不是', '没', '没有', '不', '不要', '得', '地', '的'
])

# 用户自定义停用词
custom_stopwords = set()

# 当前词云图像
current_wordcloud = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'message': '请输入文本内容'})
        
        # 分词并过滤停用词
        words = list(jieba.cut(text))
        filtered_words = [word for word in words if (
            word not in STOPWORDS and
            word not in custom_stopwords and
            len(word.strip()) > 1 and
            not word.isspace() and
            not re.match(r'^[0-9]+$', word)
        )]
        
        # 统计词频
        word_freq = Counter(filtered_words)
        
        # 生成词云
        wordcloud = WordCloud(
            font_path="msyh.ttc",
            width=600,
            height=400,
            background_color='white',
            max_words=100,
            min_font_size=10,
            max_font_size=100
        ).generate_from_frequencies(word_freq)
        
        # 保存当前词云图像
        global current_wordcloud
        current_wordcloud = wordcloud
        
        # 将词云图像转换为base64
        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        # 获取前10个高频词
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            'success': True,
            'wordcloud_image': f'data:image/png;base64,{img_str}',
            'frequencies': top_words
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add_stopword', methods=['POST'])
def add_stopword():
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        
        if not word:
            return jsonify({'success': False, 'message': '请输入要添加的停用词'})
        
        if word in custom_stopwords:
            return jsonify({'success': False, 'message': '该词已在停用词列表中'})
        
        custom_stopwords.add(word)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/remove_stopword', methods=['POST'])
def remove_stopword():
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        
        if not word:
            return jsonify({'success': False, 'message': '请选择要删除的停用词'})
        
        if word not in custom_stopwords:
            return jsonify({'success': False, 'message': '该词不在停用词列表中'})
        
        custom_stopwords.remove(word)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/save_image', methods=['GET'])
def save_image():
    try:
        if current_wordcloud is None:
            return '请先生成词云', 400
            
        img_buffer = io.BytesIO()
        current_wordcloud.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name='wordcloud.png'
        )
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 