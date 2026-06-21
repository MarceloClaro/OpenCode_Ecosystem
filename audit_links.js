const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const dir = path.join(__dirname, 'livro-opencode', 'capitulos');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.tex'));
// Regex to capture URLs more accurately in LaTeX files
const urlRegex = /https?:\/\/[^\s}\\\"]+/g;

const urls = new Set();

files.forEach(f => {
    const content = fs.readFileSync(path.join(dir, f), 'utf8');
    let match;
    while ((match = urlRegex.exec(content)) !== null) {
        let url = match[0].replace(/\\/g, '').replace(/["',.\\]+$/, '');
        urls.add(url);
    }
});

// Also check livro.tex and livro-dark.tex
const baseFiles = ['livro.tex', 'livro-dark.tex'];
baseFiles.forEach(f => {
    try {
        const content = fs.readFileSync(path.join(__dirname, 'livro-opencode', f), 'utf8');
        let match;
        while ((match = urlRegex.exec(content)) !== null) {
            let url = match[0].replace(/\\/g, '').replace(/["',.\\]+$/, '');
            urls.add(url);
        }
    } catch(e) {}
});

console.log(`Found ${urls.size} unique URLs.`);

const checkUrl = (url) => new Promise(resolve => {
    if(url.includes('localhost') || url.includes('127.0.0.1')) {
        return resolve({url, status: 'LOCAL'});
    }
    
    let parsed;
    try {
        parsed = new URL(url);
    } catch(e) {
        return resolve({url, status: 'INVALID'});
    }

    const lib = url.startsWith('https') ? https : http;
    const req = lib.request(url, { method: 'HEAD', headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
        if (res.statusCode >= 400 || res.statusCode === 405) {
            lib.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res2 => {
                resolve({url, status: res2.statusCode});
            }).on('error', err => resolve({url, status: 'ERROR'}));
        } else {
            resolve({url, status: res.statusCode});
        }
    }).on('error', err => {
        lib.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res2 => {
            resolve({url, status: res2.statusCode});
        }).on('error', err2 => resolve({url, status: 'ERROR'}));
    });
    
    req.setTimeout(10000, () => {
        req.destroy();
        resolve({url, status: 'TIMEOUT'});
    });
    req.end();
});

Promise.all(Array.from(urls).map(checkUrl)).then(results => {
    // 200 OK, 301/302 Redirects, 308 Perm Redirect, 403 Forbidden (some bot checks)
    const broken = results.filter(r => r.status !== 200 && r.status !== 301 && r.status !== 302 && r.status !== 308 && r.status !== 403 && r.status !== 'LOCAL');
    
    if (broken.length === 0) {
        console.log('All external links are active.');
    } else {
        console.log('\n--- BROKEN OR SUSPICIOUS LINKS ---');
        broken.forEach(b => console.log(`Status [${b.status}]: ${b.url}`));
    }
});
