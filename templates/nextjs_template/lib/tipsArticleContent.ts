export type TipsArticleBlock =
  | { type: "h2_bullets"; h2: string; bullets: string[] }
  | { type: "h2_quote"; h2: string; quote: string };

export type TipsArticleContent = {
  h1: string;
  intro: string;
  blocks: TipsArticleBlock[];
  footerH2: string;
  footerBody: string[];
  secondaryCtaLabel: string;
};

export const tipsArticles: Record<string, TipsArticleContent> = {
  "weekly-check-01": {
    h1: "出発前30秒：今日の「見る順番」を固定する",
    intro:
      "ドライバーによって最初に見る場所が違うと、同じ車両でもリスクの取り方がばらつきます。出発前に「今日の順番」を一言で決めるだけで、チーム内の差が縮まります。",
    blocks: [
      {
        type: "h2_bullets",
        h2: "今日から使える合言葉（例）",
        bullets: [
          "死角→ミラー→前方、の順で一度止まって見る",
          "曲がり角手前は速度より「視線の先」を先に決める",
        ],
      },
      {
        type: "h2_quote",
        h2: "朝礼で読み上げる短文（例）",
        quote: "「今日は全員、出発前に死角から。順番は変えません。」",
      },
    ],
    footerH2: "相談につなげる",
    footerBody: [
      "合言葉は作っても定着しないことがあります。教育設計や会議進行を含めて整えたい場合は、相談ください。",
    ],
    secondaryCtaLabel: "お問い合わせへ",
  },
  "handover-one-liner": {
    h1: "配車交代の一言：「道路は変わった」前提で渡す",
    intro:
      "前便の運転感覚をそのまま引きずると、変化した交通状況や荷物の積載状態を見落としやすくなります。引き継ぎは短く、道路環境が新しくなった前提で始めると再現しやすいです。",
    blocks: [
      {
        type: "h2_bullets",
        h2: "現場での使い方（例）",
        bullets: [
          "キー渡しの一言：「道路はこの後の区間で様子が変わります。最初の合流まで速度は抑えめで」",
          "配車表にメモ：「○○交差点手前、歩行者が多い時間帯」など事実だけ一行",
        ],
      },
      {
        type: "h2_quote",
        h2: "朝礼で読み上げる短文（例）",
        quote: "「引き継ぎは結論から。道路は前と同じとは限りません。」",
      },
    ],
    footerH2: "相談につなげる",
    footerBody: [
      "引き継ぎが形骸化している場合は、配車フローと教育設計をあわせて整えると効果が出やすいです。",
    ],
    secondaryCtaLabel: "お問い合わせへ",
  },
  "meeting-starter": {
    h1: "安全会議の冒頭1分：事実→仮説→次の一回",
    intro:
      "ヒヤリ報告が感想で終わると、次の運行に接続されません。短い時間でも、事実・仮説・次の一回の順にそろえると会議の質が安定しやすくなります。",
    blocks: [
      {
        type: "h2_bullets",
        h2: "進行の型（例）",
        bullets: [
          "事実：いつ・どこで・何が起きたか（推測は分ける）",
          "仮説：再発しうる条件は何か（速度・確認順・疲労など）",
          "次の一回：明日の最初の運行で試す具体行動を一つだけ決める",
        ],
      },
      {
        type: "h2_quote",
        h2: "冒頭の合言葉（例）",
        quote: "「今日は事実から。次の一回まで落とします。」",
      },
    ],
    footerH2: "相談につなげる",
    footerBody: [
      "会議の型が定着しない場合は、ファシリテーションと社内ルールのすり合わせから支援できます。",
    ],
    secondaryCtaLabel: "お問い合わせへ",
  },
};

export const tipsArticleSlugs = Object.keys(tipsArticles);
