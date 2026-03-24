"""google.generativeai の unary ``generate_content`` に RPC タイムアウトと再試行を付与する。

``google.ai.generativelanguage`` の既定タイムアウト（約 60s）では、
手順7 相当の長大なコード生成で ``DeadlineExceeded`` になりやすい。
``GenerativeModel.generate_content`` を差し替え、gapic の ``timeout=`` を明示する。
"""
from __future__ import annotations

import logging
import time
from typing import Any

from google.api_core import exceptions as gexc
from google.generativeai import client as genai_client
from google.generativeai import generative_models as gm
from google.generativeai.types import generation_types

logger = logging.getLogger(__name__)

_orig_generate: Any = None
_installed = False


def install_generative_model_rpc_timeout(
    *,
    timeout_sec: float,
    deadline_retries: int,
) -> None:
    """
    プロセス内で1回だけ ``GenerativeModel.generate_content`` をラップする。

    ``stream=True`` のときは元実装のまま（タイムアウト拡張は unary のみ）。
    """
    global _orig_generate, _installed
    if _installed:
        return
    _orig_generate = gm.GenerativeModel.generate_content

    def generate_content(
        self: Any,
        contents: Any,
        *,
        generation_config: Any = None,
        safety_settings: Any = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        if stream:
            return _orig_generate(
                self,
                contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True,
                **kwargs,
            )
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            **kwargs,
        )
        if self._client is None:
            self._client = genai_client.get_default_generative_client()
        attempts = 1 + max(0, int(deadline_retries))
        last_exc: BaseException | None = None
        for attempt in range(attempts):
            try:
                raw = self._client.generate_content(request, timeout=float(timeout_sec))
                return generation_types.GenerateContentResponse.from_response(raw)
            except gexc.DeadlineExceeded as e:
                last_exc = e
                if attempt + 1 >= attempts:
                    raise
                delay = min(120.0, 5.0 * (2**attempt))
                logger.warning(
                    "Gemini RPC タイムアウトのため再試行 (%s/%s) 待機 %.1fs: %s",
                    attempt + 1,
                    attempts,
                    delay,
                    e,
                )
                time.sleep(delay)
        assert last_exc is not None
        raise last_exc

    gm.GenerativeModel.generate_content = generate_content  # type: ignore[method-assign]
    _installed = True
    logger.info(
        "Gemini unary RPC: timeout=%ss, DeadlineExceeded 再試行=%s 回を適用",
        timeout_sec,
        deadline_retries,
    )


def ensure_gemini_rpc_patch_from_config() -> None:
    """config の ``GEMINI_RPC_*`` に従いパッチを適用（冪等）。"""
    from config.config import GEMINI_RPC_DEADLINE_RETRIES, GEMINI_RPC_TIMEOUT_SEC

    install_generative_model_rpc_timeout(
        timeout_sec=float(GEMINI_RPC_TIMEOUT_SEC),
        deadline_retries=int(GEMINI_RPC_DEADLINE_RETRIES),
    )
    # タイムアウトラッパーの外側に連鎖（案件トレース有効時のみ output/<record>/llm_steps/ へ保存）
    from modules.llm.llm_step_trace import install_generative_model_trace_wrap

    install_generative_model_trace_wrap()
