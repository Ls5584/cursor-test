import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import jieba
from wordcloud import WordCloud
import io
from collections import Counter
import string
import re

class WordCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("词云统计应用")
        self.root.geometry("800x800")
        
        # 定义停用词列表
        self.stopwords = set([
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
            '���么', '谁', '哪', '哪个', '哪些', '怎么', '怎么样', '怎样', '为什么',
            '是', '不是', '没', '没有', '不', '不要', '得', '地', '的'
        ])
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文本输入区域
        self.text_label = ttk.Label(self.main_frame, text="请输入或粘贴文本：")
        self.text_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.text_input = tk.Text(self.main_frame, height=10, width=80)
        self.text_input.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 词频设置区域
        self.freq_frame = ttk.LabelFrame(self.main_frame, text="词频设置", padding="5")
        self.freq_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 最小词频滑动条
        self.min_freq_label = ttk.Label(self.freq_frame, text="最小词频：")
        self.min_freq_label.grid(row=0, column=0, padx=5)
        
        self.min_freq_var = tk.IntVar(value=1)
        self.min_freq_scale = ttk.Scale(
            self.freq_frame,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.min_freq_var,
            length=200
        )
        self.min_freq_scale.grid(row=0, column=1, padx=5)
        
        self.min_freq_value_label = ttk.Label(self.freq_frame, text="1")
        self.min_freq_value_label.grid(row=0, column=2, padx=5)
        
        # 最大词频滑动条
        self.max_freq_label = ttk.Label(self.freq_frame, text="最大词频：")
        self.max_freq_label.grid(row=1, column=0, padx=5)
        
        self.max_freq_var = tk.IntVar(value=100)
        self.max_freq_scale = ttk.Scale(
            self.freq_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.max_freq_var,
            length=200
        )
        self.max_freq_scale.grid(row=1, column=1, padx=5)
        
        self.max_freq_value_label = ttk.Label(self.freq_frame, text="100")
        self.max_freq_value_label.grid(row=1, column=2, padx=5)
        
        # 绑定滑动条值变化事件
        self.min_freq_scale.configure(command=self.update_min_freq_label)
        self.max_freq_scale.configure(command=self.update_max_freq_label)
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.import_btn = ttk.Button(self.button_frame, text="导入文本", command=self.import_file)
        self.import_btn.grid(row=0, column=0, padx=5)
        
        self.generate_btn = ttk.Button(self.button_frame, text="生成词云", command=self.generate_wordcloud)
        self.generate_btn.grid(row=0, column=1, padx=5)
        
        self.save_btn = ttk.Button(self.button_frame, text="保存图片", command=self.save_image)
        self.save_btn.grid(row=0, column=2, padx=5)
        
        # 词频统计显示区域
        self.freq_display = tk.Text(self.main_frame, height=5, width=80)
        self.freq_display.grid(row=4, column=0, columnspan=2, pady=5)
        self.freq_display.config(state=tk.DISABLED)
        
        # 词云显示区域
        self.image_label = ttk.Label(self.main_frame)
        self.image_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 保存当前词云图像和词频统计
        self.current_wordcloud = None
        self.word_frequencies = None
        
    def update_min_freq_label(self, value):
        self.min_freq_value_label.configure(text=str(int(float(value))))
        
    def update_max_freq_label(self, value):
        self.max_freq_value_label.configure(text=str(int(float(value))))
        
    def import_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_input.delete('1.0', tk.END)
                    self.text_input.insert('1.0', content)
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件：{str(e)}")
    
    def filter_words(self, words):
        """过滤停用词和无效字符"""
        return [word for word in words if (
            word not in self.stopwords and  # 不在停用词列表中
            len(word.strip()) > 1 and       # 长度大于1
            not word.isspace() and          # 不是空白字符
            not re.match(r'^[0-9]+$', word) # 不是纯数字
        )]
    
    def generate_wordcloud(self):
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入文本内容")
            return
            
        # 使用jieba分词并过滤停用词
        words = list(jieba.cut(text))
        filtered_words = self.filter_words(words)
        
        # 统计词频
        word_freq = Counter(filtered_words)
        
        # 过滤词频
        min_freq = self.min_freq_var.get()
        max_freq = self.max_freq_var.get()
        
        filtered_words = {word: freq for word, freq in word_freq.items() 
                         if min_freq <= freq <= max_freq}
        
        if not filtered_words:
            messagebox.showwarning("警告", "在当前词频范围内没有找到符合条件的词语")
            return
        
        # 更新词频显示
        self.freq_display.config(state=tk.NORMAL)
        self.freq_display.delete('1.0', tk.END)
        freq_text = "词频统计（前10个）：\n"
        for word, freq in sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:10]:
            freq_text += f"{word}: {freq}次\n"
        self.freq_display.insert('1.0', freq_text)
        self.freq_display.config(state=tk.DISABLED)
        
        # 生成词云
        wordcloud = WordCloud(
            font_path="msyh.ttc",  # 使用微软雅黑字体
            width=600,
            height=400,
            background_color='white',
            max_words=100,
            min_font_size=10,
            max_font_size=100
        ).generate_from_frequencies(filtered_words)
        
        # 转换为PIL图像
        image = wordcloud.to_image()
        self.current_wordcloud = image
        
        # 调整图像大小以适应显示
        image = image.resize((600, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        # 更新显示
        self.image_label.configure(image=photo)
        self.image_label.image = photo
    
    def save_image(self):
        if self.current_wordcloud is None:
            messagebox.showwarning("警告", "请先生成词云")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")]
        )
        if file_path:
            try:
                self.current_wordcloud.save(file_path)
                messagebox.showinfo("成功", "词云图片已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WordCloudApp(root)
    root.mainloop() 