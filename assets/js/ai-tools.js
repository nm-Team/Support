// AI tools: view-as-Markdown, open in ChatGPT / Claude.
// The page's raw Markdown twin lives at the same docs-relative path with a
// ".md" suffix (e.g. /nmbot-telegram/mcp.md); it is staged into site/ by the
// build. When the twin is missing (e.g. `mkdocs serve`), ChatGPT/Claude fall
// back to a prompt that references the page URL instead of its content.
(function () {
    "use strict";

    var ENDPOINTS = {
        chatgpt: "https://chatgpt.com/?q=",
        claude: "https://claude.ai/new?q=",
    };
    // Keep the prompt URL short enough for chat providers to accept.
    var MAX_PROMPT = 60000;

    function mdUrl(raw) {
        // Root-relative: a relative path would resolve against the page URL,
        // e.g. /nmbot-telegram/mcp/ + "nmbot-telegram/mcp.md" -> wrong twin.
        // The home page has an empty page.url and its twin is /index.md
        // (already carries the ".md" suffix).
        if (!raw) {
            return "/index.md";
        }
        return "/" + raw.replace(/\/+$/, "") + ".md";
    }

    function pageUrl(raw) {
        return location.origin + "/" + (raw || "");
    }

    function buildPrompt(content, url) {
        if (!content) {
            return "请阅读此文档页面并回答我的问题：" + url;
        }
        var header = "以下是 support.nmteam.xyz 文档页面的内容，请基于此内容回答我的问题：\n\n";
        var body = content;
        if (body.length > MAX_PROMPT) {
            body = body.slice(0, MAX_PROMPT) + "\n\n…（内容过长已截断）";
        }
        return header + body;
    }

    function openAi(which, prompt) {
        window.open(ENDPOINTS[which] + encodeURIComponent(prompt), "_blank", "noopener");
    }

    function wireFetch(button, which, md, url) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            fetch(md)
                .then(function (response) {
                    return response.ok ? response.text() : "";
                })
                .catch(function () {
                    return "";
                })
                .then(function (content) {
                    openAi(which, buildPrompt(content, url));
                });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        var box = document.querySelector(".ai-tools");
        if (!box) {
            return;
        }
        var raw = box.getAttribute("data-md-url") || "";
        var md = mdUrl(raw);
        var url = pageUrl(raw);

        var markdownLink = box.querySelector('[data-ai="markdown"]');
        if (markdownLink) {
            markdownLink.setAttribute("href", md);
        }
        var chatgpt = box.querySelector('[data-ai="chatgpt"]');
        if (chatgpt) {
            wireFetch(chatgpt, "chatgpt", md, url);
        }
        var claude = box.querySelector('[data-ai="claude"]');
        if (claude) {
            wireFetch(claude, "claude", md, url);
        }
    });
})();
