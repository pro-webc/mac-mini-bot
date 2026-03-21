export default function TshProgramAudiencesSection() {
  const bullets = [
    "安全運転管理者・運行管理担当（社内ルールの実装責任者）",
    "業務ドライバー（営業・サービス・監督職の運転を含む）",
    "部門横断のキーパーソン（現場と管理の接点）",
  ];

  return (
    <section
      className="border-b border-[#e7e5e4] bg-[#f5f5f4]"
      aria-labelledby="prog-aud-heading"
    >
      <div className="mx-auto max-w-6xl px-4 py-16 md:px-6">
        <h2
          id="prog-aud-heading"
          className="text-2xl font-bold text-[#1c1917] md:text-3xl"
        >
          対象例
        </h2>
        <ul className="mt-8 flex flex-col gap-3">
          {bullets.map((t) => (
            <li
              key={t}
              className="border border-[#e7e5e4] bg-[#ffffff] p-4 text-left text-base leading-[1.7] text-[#1c1917]"
            >
              {t}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
