// Local document review tools, loaded only by the MkDocs development lifecycle.
(function () {
    "use strict";

    const contextNode = document.getElementById("review-context");
    const article = document.querySelector(".review-document");
    if (!contextNode || !article) return;
    const context = JSON.parse(contextNode.textContent);
    const storageKey = "nmteam-review-v1:" + context.project;
    const openButton = document.getElementById("review-open");
    const addButton = document.getElementById("review-add");
    const editor = document.getElementById("review-editor");
    const list = document.getElementById("review-list");
    const form = document.getElementById("review-form");
    const input = document.getElementById("review-comment");
    const errorNode = document.getElementById("review-error");
    const status = document.getElementById("review-status");
    const listStatus = document.getElementById("review-list-status");
    const copyButton = document.getElementById("review-copy");
    const clearButton = document.getElementById("review-clear");
    const toast = document.getElementById("review-toast");
    const undoButton = document.getElementById("review-undo");
    let comments = [];
    let candidate = null;
    let selectionRange = null;
    let editorAnchor = null;
    let editing = null;
    let editingId = null;
    let returnToList = false;
    let storageError = null;
    let removedComments = [];
    let noticeTimer = null;

    function validComment(value) {
        if (!value || typeof value !== "object") return false;
        const strings = ["id", "path", "url", "title", "quote", "comment", "createdAt"];
        return strings.every(key => typeof value[key] === "string") &&
            (value.source === null || typeof value.source === "string") &&
            ((value.lineStart === null && value.lineEnd === null) ||
                (Number.isSafeInteger(value.lineStart) && value.lineStart > 0 &&
                 Number.isSafeInteger(value.lineEnd) && value.lineEnd >= value.lineStart));
    }

    function readComments() {
        const saved = [];
        for (let index = 0; index < localStorage.length; index++) {
            const key = localStorage.key(index);
            if (!key || !key.startsWith(storageKey + ":")) continue;
            const data = JSON.parse(localStorage.getItem(key));
            if (!data || data.version !== 1 || !validComment(data.comment) ||
                key !== storageKey + ":" + data.comment.id) {
                throw new Error("Invalid saved review data");
            }
            saved.push(data.comment);
        }
        return saved.sort((first, second) => first.createdAt.localeCompare(second.createdAt) || first.id.localeCompare(second.id));
    }

    function showListError(message) {
        listStatus.textContent = message || "";
        listStatus.hidden = !message;
    }

    function load() {
        try {
            comments = readComments();
            storageError = null;
            status.hidden = true;
            showListError("");
        } catch (error) {
            console.error("Unable to access saved document reviews:", error);
            storageError = "无法读取评论，请检查浏览器存储后刷新。";
            status.textContent = storageError;
            status.hidden = false;
            showListError(storageError);
        }
        render();
    }

    function save(update) {
        if (storageError) throw new Error(storageError);
        const latest = readComments();
        const next = update(latest);
        for (const comment of next) {
            const previous = latest.find(value => value.id === comment.id);
            if (JSON.stringify(previous) !== JSON.stringify(comment)) {
                localStorage.setItem(storageKey + ":" + comment.id, JSON.stringify({ version: 1, comment }));
            }
        }
        for (const comment of latest) {
            if (!next.some(value => value.id === comment.id)) localStorage.removeItem(storageKey + ":" + comment.id);
        }
        comments = readComments();
        render();
    }

    function locationLabel(comment) {
        return comment.path + (comment.lineStart === null
            ? " · 无对应源码行"
            : ":" + comment.lineStart + (comment.lineEnd === comment.lineStart ? "" : "–" + comment.lineEnd));
    }

    function element(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function icon(name) {
        return document.getElementById("review-icon-" + name).content.cloneNode(true);
    }

    function action(label, name, handler) {
        const button = element("button", "review-button review-button--icon");
        button.type = "button";
        button.title = label;
        button.setAttribute("aria-label", label);
        button.append(icon(name));
        button.addEventListener("click", handler);
        return button;
    }

    function notify(message, removed) {
        window.clearTimeout(noticeTimer);
        removedComments = removed || [];
        document.getElementById("review-toast-text").textContent = message;
        undoButton.hidden = removedComments.length === 0;
        toast.hidden = false;
        if (undoButton.hidden) noticeTimer = window.setTimeout(() => { toast.hidden = true; }, 4000);
    }

    function deleteComments(ids) {
        const selected = new Set(ids);
        let removed = [];
        try {
            save(latest => {
                removed = latest.filter(value => selected.has(value.id));
                return latest.filter(value => !selected.has(value.id));
            });
            showListError("");
            if (removed.length) notify(removed.length === 1 ? "评论已删除" : "已清空 " + removed.length + " 条评论", removed);
        } catch (error) {
            console.error("Unable to delete document reviews:", error);
            load();
            showListError("删除失败，请检查浏览器存储后重试。");
        }
    }

    function render() {
        for (const id of ["review-count", "review-panel-count"]) {
            document.getElementById(id).textContent = String(comments.length);
        }
        copyButton.disabled = clearButton.disabled = comments.length === 0 || Boolean(storageError);
        const items = document.getElementById("review-items");
        items.replaceChildren();
        if (comments.length === 0 && !storageError) {
            const empty = element("div", "review-empty");
            empty.append(icon("empty"), element("strong", "", "还没有评论"),
                element("p", "", "选中文档文字，即可添加"));
            items.append(empty);
        }
        comments.forEach(comment => {
            const item = element("section", "review-item");
            const heading = element("div", "review-item-heading");
            const link = element("a", "review-location", locationLabel(comment));
            link.title = locationLabel(comment);
            // Saved storage is untrusted. Navigation stays on this site's origin.
            try {
                const url = new URL(comment.url, location.href);
                if (url.origin === location.origin) link.href = url.href;
            } catch (error) {
                console.warn("Invalid document review URL:", error);
            }
            const actions = element("div", "review-item-actions");
            const editButton = action("编辑评论", "edit", () => {
                openEditor(comment, comment.id, editButton.getBoundingClientRect());
            });
            const deleteButton = action("删除评论", "delete", () => deleteComments([comment.id]));
            deleteButton.classList.add("review-button--danger");
            actions.append(editButton, deleteButton);
            heading.append(link, actions);
            item.append(heading, element("blockquote", "review-quote", comment.quote),
                element("p", "review-comment", comment.comment));
            items.append(item);
        });
    }

    function sourceLocation(start, end, text) {
        // Browser HTML normalization or theme mutations can change Range offsets.
        if (article.textContent !== context.text || context.source === null) return null;
        const matched = [];
        let cursor = start;
        for (const [renderStart, length, lineStart, lineEnd] of context.mappings) {
            const from = Math.max(start, renderStart);
            const to = Math.min(end, renderStart + length);
            if (to <= from) continue;
            if (text.slice(cursor - start, from - start).trim()) return null;
            matched.push([lineStart, lineEnd]);
            cursor = to;
        }
        if (!matched.length || text.slice(cursor - start).trim()) return null;
        const lineStart = Math.min(...matched.map(value => value[0]));
        const lineEnd = Math.max(...matched.map(value => value[1]));
        return { lineStart, lineEnd, source: context.source.split("\n").slice(lineStart - 1, lineEnd).join("\n") };
    }

    function rangeBounds() {
        if (!selectionRange) return null;
        const rectangles = Array.from(selectionRange.getClientRects()).filter(rect => rect.height > 0);
        return rectangles.length ? rectangles[rectangles.length - 1] : selectionRange.getBoundingClientRect();
    }

    function place(surface, anchor, preferAbove) {
        if (!anchor) return;
        const viewport = window.visualViewport;
        const left = (viewport ? viewport.offsetLeft : 0) + 12;
        const top = (viewport ? viewport.offsetTop : 0) + 12;
        const right = left + (viewport ? viewport.width : innerWidth) - 24;
        const bottom = top + (viewport ? viewport.height : innerHeight) - 24;
        surface.style.maxWidth = Math.max(0, right - left) + "px";
        surface.style.maxHeight = Math.max(0, bottom - top) + "px";
        const width = surface.offsetWidth;
        const height = surface.offsetHeight;
        const below = anchor.bottom + 10;
        const above = anchor.top - height - 10;
        let y = below;
        if ((preferAbove && above >= top) || (below + height > bottom && above >= top)) y = above;
        surface.style.left = Math.max(left, Math.min(anchor.left, right - width)) + "px";
        surface.style.top = Math.max(top, Math.min(y, bottom - height)) + "px";
    }

    function captureSelection() {
        if (!editor.hidden) return;
        const selection = window.getSelection();
        candidate = null;
        selectionRange = null;
        addButton.hidden = true;
        if (!selection || selection.rangeCount === 0 || selection.isCollapsed) return;
        const range = selection.getRangeAt(0);
        if (!article.contains(range.startContainer) || !article.contains(range.endContainer)) return;
        const raw = range.toString();
        const quote = raw.trim();
        if (!quote) return;
        const prefix = document.createRange();
        prefix.selectNodeContents(article);
        prefix.setEnd(range.startContainer, range.startOffset);
        const start = prefix.toString().length + raw.length - raw.trimStart().length;
        const source = sourceLocation(start, start + quote.length, quote);
        candidate = {
            path: context.path, url: location.href, title: document.title, quote,
            lineStart: null, lineEnd: null, source: null,
            ...source,
        };
        selectionRange = range.cloneRange();
        addButton.hidden = false;
        place(addButton, rangeBounds(), true);
    }

    function setListOpen(open, focus) {
        list.hidden = !open;
        openButton.setAttribute("aria-expanded", String(open));
        if (focus) (open ? document.getElementById("review-list-close") : openButton).focus({ preventScroll: true });
    }

    function highlightSelection(active) {
        if (window.CSS && CSS.highlights && window.Highlight) {
            if (active && selectionRange) CSS.highlights.set("nmteam-review-selection", new Highlight(selectionRange));
            else CSS.highlights.delete("nmteam-review-selection");
        }
    }

    function openEditor(comment, id, anchor) {
        editing = comment;
        editingId = id || null;
        returnToList = Boolean(id) && !list.hidden;
        editorAnchor = anchor || null;
        setListOpen(false);
        document.getElementById("review-editor-title").textContent = id ? "编辑评论" : "添加评论";
        const location = document.getElementById("review-location");
        location.textContent = location.title = locationLabel(comment);
        document.getElementById("review-quote").textContent = comment.quote;
        input.value = id ? comment.comment : "";
        errorNode.hidden = true;
        addButton.hidden = true;
        editor.hidden = false;
        place(editor, editorAnchor || rangeBounds());
        highlightSelection(!id);
        input.focus({ preventScroll: true });
    }

    function closeEditor(focus) {
        editor.hidden = true;
        highlightSelection(false);
        addButton.hidden = true;
        candidate = null;
        selectionRange = null;
        if (returnToList) setListOpen(true);
        if (focus) (returnToList ? document.getElementById("review-list-close") : openButton).focus({ preventScroll: true });
    }

    // Fence lengths adapt to source and comments containing Markdown code fences.
    function fence(text) {
        const runs = text.match(/`+/g) || [];
        return "`".repeat(Math.max(3, ...runs.map(run => run.length + 1)));
    }

    function block(text, language) {
        const marker = fence(text);
        return marker + language + "\n" + text + "\n" + marker;
    }

    function exportComments() {
        return "请根据以下审阅评论修订文档。行号对应审阅时的源文件，请结合原文定位。\n\n" +
            comments.map((comment, index) => {
                const parts = ["## " + (index + 1) + ". " + comment.path,
                    "文件：" + comment.path,
                    "行号：" + (comment.lineStart === null ? "无对应源码行（生成内容或无法定位）" :
                        comment.lineStart + (comment.lineStart === comment.lineEnd ? "" : "-" + comment.lineEnd)),
                    "页面：" + comment.url, "选中文本：\n" + block(comment.quote, "text")];
                if (comment.source !== null) parts.push("原始 Markdown：\n" + block(comment.source, "markdown"));
                parts.push("评论：\n" + block(comment.comment, "text"));
                return parts.join("\n\n");
            }).join("\n\n");
    }

    async function copy(text) {
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
                return;
            }
        } catch (error) {
            console.warn("Clipboard API failed; trying selection copy:", error);
        }
        const textarea = element("textarea", "review-clipboard");
        textarea.value = text;
        list.append(textarea);
        try {
            textarea.select();
            if (!document.execCommand("copy")) throw new Error("Copy command failed");
        } finally {
            textarea.remove();
            copyButton.focus({ preventScroll: true });
        }
    }

    form.addEventListener("submit", event => {
        event.preventDefault();
        if (!input.value.trim()) {
            errorNode.textContent = "请输入评论内容。";
            errorNode.hidden = false;
            input.focus();
            return;
        }
        try {
            const random = crypto.getRandomValues(new Uint32Array(4));
            const comment = {
                ...editing, id: editingId || Array.from(random, value => value.toString(16).padStart(8, "0")).join(""),
                comment: input.value.trim(), createdAt: editing.createdAt || new Date().toISOString(),
            };
            save(latest => {
                if (!editingId) return [...latest, comment];
                if (!latest.some(value => value.id === editingId)) throw new Error("Review was deleted in another tab");
                return latest.map(value => value.id === editingId ? comment : value);
            });
            closeEditor(true);
            notify("评论已保存");
        } catch (error) {
            console.error("Unable to save document review:", error);
            errorNode.textContent = "保存失败，输入的评论还在。请检查浏览器存储后重试。";
            errorNode.hidden = false;
            place(editor, editorAnchor || rangeBounds());
        }
    });
    input.addEventListener("input", () => { errorNode.hidden = true; });
    input.addEventListener("keydown", event => {
        if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && !event.isComposing) {
            event.preventDefault();
            form.requestSubmit();
        }
    });
    document.getElementById("review-shortcut").textContent = /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘ ↵ 保存" : "Ctrl ↵ 保存";
    addButton.addEventListener("mousedown", event => event.preventDefault());
    addButton.addEventListener("click", () => {
        if (candidate) openEditor(candidate);
    });
    document.getElementById("review-editor-close").addEventListener("click", () => closeEditor(true));
    document.getElementById("review-list-close").addEventListener("click", () => setListOpen(false, true));
    openButton.addEventListener("click", () => {
        if (!editor.hidden) {
            input.focus({ preventScroll: true });
            return;
        }
        load();
        addButton.hidden = true;
        setListOpen(list.hidden, true);
    });
    clearButton.addEventListener("click", () => deleteComments(comments.map(comment => comment.id)));
    undoButton.addEventListener("click", () => {
        try {
            save(latest => [...latest, ...removedComments.filter(comment => !latest.some(value => value.id === comment.id))]);
            notify("评论已恢复");
            showListError("");
        } catch (error) {
            console.error("Unable to restore document reviews:", error);
            showListError("恢复失败，请检查浏览器存储后重试。");
            document.getElementById("review-toast-text").textContent = "恢复失败，请重试";
        }
    });
    document.getElementById("review-toast-close").addEventListener("click", () => {
        toast.hidden = true;
        removedComments = [];
    });
    copyButton.addEventListener("click", async () => {
        try {
            comments = readComments();
            render();
            if (!comments.length) return;
            await copy(exportComments());
            notify("全部评论已复制");
            showListError("");
        } catch (error) {
            console.error("Unable to copy document reviews:", error);
            showListError("复制失败，请检查剪贴板权限和浏览器存储后重试。");
        }
    });
    document.addEventListener("keydown", event => {
        if (event.key !== "Escape") return;
        if (!editor.hidden) {
            event.preventDefault();
            closeEditor(true);
        } else if (!list.hidden) {
            event.preventDefault();
            setListOpen(false, true);
        }
    });
    document.addEventListener("pointerdown", event => {
        if (!editor.hidden && !editor.contains(event.target) && !addButton.contains(event.target)) {
            const changed = input.value.trim() !== (editingId ? editing.comment : "");
            if (!changed) closeEditor(false);
        }
        if (!list.hidden && !list.contains(event.target) && !openButton.contains(event.target) && !toast.contains(event.target)) setListOpen(false);
    });
    document.addEventListener("selectionchange", captureSelection);
    function reposition() {
        addButton.hidden = true;
        if (!editor.hidden) place(editor, editorAnchor || rangeBounds());
    }
    window.addEventListener("scroll", reposition, { passive: true });
    window.addEventListener("resize", reposition);
    if (window.visualViewport) {
        visualViewport.addEventListener("resize", reposition);
        visualViewport.addEventListener("scroll", reposition);
    }
    window.addEventListener("storage", event => {
        if (event.key === null || event.key.startsWith(storageKey + ":")) load();
    });
    load();
})();
