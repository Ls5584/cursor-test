# 系统库导入
import sys
import subprocess
import pkg_resources
import re
import string
from collections import Counter

# 依赖检查函数
def check_and_install_dependencies():
    """检查并安装所需的依赖包"""
    required_packages = {
        'jieba': '0.42.1',
        'wordcloud': '1.9.2',
        'Pillow': '10.1.0'
    }
    
    def install_package(package_name, version):
        print(f"正在安装 {package_name}=={version}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={version}"])
            return True
        except subprocess.CalledProcessError:
            print(f"安装 {package_name} 失败")
            return False
    
    all_installed = True
    for package, version in required_packages.items():
        try:
            pkg_resources.require(f"{package}=={version}")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            if not install_package(package, version):
                all_installed = False
    
    if not all_installed:
        print("某些依赖包安装失败，请手动安装所需的包。")
        print("需要安装的包：")
        for package, version in required_packages.items():
            print(f"pip install {package}=={version}")
        sys.exit(1)

# 检查并安装依赖
if __name__ == "__main__":
    check_and_install_dependencies()

# GUI库导入
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 第三方库导入
from PIL import Image, ImageTk
import jieba
from wordcloud import WordCloud

# 主应用类
class WordCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("词云统计应用")
        self.root.geometry("1200x800")
        
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
            '什么', '谁', '哪', '哪个', '哪些', '怎么', '怎么样', '怎样', '为什么',
            '是', '不是', '没', '没有', '不', '不要', '得', '地', '的'
        ])
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建水平分割的PanedWindow
        self.h_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.h_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建左侧垂直分割的PanedWindow
        self.left_v_paned = ttk.PanedWindow(self.h_paned, orient=tk.VERTICAL)
        
        # 创建右侧垂直分割的PanedWindow
        self.right_v_paned = ttk.PanedWindow(self.h_paned, orient=tk.VERTICAL)
        
        # 添加左右PanedWindow到水平分割
        self.h_paned.add(self.left_v_paned, weight=1)
        self.h_paned.add(self.right_v_paned, weight=1)
        
        # 文本输入区域
        input_frame = ttk.LabelFrame(self.left_v_paned, text="文本输入", padding="5")
        
        self.text_label = ttk.Label(input_frame, text="请输入或粘贴文本：")
        self.text_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # 创建文本输入框的滚动条
        text_scrollbar = ttk.Scrollbar(input_frame)
        text_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        self.text_input = tk.Text(
            input_frame,
            height=10,
            width=60,
            yscrollcommand=text_scrollbar.set,
            wrap=tk.WORD
        )
        self.text_input.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_scrollbar.configure(command=self.text_input.yview)
        
        # 配置input_frame的网格权重
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.import_btn = ttk.Button(button_frame, text="导入文件", command=self.import_file)
        self.import_btn.grid(row=0, column=0, padx=5)
        
        self.generate_btn = ttk.Button(button_frame, text="生成词云", command=self.generate_wordcloud)
        self.generate_btn.grid(row=0, column=1, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存图片", command=self.save_image)
        self.save_btn.grid(row=0, column=2, padx=5)
        
        self.reset_btn = ttk.Button(button_frame, text="初始化", command=self.reset_app)
        self.reset_btn.grid(row=0, column=3, padx=5)
        
        # 词频统计显示区域
        freq_display_frame = ttk.LabelFrame(self.left_v_paned, text="词频统计", padding="5")
        
        # 创建滚动条
        freq_scrollbar = ttk.Scrollbar(freq_display_frame)
        freq_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.freq_display = tk.Text(
            freq_display_frame,
            height=5,
            width=60,
            yscrollcommand=freq_scrollbar.set,
            wrap=tk.WORD
        )
        self.freq_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        freq_scrollbar.configure(command=self.freq_display.yview)
        self.freq_display.config(state=tk.DISABLED)
        
        # 配置freq_display_frame的网格权重
        freq_display_frame.columnconfigure(0, weight=1)
        freq_display_frame.rowconfigure(0, weight=1)
        
        # 添加到左侧垂直分割
        self.left_v_paned.add(input_frame, weight=1)
        self.left_v_paned.add(freq_display_frame, weight=1)
        
        # 自定义停用词区域（初始隐藏）
        self.stopwords_frame = ttk.LabelFrame(self.right_v_paned, text="自定义停用词", padding="5")
        self.stopwords_frame.grid_remove()  # 初始隐藏
        
        # 停用词输入和按钮区域
        stopword_input_frame = ttk.Frame(self.stopwords_frame)
        stopword_input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.stopword_var = tk.StringVar()
        self.stopword_entry = ttk.Entry(
            stopword_input_frame,
            textvariable=self.stopword_var
        )
        self.stopword_entry.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.add_stopword_btn = ttk.Button(
            stopword_input_frame,
            text="添加停用词",
            command=self.add_stopword
        )
        self.add_stopword_btn.grid(row=0, column=1, padx=5)
        
        # 配置stopword_input_frame的网格权重
        stopword_input_frame.columnconfigure(0, weight=1)
        
        # 停用词列表显示区域
        stopwords_list_frame = ttk.Frame(self.stopwords_frame)
        stopwords_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建滚动条
        stopwords_scrollbar = ttk.Scrollbar(stopwords_list_frame)
        stopwords_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.stopwords_listbox = tk.Listbox(
            stopwords_list_frame,
            height=4,
            selectmode=tk.SINGLE,
            yscrollcommand=stopwords_scrollbar.set
        )
        self.stopwords_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stopwords_scrollbar.configure(command=self.stopwords_listbox.yview)
        
        # 配置stopwords_list_frame的网格权重
        stopwords_list_frame.columnconfigure(0, weight=1)
        stopwords_list_frame.rowconfigure(0, weight=1)
        
        self.remove_stopword_btn = ttk.Button(
            self.stopwords_frame,
            text="删除选中的停用词",
            command=self.remove_stopword
        )
        self.remove_stopword_btn.grid(row=2, column=0, pady=5)
        
        # 配置stopwords_frame的网格权重
        self.stopwords_frame.columnconfigure(0, weight=1)
        self.stopwords_frame.rowconfigure(1, weight=1)
        
        # 词云显示区域
        wordcloud_frame = ttk.LabelFrame(self.right_v_paned, text="词云图像", padding="5")
        
        self.image_label = ttk.Label(wordcloud_frame)
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置wordcloud_frame的网格权重
        wordcloud_frame.columnconfigure(0, weight=1)
        wordcloud_frame.rowconfigure(0, weight=1)
        
        # 添加到右侧垂直分割
        self.right_v_paned.add(wordcloud_frame, weight=2)
        
        # 配置主窗口和主框架的权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # 初始化变量
        self.current_wordcloud = None
        self.word_frequencies = None
        self.custom_stopwords = set()
    
    def validate_number(self, value):
        """验证输入是否为有效的数字或无穷大符号"""
        if value == "" or value == "∞":
            return True
        try:
            if value.startswith("-"):
                return False
            if value.isdigit():
                return True
            return False
        except ValueError:
            return False
    
    def get_freq_value(self, value_str):
        """将输入值转换为数字，处理无穷大的情况"""
        if value_str == "∞":
            return float('inf')
        try:
            return int(value_str)
        except ValueError:
            return 1
    
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
    
    def add_stopword(self):
        """添加自定义停用词"""
        word = self.stopword_var.get().strip()
        if word:
            if word not in self.custom_stopwords:
                self.custom_stopwords.add(word)
                self.stopwords_listbox.insert(tk.END, word)
                self.stopword_var.set("")  # 清空输入框
            else:
                messagebox.showinfo("提示", "该词已在停用词列表中")
        else:
            messagebox.showwarning("警告", "请输入要添加的停用词")
    
    def remove_stopword(self):
        """删除选中的停用词"""
        selection = self.stopwords_listbox.curselection()
        if selection:
            word = self.stopwords_listbox.get(selection[0])
            self.custom_stopwords.remove(word)
            self.stopwords_listbox.delete(selection[0])
        else:
            messagebox.showwarning("警告", "请先选择要删除的停用词")
    
    def filter_words(self, words):
        """过滤停用词和无效字符"""
        return [word for word in words if (
            word not in self.stopwords and  # 不在默认停用词列表中
            word not in self.custom_stopwords and  # 不在自定义停用词列表中
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
        
        # 更新词频显示
        self.freq_display.config(state=tk.NORMAL)
        self.freq_display.delete('1.0', tk.END)
        freq_text = "词频统计（前10个）：\n"
        for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
            freq_text += f"{word}: {freq}次\n"
        self.freq_display.insert('1.0', freq_text)
        self.freq_display.config(state=tk.DISABLED)
        
        # 显示停用词区域并添加到右侧PanedWindow
        self.stopwords_frame.grid()
        self.right_v_paned.add(self.stopwords_frame, weight=1)
        
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
    
    def reset_app(self):
        """初始化应用状态"""
        # 清空文本输入
        self.text_input.delete('1.0', tk.END)
        
        # 清空词频显示
        self.freq_display.config(state=tk.NORMAL)
        self.freq_display.delete('1.0', tk.END)
        self.freq_display.config(state=tk.DISABLED)
        
        # 清空词云图像
        self.image_label.configure(image='')
        self.current_wordcloud = None
        
        # 清空自定义停用词
        self.custom_stopwords.clear()
        self.stopwords_listbox.delete(0, tk.END)
        self.stopword_var.set("")
        
        # 隐藏停用词区域
        self.stopwords_frame.grid_remove()
        
        # 重置变量
        self.word_frequencies = None
        
        messagebox.showinfo("提示", "已重置所有内容")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WordCloudApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
        sys.exit(1) 