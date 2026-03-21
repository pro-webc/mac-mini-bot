import { ListChecks } from "lucide-react";

export default function TshHomeSolutionFrameworkSection() {
  const bullets = [
    "ワーク中心：短時間でも「話す→気づく→決める」まで持っていく",
    "評価は自己理解のための地図。過大な数値目標は置かない",
    "実施後は、日常に戻したときの小さな行動まで分解",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="solution-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="solution-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          「腹落ち」と「可視化」で、次の運転行動に落とす
        </h2>
        <p className="mt-4 max-w-prose text-left text-base leading-[1.7] text-[#1c1917]">
          TS-hubの支援は、ティーチング偏重に寄りすぎない進行を意識します。参加者が具体例を持ち寄り、安全行動を言葉にすることで相互学習が起きやすくなります。併せて、一般道路のコースを自社車で走行し、GPS等を用いた評価指標を材料に強み弱みを整理します。医療・法律の判断や、違反取締りの代替にはなりません。
        </p>
        <ul className="mt-8 flex flex-col gap-4">
          {bullets.map((t) => (
            <li
              key={t}
              className="flex gap-3 rounded-none border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              <ListChecks
                className="mt-0.5 h-6 w-6 shrink-0 text-[#0f766e]"
                aria-hidden
              />
              <span>{t}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
