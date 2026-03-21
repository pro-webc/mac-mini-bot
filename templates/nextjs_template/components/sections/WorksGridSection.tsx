"use client";

import { useCallback, useEffect, useId, useState } from "react";
import { X } from "lucide-react";
import ImagePlaceholder from "@/components/ImagePlaceholder";

type WorkItem = {
  id: string;
  title: string;
  summary: string;
  detail: string;
  shotNote: string;
  overlay: string;
};

const works: WorkItem[] = [
  {
    id: "w1",
    title: "基地局周辺の設置工事（仮題）",
    summary: "アンテナ・レック周辺の設置と配線整理。安全区域の設定まで。",
    detail:
      "詳細な工程表・使用機材・工期は確定稿で追記します。ここではモーダル内に補足テキストと追加カットの意図を載せる想定です。",
    shotNote:
      "基地局設備が主体で写る広角。企業ロゴ・個人が特定される情報は避ける。",
    overlay: "屋外基地局イメージ（差し替え）",
  },
  {
    id: "w2",
    title: "レーン系通信設備の接続（仮題）",
    summary: "新設ラインの接続試験とラベル付け。夜間作業の可能性あり。",
    detail:
      "掲載可否とモザイク範囲は発注者確認後に確定。本文は1段落＋箇条書きを想定。",
    shotNote: "レーン横の機器盤が分かるアングル。車両ナンバーは不可。",
    overlay: "レーン設備イメージ（差し替え）",
  },
  {
    id: "w3",
    title: "既設ラックの整備（仮題）",
    summary: "配線の見直しと不良コネクタ交換。稼働中設備への注意。",
    detail: "作業前後の写真セットで掲載する想定。注意事項は別枠で記載。",
    shotNote: "ラック内が整列して見える構図。ケーブル色分けルールを反映。",
    overlay: "ラック内Before/After想定",
  },
];

export default function WorksGridSection() {
  const [openId, setOpenId] = useState<string | null>(null);
  const titleId = useId();
  const openItem = works.find((w) => w.id === openId) ?? null;

  const close = useCallback(() => setOpenId(null), []);

  useEffect(() => {
    if (!openId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [openId, close]);

  return (
    <section
      className="overflow-x-hidden rounded-[12px] border border-white/15 bg-white p-6 md:p-10"
      aria-labelledby="works-grid-heading"
    >
      <h2
        id="works-grid-heading"
        className="text-xl font-bold text-[#0F172A] md:text-2xl"
      >
        事例カード一覧
      </h2>
      <p className="mt-3 text-left text-sm leading-relaxed text-[#475569]">
        カードを押すと詳細が開きます。6ページ構成のため事例専用ルートは設けていません。
      </p>
      <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {works.map((w) => (
          <li key={w.id}>
            <button
              type="button"
              className="flex w-full flex-col overflow-hidden rounded-[12px] border border-[#E2E8F0] bg-[#F8FAFC] text-left transition-colors hover:border-[#2563eb] hover:bg-[#EFF6FF] active:bg-[#DBEAFE] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
              onClick={() => setOpenId(w.id)}
            >
              <ImagePlaceholder
                aspectClassName="aspect-[4/3] object-cover"
                description={w.shotNote}
                overlayText={w.overlay}
              />
              <div className="flex flex-col gap-2 p-4">
                <h3 className="text-base font-bold text-[#0F172A]">{w.title}</h3>
                <p className="text-sm leading-relaxed text-[#475569]">{w.summary}</p>
                <span className="text-xs font-semibold text-[#2563eb]">詳細を見る</span>
              </div>
            </button>
          </li>
        ))}
      </ul>

      {openItem ? (
        <div
          className="fixed inset-0 z-[100] flex items-end justify-center bg-black/50 p-4 sm:items-center"
          role="presentation"
          onClick={close}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-[12px] border border-[#E2E8F0] bg-[#FFFFFF] p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <h2 id={titleId} className="text-lg font-bold text-[#0F172A]">
                {openItem.title}
              </h2>
              <button
                type="button"
                className="inline-flex min-h-[44px] min-w-[44px] shrink-0 items-center justify-center rounded-[10px] border border-[#E2E8F0] bg-[#F8FAFC] text-[#0F172A] hover:bg-[#E2E8F0] active:bg-[#CBD5E1] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                aria-label="閉じる"
                onClick={close}
              >
                <X className="h-5 w-5" aria-hidden />
              </button>
            </div>
            <p className="mt-4 text-left text-sm leading-relaxed text-[#475569]">
              {openItem.detail}
            </p>
            <div className="mt-4">
              <ImagePlaceholder
                aspectClassName="aspect-video"
                description={`詳細モーダル用の追加カット：${openItem.shotNote}`}
                overlayText="ライトボックス内プレビュー枠"
              />
            </div>
            <button
              type="button"
              className="mt-6 inline-flex min-h-[48px] w-full items-center justify-center rounded-[14px] border-2 border-[#2563eb] bg-[#FFFFFF] px-4 py-3 text-sm font-semibold text-[#2563eb] hover:bg-[#EFF6FF] active:bg-[#DBEAFE] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
              onClick={close}
            >
              閉じる
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
