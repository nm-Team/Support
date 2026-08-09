// Fumadocs-style page actions menu.
(function () {
    "use strict";

    var ENDPOINTS = {
        scira: "https://scira.ai/?q=",
        chatgpt: "https://chatgpt.com/?prompt=",
        claude: "https://claude.ai/new?q=",
        cursor: "https://cursor.com/link/prompt?text=",
    };

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
    }

    function wireMenu(box) {
        var trigger = box.querySelector(".ai-tools__trigger");
        var menu = box.querySelector(".ai-tools__menu");
        var raw = box.getAttribute("data-md-url") || "";
        var markdown = menu.querySelector('[data-ai="markdown"]');
        var prompt = providerPrompt(pageUrl(raw));

        wireMarkdown(markdown, mdUrl(raw));
        ["scira", "chatgpt", "claude", "cursor"].forEach(function (provider) {
            menu.querySelector('[data-ai="' + provider + '"]').href = providerUrl(
                provider,
                prompt
            );
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
