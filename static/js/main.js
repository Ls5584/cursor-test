// DOM元素
const textInput = document.getElementById('textInput');
const importBtn = document.getElementById('importBtn');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const saveBtn = document.getElementById('saveBtn');
const helpBtn = document.getElementById('helpBtn');
const themeBtn = document.getElementById('themeBtn');
const closeHelpBtn = document.getElementById('closeHelpBtn');
const helpDialog = document.getElementById('helpDialog');
const stopwordsSection = document.getElementById('stopwordsSection');
const stopwordInput = document.getElementById('stopwordInput');
const addStopwordBtn = document.getElementById('addStopwordBtn');
const stopwordsList = document.getElementById('stopwordsList');
const freqList = document.getElementById('freqList');
const wordcloudImage = document.getElementById('wordcloudImage');

// 主题切换
let isDarkTheme = false;
themeBtn.addEventListener('click', () => {
    isDarkTheme = !isDarkTheme;
    document.body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    themeBtn.querySelector('.material-icons').textContent = isDarkTheme ? 'light_mode' : 'dark_mode';
});

// 帮助对话框
helpBtn.addEventListener('click', () => {
    helpDialog.style.display = 'block';
});

closeHelpBtn.addEventListener('click', () => {
    helpDialog.style.display = 'none';
});

// 点击对话框外部关闭
helpDialog.addEventListener('click', (e) => {
    if (e.target === helpDialog) {
        helpDialog.style.display = 'none';
    }
});

// 文件导入
importBtn.addEventListener('click', async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (file) {
            try {
                const text = await file.text();
                textInput.value = text;
            } catch (error) {
                showNotification('错误', '无法读取文件内容');
            }
        }
    };
    
    input.click();
});

// 生成词云
generateBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
        showNotification('警告', '请输入文本内容');
        return;
    }
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        if (data.success) {
            // 更新词频统计
            updateFreqList(data.frequencies);
            // 更新词云图像
            wordcloudImage.src = data.wordcloud_image;
            // 显示停用词区域
            stopwordsSection.style.display = 'block';
            // 启用保存按钮
            saveBtn.disabled = false;
        } else {
            showNotification('错误', data.message || '生成词云失败');
        }
    } catch (error) {
        showNotification('错误', '服务器连接失败');
    }
});

// 更新词频列表
function updateFreqList(frequencies) {
    freqList.innerHTML = '';
    frequencies.forEach(([word, freq]) => {
        const item = document.createElement('div');
        item.className = 'freq-item';
        item.innerHTML = `
            <span class="word">${word}</span>
            <span class="freq">${freq}次</span>
        `;
        freqList.appendChild(item);
    });
}

// 添加停用词
addStopwordBtn.addEventListener('click', async () => {
    const word = stopwordInput.value.trim();
    if (!word) {
        showNotification('警告', '请输入要添加的停用词');
        return;
    }
    
    try {
        const response = await fetch('/add_stopword', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ word })
        });
        
        const data = await response.json();
        if (data.success) {
            addStopwordToList(word);
            stopwordInput.value = '';
            // 重新生成词云
            generateBtn.click();
        } else {
            showNotification('错误', data.message || '添加停用词失败');
        }
    } catch (error) {
        showNotification('错误', '服务器连接失败');
    }
});

// 添加停用词到列表
function addStopwordToList(word) {
    const item = document.createElement('div');
    item.className = 'stopword-item';
    item.innerHTML = `
        <span>${word}</span>
        <button class="btn danger" onclick="removeStopword('${word}')">
            <span class="material-icons">close</span>
        </button>
    `;
    stopwordsList.appendChild(item);
}

// 删除停用词
async function removeStopword(word) {
    try {
        const response = await fetch('/remove_stopword', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ word })
        });
        
        const data = await response.json();
        if (data.success) {
            // 从列表中移除
            const items = stopwordsList.getElementsByClassName('stopword-item');
            for (let item of items) {
                if (item.querySelector('span').textContent === word) {
                    item.remove();
                    break;
                }
            }
            // 重新生成词云
            generateBtn.click();
        } else {
            showNotification('错误', data.message || '删除停用词失败');
        }
    } catch (error) {
        showNotification('错误', '服务器连接失败');
    }
}

// 保存图片
saveBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/save_image', {
            method: 'GET'
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'wordcloud.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            showNotification('错误', '保存图片失败');
        }
    } catch (error) {
        showNotification('错误', '服务器连接失败');
    }
});

// 重置应用
resetBtn.addEventListener('click', () => {
    textInput.value = '';
    freqList.innerHTML = '';
    wordcloudImage.src = '';
    stopwordInput.value = '';
    stopwordsList.innerHTML = '';
    stopwordsSection.style.display = 'none';
    saveBtn.disabled = true;
});

// 显示通知
function showNotification(title, message) {
    // 这里可以使用你喜欢的通知库
    alert(`${title}: ${message}`);
} 