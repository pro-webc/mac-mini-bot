import Link from "next/link";
import { Globe, MapPin, MonitorSmartphone } from "lucide-react";

export default function ServiceAreasSection() {
  return (
    <section className="px-0 py-12 md:py-16" aria-labelledby="area-heading">
      <div className="mx-auto max-w-6xl">
        <h2
          id="area-heading"
          className="text-2xl font-bold tracking-tight text-white md:text-3xl"
        >
          対応エリアとハイブリッドな進行
        </h2>
        <p className="mt-4 max-w-3xl text-left text-base leading-relaxed text-[#BFDBFE]">
          全国対応を想定しています。オンラインでの打合せ・進捗共有と現場工事を組み合わせ、遠方案件でも認識合わせが途切れないよう支援します。対応エリアを地図画像やイラストで示すことはせず、例外条件はお問い合わせで個別に確認してください。
        </p>
        <ul className="mt-8 grid gap-4 md:grid-cols-3">
          <li className="flex items-start gap-3 rounded-[12px] border border-white/20 bg-[#1d4ed8] p-5">
            <Globe className="mt-1 h-6 w-6 shrink-0 text-[#caeb25]" aria-hidden />
            <div>
              <p className="text-base font-semibold text-white">全国対応</p>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">
                案件の前提に応じて移動・宿泊が伴う場合があります。詳細は相談時にご説明します。
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3 rounded-[12px] border border-white/20 bg-[#1d4ed8] p-5">
            <MonitorSmartphone className="mt-1 h-6 w-6 shrink-0 text-[#caeb25]" aria-hidden />
            <div>
              <p className="text-base font-semibold text-white">オンライン打合せ・共有</p>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">
                Web会議や書面での進捗共有に対応します。利用ツールは案件に合わせて調整します。
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3 rounded-[12px] border border-white/20 bg-[#1d4ed8] p-5">
            <MapPin className="mt-1 h-6 w-6 shrink-0 text-[#caeb25]" aria-hidden />
            <div>
              <p className="text-base font-semibold text-white">本社所在地</p>
              <p className="mt-2 text-left text-sm leading-relaxed text-[#E0E7FF]">
                大阪市阿倍野区三明町2丁目16-5。地図は{" "}
                <Link
                  href="/company"
                  className="font-medium text-[#caeb25] underline-offset-2 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#caeb25]"
                >
                  会社情報のアクセス
                </Link>
                をご確認ください。
              </p>
            </div>
          </li>
        </ul>
      </div>
    </section>
  );
}
