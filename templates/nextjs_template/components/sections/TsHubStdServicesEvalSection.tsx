import ImagePlaceholder from "@/components/ImagePlaceholder";

export default function TsHubStdServicesEvalSection() {
  return (
    <section
      className="border-b border-[#E2E8F0] bg-[#FAFAF9] py-16 md:py-20"
      aria-labelledby="eval-heading"
    >
      <div className="mx-auto max-w-6xl px-4 md:px-6">
        <h2
          id="eval-heading"
          className="border-b border-[#E2E8F0] pb-4 text-2xl font-semibold text-[#0F172A] md:text-3xl"
        >
          運転評価の見える化（GPSを用いた可視化）
        </h2>
        <div className="mt-10 grid gap-10 md:grid-cols-2 md:items-start">
          <div>
            <p className="max-w-prose text-left text-base leading-[1.7] text-[#0F172A]">
              一般道路コースを想定し、運転の傾向を材料として可視化します。数値は万能ではありませんが、安全会議の議論を具体化する手がかりになります。
            </p>
            <ul className="mt-6 flex flex-col gap-3">
              <li className="border-l-4 border-[#14B8A6] pl-4 text-left text-base text-[#0F172A]">
                評価項目や回数は、対象者・路線・目的に合わせて設計する
              </li>
              <li className="border-l-4 border-[#14B8A6] pl-4 text-left text-base text-[#0F172A]">
                個人情報・プライバシー配慮は、事前説明と運用ルールで明確化する
              </li>
            </ul>
            <p className="mt-6 text-sm text-[#64748B]">
              機材やソフトの名称は公開文案では固定せず、提案時に説明します。
            </p>
          </div>
          <ImagePlaceholder
            aspectClassName="aspect-[4/3]"
            description="サービス説明用：車内ダッシュボードを直接写さず、道路と車線、ミラーの反射など安全運転の「注意力」が伝わる抽象的構図。彩度は抑え、説明文横の余白と調和。"
            overlayText="評価は改善の材料として共有する"
          />
        </div>
      </div>
    </section>
  );
}
