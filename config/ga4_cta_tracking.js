/**
 * GA4 CTA トラッキング（自動検出・グローバルリスナー方式）
 *
 * コンポーネント側の変更は不要。ランタイムでリンク先URL・テキスト・class・DOM祖先を
 * 走査してCTA種別と配置位置を自動判定し、GA4 イベントを発火する。
 *
 * 注入: modules/ga4_injector.py が app/layout.tsx の <Script> で読み込む。
 * プレースホルダ __GA4_MEASUREMENT_ID__ は注入時に実IDへ置換される。
 */
(function () {
  "use strict";

  var MID = "__GA4_MEASUREMENT_ID__";

  // --- gtag 初期化 ---
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", MID);

  // --- 定数 ---
  var EXCLUDED_SNS =
    /instagram\.com|youtube\.com|youtu\.be|twitter\.com|x\.com|facebook\.com|fb\.com|tiktok\.com/i;

  // --- CTA 種別判定（URL） ---
  function ctaTypeFromUrl(url) {
    if (!url) return null;
    if (/^tel:/i.test(url)) return "tel";
    if (/^mailto:/i.test(url)) return "mail";
    if (/line\.me|lin\.ee/i.test(url)) return "line";
    try {
      var parsed = new URL(url, location.origin);
      if (parsed.hostname === location.hostname) return null;
    } catch (_) {
      /* data: / javascript: 等は外部扱いしない */
      if (!/^https?:/i.test(url)) return null;
    }
    if (EXCLUDED_SNS.test(url)) return null;
    return "external";
  }

  // --- CTA 種別判定（非リンク要素のテキスト・class・id） ---
  var LINE_TEXT = /\bline\b|ライン|ＬＩＮ[ＥE]/i;
  var LINE_ATTR = /line[-_]?(btn|cta|link|button|add|friend)/i;
  var TEL_TEXT = /電話|お電話|tel(?:ephone)?|call/i;
  var TEL_NOISE = /hotel|hostel|intel|telemetry/i;
  var MAIL_TEXT = /メール|e?-?mail|お問い合わせメール/i;

  function ctaTypeFromElement(el) {
    var text = (el.textContent || "").trim();
    var cls = (el.className || "").toString();
    var id = el.id || "";
    if (LINE_TEXT.test(text) || LINE_ATTR.test(cls) || LINE_ATTR.test(id))
      return "line";
    if (TEL_TEXT.test(text) && !TEL_NOISE.test(text)) return "tel";
    if (MAIL_TEXT.test(text)) return "mail";
    return null;
  }

  // --- 配置位置の自動判定（DOM 祖先走査） ---
  function detectPosition(el) {
    var node = el;
    while (node && node !== document.body) {
      var tag = (node.tagName || "").toLowerCase();
      var cls = (node.className || "").toString().toLowerCase();
      var nid = (node.id || "").toLowerCase();
      if (tag === "header" || /\bheader\b/.test(cls) || /\bheader\b/.test(nid))
        return "header";
      if (tag === "nav" || /\bnav(bar|igation)?\b/.test(cls) || /\bnav\b/.test(nid))
        return "nav";
      if (/\bhero\b/.test(cls) || /\bhero\b/.test(nid)) return "hero";
      if (tag === "footer" || /\bfooter\b/.test(cls) || /\bfooter\b/.test(nid))
        return "footer";
      if (
        tag === "aside" ||
        /\bsidebar\b/.test(cls) ||
        /\bsidebar\b/.test(nid)
      )
        return "sidebar";
      if (
        tag === "main" ||
        /\bmain[-_]?content\b/.test(cls) ||
        /\bmain\b/.test(nid)
      )
        return "main";
      node = node.parentElement;
    }
    return "other";
  }

  // --- ナビゲーション開閉ボタンの除外 ---
  function isNavToggle(el) {
    var cls = (el.className || "").toString().toLowerCase();
    var ariaExpanded = el.getAttribute("aria-expanded");
    var ariaControls = (el.getAttribute("aria-controls") || "").toLowerCase();
    var ariaLabel = (el.getAttribute("aria-label") || "").toLowerCase();
    var text = (el.textContent || "").trim();
    if (
      ariaExpanded !== null &&
      /nav|menu|drawer|sidebar/i.test(ariaControls + " " + ariaLabel + " " + cls)
    )
      return true;
    if (/hamburger|menu[-_]?toggle|nav[-_]?toggle|drawer[-_]?toggle/i.test(cls))
      return true;
    if (/^(メニュー|menu|☰|✕|✖|×)$/i.test(text)) return true;
    return false;
  }

  // ------------------------------------------------------------------
  // 1. CTA クリック — グローバルリスナー
  // ------------------------------------------------------------------
  document.addEventListener(
    "click",
    function (e) {
      if (typeof gtag !== "function") return;

      var target = e.target;
      var link = target.closest ? target.closest("a[href]") : null;
      var ctaType = null;
      var linkUrl = "";
      var ctaEl = null;

      if (link) {
        var href = link.getAttribute("href") || "";
        ctaType = ctaTypeFromUrl(href);
        linkUrl = href;
        ctaEl = link;
      }

      if (!ctaType) {
        var clickable = target.closest
          ? target.closest('button, [role="button"], [onclick], div[class*="btn"], div[class*="cta"]')
          : target;
        if (!clickable) clickable = target;
        if (clickable.tagName && /^(button|div|span)$/i.test(clickable.tagName) && isNavToggle(clickable))
          return;
        ctaType = ctaTypeFromElement(clickable);
        if (ctaType) {
          ctaEl = clickable;
          linkUrl = (clickable.textContent || "").trim().substring(0, 100);
        }
      }

      if (!ctaType || !ctaEl) return;

      var position = detectPosition(ctaEl);
      var eventName = "cta_" + ctaType + "_" + position;

      gtag("event", eventName, {
        cta_type: ctaType,
        cta_position: position,
        link_url: linkUrl,
      });
    },
    true
  );

  // ------------------------------------------------------------------
  // 2. お問い合わせフォーム送信 — submit イベント
  // ------------------------------------------------------------------
  var CONTACT_KW =
    /contact|お問い合わせ|問い合わせ|問合せ|相談|consultation|inquiry|ご相談/i;

  function isContactForm(form) {
    var action = form.getAttribute("action") || "";
    var id = form.id || "";
    var cls = (form.className || "").toString();
    var text = (form.textContent || "").substring(0, 2000);
    return (
      CONTACT_KW.test(action) ||
      CONTACT_KW.test(id) ||
      CONTACT_KW.test(cls) ||
      CONTACT_KW.test(text)
    );
  }

  document.addEventListener(
    "submit",
    function (e) {
      if (typeof gtag !== "function") return;
      var form = e.target;
      if (!form || (form.tagName || "").toLowerCase() !== "form") return;
      if (!isContactForm(form)) return;

      var position = detectPosition(form);
      gtag("event", "form_submit_contact_" + position, {
        form_id: form.id || form.getAttribute("name") || "unknown",
      });
    },
    true
  );

  // ------------------------------------------------------------------
  // 3. フォーム外の非同期送信ボタン
  // ------------------------------------------------------------------
  var SUBMIT_KW = /送信|submit|お問い合わせ|問い合わせ|相談|申し込み|申込/i;

  document.addEventListener(
    "click",
    function (e) {
      if (typeof gtag !== "function") return;
      var btn = e.target.closest
        ? e.target.closest('button[type="submit"], input[type="submit"]')
        : null;
      if (!btn) return;
      if (btn.closest && btn.closest("form")) return;

      var text = (btn.textContent || btn.value || "").trim();
      if (!SUBMIT_KW.test(text)) return;

      var position = detectPosition(btn);
      gtag("event", "form_submit_contact_" + position, {
        form_id: btn.id || btn.getAttribute("name") || "async_button",
      });
    },
    true
  );
})();
