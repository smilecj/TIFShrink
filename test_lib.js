// 模拟浏览器环境
const { JSDOM } = require('jsdom');

// 创建虚拟 DOM
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
    runScripts: 'dangerously',
    resources: 'usable'
});

global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

// 动态加载脚本并测试
const https = require('https');
const http = require('http');

function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        lib.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve({ status: res.statusCode, data }));
        }).on('error', reject);
    });
}

async function test() {
    console.log('=== TIFShrink Pro 库测试 ===\n');
    
    // 测试 CDN 可访问性
    const urls = [
        ['JSZip', 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js'],
        ['tiff.js', 'https://unpkg.com/tiff.js'],
        ['canvas-to-tiff', 'https://cdn.jsdelivr.net/gh/motiz88/canvas-to-tiff@master/canvastotiff.min.js'],
        ['jsPDF', 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'],
    ];
    
    console.log('1. CDN 库可用性:');
    for (const [name, url] of urls) {
        try {
            const { status, data } = await fetchUrl(url);
            if (status === 200) {
                console.log(`   ✓ ${name}: 可用 (${(data.length / 1024).toFixed(1)} KB)`);
            } else {
                console.log(`   ✗ ${name}: HTTP ${status}`);
            }
        } catch (err) {
            console.log(`   ✗ ${name}: ${err.message}`);
        }
    }
    
    console.log('\n2. 测试主页面 HTML 结构:');
    const fs = require('fs');
    const html = fs.readFileSync('index.html', 'utf-8');
    
    const checks = [
        ['dropZone 元素', /id="dropZone"/],
        ['fileInput 元素', /id="fileInput"/],
        ['开始按钮', /id="startBtn"/],
        ['下载按钮', /id="downloadAllBtn"/],
        ['进度条', /id="progressBar"/],
        ['文件列表', /id="fileList"/],
        ['tiff.js 引用', /tiff\.js/],
        ['canvas-to-tiff 引用', /canvas-to-tiff/],
        ['jsPDF 引用', /jspdf/],
        ['JSZip 引用', /jszip/i],
    ];
    
    for (const [name, pattern] of checks) {
        if (pattern.test(html)) {
            console.log(`   ✓ ${name}`);
        } else {
            console.log(`   ✗ ${name} - 缺失!`);
        }
    }
    
    console.log('\n3. 测试测试页面:');
    if (fs.existsSync('test.html')) {
        console.log('   ✓ test.html 存在');
    } else {
        console.log('   ✗ test.html 不存在');
    }
    
    console.log('\n=== 测试完成 ===');
}

test().catch(console.error);
