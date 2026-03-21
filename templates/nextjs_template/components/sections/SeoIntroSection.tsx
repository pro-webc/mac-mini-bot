type Props = {
  title: string;
  lead: string;
};

export default function SeoIntroSection({ title, lead }: Props) {
  return (
    <header className="mb-10 overflow-x-hidden">
      <h1 className="text-center text-2xl font-bold text-white md:text-left md:text-4xl">{title}</h1>
      <p className="mx-auto mt-4 max-w-3xl text-center text-base leading-relaxed text-[#BFDBFE] md:mx-0 md:text-left md:text-lg">
        {lead}
      </p>
    </header>
  );
}
