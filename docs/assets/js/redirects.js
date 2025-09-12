// 简单的客户端重定向脚本
(function () {
    // 重定向映射
    const redirects = {
        '/nmbot-telegram/about-panel/': '/nmbot-telegram/panel/',
    };

    // 获取当前路径
    const currentPath = window.location.pathname;

    // 检查是否需要重定向
    for (const oldPath in redirects) {
        if (currentPath === oldPath || currentPath.startsWith(oldPath)) {
            const newPath = redirects[oldPath];
            // 执行重定向
            window.location.replace(newPath);
            break;
        }
    }
})();
