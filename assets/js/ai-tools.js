// Fumadocs-style page actions menu.
(function () {
    "use strict";

    var ENDPOINTS = {
        perplexity: "https://www.perplexity.ai/search?q=",
        grok: "https://grok.com/?q=",
        chatgpt: "https://chatgpt.com/?prompt=",
        claude: "https://claude.ai/new?q=",
        "claude-desktop": "claude://claude.ai/new?q=",
        "claude-code": "https://claude.ai/code/new?q=",
        codex: "codex://new?prompt=",
        cursor: "https://cursor.com/link/prompt?text=",
    };

    var CLAUDE_CODE_REPOSITORY = "nm-Team/Support";
    var CLAUDE_CODE_BRANCH = "main";

    function mdUrl(raw) {
        if (!raw) {
            return "/index.md";
        }
        return "/" + raw.replace(/\/+$/, "") + ".md";
    }

    function pageUrl(raw) {
        return location.origin + "/" + (raw || "");
    }

    function providerPrompt(url) {
        return "Read " + url + ", I want to ask questions about it.";
    }

    function providerUrl(provider, prompt) {
        var url = ENDPOINTS[provider] + encodeURIComponent(prompt);
        if (provider === "chatgpt") {
            return url + "&hints=search";
        }
        if (provider === "claude-code") {
            return (
                url +
                "&repo=" +
                encodeURIComponent(CLAUDE_CODE_REPOSITORY) +
                "&branch=" +
                encodeURIComponent(CLAUDE_CODE_BRANCH)
            );
        }
        return url;
    }

    function setOpen(box, open, restoreFocus) {
        var trigger = box.querySelector(".ai-tools__trigger");
        var menu = box.querySelector(".ai-tools__menu");
        box.classList.toggle("is-open", open);
        trigger.setAttribute("aria-expanded", String(open));
        menu.hidden = !open;
        if (!open && restoreFocus) {
            trigger.focus();
        }
    }

    function showMarkdownUnavailable() {
        window.alert(
            "Markdown 版本在构建产物中提供。请先运行 `uv run nmteam build`，" +
                "或使用其他打开方式。"
        );
    }

    function showCopyFailed() {
        window.alert("无法复制 Markdown，请稍后重试。");
    }

    function copyWithSelection(text) {
        var textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();

        var copied = document.execCommand("copy");
        textarea.remove();
        if (!copied) {
            return Promise.reject(new Error("Copy command failed"));
        }
        return Promise.resolve();
    }

    function copyText(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text).catch(function () {
                return copyWithSelection(text);
            });
        }
        return copyWithSelection(text);
    }

    function setCopyState(button, copied) {
        button.querySelector(".ai-tools__copy-icon--idle").hidden = copied;
        button.querySelector(".ai-tools__copy-icon--success").hidden = !copied;
        button.querySelector(".ai-tools__copy-label").textContent = copied
            ? "已复制"
            : "复制本文 Markdown";
    }

    function wireCopy(button, md, availability) {
        var resetTimer;

        button.addEventListener("click", function () {
            button.disabled = true;
            availability
                .then(function (available) {
                    if (!available) {
                        showMarkdownUnavailable();
                        return null;
                    }
                    return fetch(md);
                })
                .then(function (response) {
                    if (!response) {
                        return null;
                    }
                    var contentType = response.headers.get("Content-Type") || "";
                    if (!response.ok || contentType.indexOf("html") !== -1) {
                        throw new Error("Markdown is unavailable");
                    }
                    return response.text();
                })
                .then(function (markdown) {
                    if (markdown === null) {
                        return;
                    }
                    return copyText(markdown).then(function () {
                        window.clearTimeout(resetTimer);
                        setCopyState(button, true);
                        resetTimer = window.setTimeout(function () {
                            setCopyState(button, false);
                        }, 1800);
                    });
                })
                .catch(showCopyFailed)
                .then(function () {
                    button.disabled = false;
                });
        });
    }

    function wireMarkdown(link, md) {
        var availability = fetch(md, { method: "HEAD" })
            .then(function (response) {
                var contentType = response.headers.get("Content-Type") || "";
                return response.ok && contentType.indexOf("html") === -1;
            })
            .catch(function () {
                return false;
            })
            .then(function (available) {
                link.dataset.rawAvailable = String(available);
                return available;
            });

        link.href = md;
        link.addEventListener("click", function (event) {
            if (link.dataset.rawAvailable === "true") {
                return;
            }

            event.preventDefault();
            if (link.dataset.rawAvailable === "false") {
                showMarkdownUnavailable();
                return;
            }

            var target = window.open("about:blank", "_blank");
            if (target) {
                target.opener = null;
            }
            availability.then(function (available) {
                if (available && target) {
                    target.location.replace(md);
                    return;
                }
                if (target) {
                    target.close();
                }
                showMarkdownUnavailable();
            });
        });

        return availability;
    }

    function wireMenu(box) {
        var trigger = box.querySelector(".ai-tools__trigger");
        var copy = box.querySelector(".ai-tools__copy");
        var menu = box.querySelector(".ai-tools__menu");
        var raw = box.getAttribute("data-md-url") || "";
        var markdown = menu.querySelector('[data-ai="markdown"]');
        var md = mdUrl(raw);
        var prompt = providerPrompt(pageUrl(raw));
        var availability = wireMarkdown(markdown, md);

        wireCopy(copy, md, availability);
        [
            "perplexity",
            "grok",
            "chatgpt",
            "claude",
            "claude-desktop",
            "claude-code",
            "codex",
            "cursor",
        ].forEach(function (provider) {
            menu.querySelector('[data-ai="' + provider + '"]').href =
                providerUrl(provider, prompt);
        });

        trigger.addEventListener("click", function () {
            setOpen(box, menu.hidden, false);
        });

        menu.addEventListener("click", function (event) {
            if (event.target.closest(".ai-tools__item")) {
                setOpen(box, false, false);
            }
        });

        document.addEventListener("click", function (event) {
            if (!menu.hidden && !box.contains(event.target)) {
                setOpen(box, false, false);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && !menu.hidden) {
                event.preventDefault();
                setOpen(box, false, true);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".ai-tools").forEach(wireMenu);
    });
})();
