document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('convertForm');
    const convertBtn = document.getElementById('convertBtn');
    const progress = document.getElementById('progress');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const downloadLink = document.getElementById('downloadLink');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 重置状态
        progress.classList.remove('hidden');
        result.classList.add('hidden');
        error.classList.add('hidden');
        convertBtn.disabled = true;
        
        // 创建FormData
        const formData = new FormData(form);
        
        // 发送请求
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progress.classList.add('hidden');
            convertBtn.disabled = false;
            
            if (data.status === 'success') {
                result.classList.remove('hidden');
                downloadLink.href = data.downloadUrl;
            } else {
                error.classList.remove('hidden');
                error.textContent = data.message;
            }
        })
        .catch(err => {
            progress.classList.add('hidden');
            convertBtn.disabled = false;
            error.classList.remove('hidden');
            error.textContent = '网络错误，请重试';
            console.error(err);
        });
    });
});
